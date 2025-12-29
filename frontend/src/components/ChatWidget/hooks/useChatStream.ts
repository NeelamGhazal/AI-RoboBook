/**
 * Chat Streaming Hook
 *
 * Manages streaming chat responses from the backend API.
 */

import { useCallback, useRef } from 'react';
import { useChatWidget } from '../context/ChatWidgetContext';
import { sendMessageStream, ChatApiError } from '../api/chatApi';
import type { StreamEvent, Message, Citation } from '../types';

export function useChatStream() {
  const {
    sessionId,
    addMessage,
    updateLastMessage,
    setIsStreaming,
    setError,
    clearError,
    setSelectedText,
    initializeSession,
  } = useChatWidget();

  const abortControllerRef = useRef<AbortController | null>(null);

  /**
   * Send a message and handle streaming response
   */
  const sendMessage = useCallback(
    async (question: string, selectedText?: string) => {
      if (!sessionId) {
        setError('Session not initialized. Please refresh the page.');
        return;
      }

      clearError();

      // Add user message immediately
      const userMessage: Message = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: question,
        timestamp: new Date(),
      };
      addMessage(userMessage);

      // Track if we've created the assistant message yet
      let assistantMessageCreated = false;
      const assistantMessageId = `assistant-${Date.now()}`;

      setIsStreaming(true);

      let fullResponse = '';
      let citations: Citation[] = [];

      try {
        // Start streaming
        abortControllerRef.current = await sendMessageStream(
          {
            session_id: sessionId,
            question,
            selected_text: selectedText,
          },
          (event: StreamEvent) => {
            console.log('[ChatStream] Received event:', event.type);

            switch (event.type) {
              case 'token':
                // Append token to response
                if (event.content) {
                  fullResponse += event.content;
                  console.log('[ChatStream] Token added, full response length:', fullResponse.length);
                  console.log('[ChatStream] Current response preview:', fullResponse.substring(0, 50) + '...');

                  // Create assistant message only when first token arrives
                  if (!assistantMessageCreated) {
                    const assistantMessage: Message = {
                      id: assistantMessageId,
                      role: 'assistant',
                      content: fullResponse,
                      timestamp: new Date(),
                      citations: [],
                    };
                    addMessage(assistantMessage);
                    assistantMessageCreated = true;
                  } else {
                    updateLastMessage(fullResponse);
                  }
                } else {
                  console.warn('[ChatStream] Token event missing content:', event);
                }
                break;

              case 'citations':
                // Store citations
                if (event.citations) {
                  citations = event.citations;
                  console.log('[ChatStream] Citations received:', citations.length, 'sources');

                  // Only update if assistant message was created
                  if (assistantMessageCreated) {
                    updateLastMessage(fullResponse, citations);
                  } else {
                    console.warn('[ChatStream] Citations received but no message created yet');
                  }
                } else {
                  console.warn('[ChatStream] Citations event missing citations array:', event);
                }
                break;

              case 'metadata':
                // Could log metadata for debugging
                console.log('[ChatStream] Metadata:', event.metadata);
                break;

              case 'done':
                // Stream completed successfully
                console.log('[ChatStream] ✓ Stream done! Final response length:', fullResponse.length);
                setIsStreaming(false);
                setSelectedText(null); // Clear selected text mode
                break;

              case 'error':
                // Stream error
                console.error('[ChatStream] Stream error event:', event.error);
                setError(event.error || 'An error occurred while streaming the response.');
                setIsStreaming(false);
                break;

              default:
                console.warn('[ChatStream] Unknown event type:', event);
            }
          }
        );
      } catch (error) {
        console.error('[ChatStream] Error:', error);

        // Check if this is a session 404 error (session expired/not found)
        if (error instanceof ChatApiError && error.statusCode === 404) {
          console.log('[ChatStream] Session not found (404) - session may have expired after backend restart');
          console.log('[ChatStream] Attempting to create new session...');

          // Clear old session from localStorage
          localStorage.removeItem('robobook_chat_session_id');
          localStorage.removeItem('robobook_chat_session_timestamp');

          // Create new session
          try {
            await initializeSession();
            console.log('[ChatStream] New session created successfully');

            // Show user-friendly error message
            setError('Your session expired. Please send your message again.');
            setTimeout(() => clearError(), 5000);
          } catch (initError) {
            console.error('[ChatStream] Failed to recreate session:', initError);
            setError('Session expired. Please refresh the page to start a new session.');
          }
        } else {
          // Other errors
          setError('Failed to send message. Please try again.');
        }

        setIsStreaming(false);
      }
    },
    [sessionId, addMessage, updateLastMessage, setIsStreaming, setError, clearError, setSelectedText, initializeSession]
  );

  /**
   * Cancel ongoing stream
   */
  const cancelStream = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setIsStreaming(false);
    }
  }, [setIsStreaming]);

  return {
    sendMessage,
    cancelStream,
  };
}
