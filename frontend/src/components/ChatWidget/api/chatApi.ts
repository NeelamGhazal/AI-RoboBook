/**
 * API client for RAG Chatbot backend
 *
 * Handles all HTTP communication with streaming support
 */

import type {
  ChatRequest,
  ChatResponse,
  SessionResponse,
  MessageHistoryResponse,
  StreamEvent,
  Citation,
} from '../types';
import { defaultConfig, API_ENDPOINTS, WIDGET_CONSTANTS, ERROR_MESSAGES } from '../config';

const { apiUrl } = defaultConfig;
const { STREAM_TIMEOUT_MS, RETRY_ATTEMPTS, RETRY_DELAY_MS } = WIDGET_CONSTANTS;

/**
 * Custom error class for API errors
 */
export class ChatApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public userMessage?: string
  ) {
    super(message);
    this.name = 'ChatApiError';
  }
}

/**
 * Exponential backoff retry utility
 */
async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  attempts: number = RETRY_ATTEMPTS
): Promise<T> {
  for (let i = 0; i < attempts; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === attempts - 1) throw error;

      const delay = RETRY_DELAY_MS * Math.pow(2, i);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  throw new Error('Retry attempts exhausted');
}

/**
 * Create a new chat session
 */
export async function createSession(): Promise<string> {
  try {
    console.log('[ChatApi] Creating session at:', `${apiUrl}${API_ENDPOINTS.createSession}`);

    const response = await retryWithBackoff(async () => {
      const res = await fetch(`${apiUrl}${API_ENDPOINTS.createSession}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!res.ok) {
        console.error('[ChatApi] Session creation failed:', res.status, res.statusText);
        throw new ChatApiError(
          `Failed to create session: ${res.statusText}`,
          res.status,
          ERROR_MESSAGES.SESSION_ERROR
        );
      }

      return res;
    });

    const data: SessionResponse = await response.json();
    console.log('[ChatApi] Session created successfully:', data.session_id);
    return data.session_id;
  } catch (error) {
    console.error('[ChatApi] Session creation failed:', error);
    throw error instanceof ChatApiError ? error : new ChatApiError(
      'Failed to create session',
      undefined,
      ERROR_MESSAGES.SESSION_ERROR
    );
  }
}

/**
 * Send chat message (non-streaming)
 */
export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  try {
    const response = await retryWithBackoff(async () => {
      const res = await fetch(`${apiUrl}${API_ENDPOINTS.chat}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!res.ok) {
        throw new ChatApiError(
          `Chat request failed: ${res.statusText}`,
          res.status,
          ERROR_MESSAGES.UNKNOWN_ERROR
        );
      }

      return res;
    });

    return await response.json();
  } catch (error) {
    console.error('[ChatApi] Chat request failed:', error);
    throw error instanceof ChatApiError ? error : new ChatApiError(
      'Failed to send message',
      undefined,
      ERROR_MESSAGES.NETWORK_ERROR
    );
  }
}

/**
 * Send chat message with streaming response
 *
 * @param request Chat request payload
 * @param onEvent Callback for each streaming event
 * @returns AbortController to cancel the stream
 */
export async function sendMessageStream(
  request: ChatRequest,
  onEvent: (event: StreamEvent) => void
): Promise<AbortController> {
  const abortController = new AbortController();

  try {
    const url = `${apiUrl}${API_ENDPOINTS.chatStream}`;
    console.log('[ChatApi] Starting stream request to:', url);
    console.log('[ChatApi] Request payload:', {
      session_id: request.session_id,
      question_length: request.question.length,
      has_selected_text: !!request.selected_text,
      selected_text_length: request.selected_text ? request.selected_text.length : 0,
    });

    if (request.selected_text) {
      console.log('[ChatApi] ✓ Selected text mode enabled');
      console.log('[ChatApi] Selected text preview:', request.selected_text.substring(0, 100) + '...');
    } else {
      console.log('[ChatApi] ℹ️ General query mode (no selected text)');
    }

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
      signal: abortController.signal,
    });

    console.log('[ChatApi] Stream response status:', response.status, response.statusText);

    if (!response.ok) {
      console.error('[ChatApi] Stream request failed:', response.status, response.statusText);
      throw new ChatApiError(
        `Stream request failed: ${response.statusText}`,
        response.status,
        ERROR_MESSAGES.UNKNOWN_ERROR
      );
    }

    if (!response.body) {
      console.error('[ChatApi] Response body is null');
      throw new ChatApiError(
        'Response body is null',
        undefined,
        ERROR_MESSAGES.UNKNOWN_ERROR
      );
    }

    console.log('[ChatApi] Stream started successfully');

    // Set up timeout
    const timeoutId = setTimeout(() => {
      console.warn('[ChatApi] Stream timeout after', STREAM_TIMEOUT_MS, 'ms');
      abortController.abort();
      onEvent({
        type: 'error',
        error: ERROR_MESSAGES.TIMEOUT_ERROR,
      });
    }, STREAM_TIMEOUT_MS);

    // Read streaming response
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let chunkCount = 0;

    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        console.log('[ChatApi] Stream completed, total chunks:', chunkCount);
        clearTimeout(timeoutId);
        break;
      }

      chunkCount++;

      // Decode chunk and add to buffer
      buffer += decoder.decode(value, { stream: true });

      // Process complete SSE messages (lines starting with "data: ")
      const lines = buffer.split('\n');
      buffer = lines.pop() || ''; // Keep incomplete line in buffer

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const eventData = line.slice(6); // Remove "data: " prefix

            // Debug: Log raw event data
            if (chunkCount === 1) {
              console.log('[ChatApi] First raw event data:', eventData);
            }

            const event: StreamEvent = JSON.parse(eventData);

            // Enhanced logging with actual content
            if (event.type === 'token') {
              // Log first few tokens and every 10th
              if (chunkCount <= 3 || chunkCount % 10 === 0) {
                console.log(`[ChatApi] Token #${chunkCount}:`, event.content);
              }
            } else {
              console.log('[ChatApi] Stream event:', event.type, event);
            }

            // Call event handler
            onEvent(event);

            // Cancel stream on 'done' or 'error' events
            if (event.type === 'done' || event.type === 'error') {
              console.log('[ChatApi] Stream ending, event type:', event.type);
              clearTimeout(timeoutId);
              reader.cancel();
              return abortController;
            }
          } catch (e) {
            console.error('[ChatApi] Failed to parse SSE event:', line, e);
            console.error('[ChatApi] Raw line that failed:', line);
          }
        } else if (line.trim()) {
          // Log non-data lines
          console.log('[ChatApi] Non-data line:', line);
        }
      }
    }
  } catch (error) {
    if (error.name === 'AbortError') {
      console.log('[ChatApi] Stream aborted by user or timeout');
    } else {
      console.error('[ChatApi] Stream error:', error);
      onEvent({
        type: 'error',
        error: error instanceof ChatApiError ? error.userMessage : ERROR_MESSAGES.NETWORK_ERROR,
      });
    }
  }

  return abortController;
}

/**
 * Fetch conversation history for a session
 */
export async function fetchHistory(sessionId: string): Promise<MessageHistoryResponse> {
  try {
    const response = await retryWithBackoff(async () => {
      const res = await fetch(`${apiUrl}${API_ENDPOINTS.chatHistory(sessionId)}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!res.ok) {
        throw new ChatApiError(
          `Failed to fetch history: ${res.statusText}`,
          res.status,
          ERROR_MESSAGES.UNKNOWN_ERROR
        );
      }

      return res;
    });

    return await response.json();
  } catch (error) {
    console.error('[ChatApi] History fetch failed:', error);
    throw error instanceof ChatApiError ? error : new ChatApiError(
      'Failed to fetch history',
      undefined,
      ERROR_MESSAGES.NETWORK_ERROR
    );
  }
}
