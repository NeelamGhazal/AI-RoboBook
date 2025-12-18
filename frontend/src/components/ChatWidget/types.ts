/**
 * Type definitions for RAG Chatbot Frontend Widget
 */

/**
 * Citation source with metadata
 */
export interface Citation {
  chunk_id: string;
  chapter: string;
  section: string;
  url: string;
  confidence_score: number;
  text_snippet?: string;
}

/**
 * Chat message (user or assistant)
 */
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  citations?: Citation[];
}

/**
 * Chat session
 */
export interface Session {
  session_id: string;
  created_at: Date;
  last_active_at: Date;
  user_id?: string;
}

/**
 * Server-Sent Event types from backend streaming
 */
export type StreamEventType = 'token' | 'citations' | 'metadata' | 'done' | 'error';

export interface StreamEvent {
  type: StreamEventType;
  content?: string;
  citations?: Citation[];
  metadata?: {
    retrieval_time_ms: number;
    generation_time_ms: number;
    total_time_ms: number;
    chunks_retrieved: number;
    avg_confidence: number;
    token_count: number;
  };
  error?: string;
}

/**
 * Widget global state
 */
export interface WidgetState {
  isOpen: boolean;
  isLoading: boolean;
  isStreaming: boolean;
  selectedText: string | null;
  error: string | null;
}

/**
 * Chat request payload
 */
export interface ChatRequest {
  session_id: string;
  question: string;
  selected_text?: string;
}

/**
 * Chat response (non-streaming)
 */
export interface ChatResponse {
  answer: string;
  citations: Citation[];
  metadata: {
    retrieval_time_ms: number;
    generation_time_ms: number;
    total_time_ms: number;
    chunks_retrieved: number;
    avg_confidence: number;
    token_count: number;
  };
}

/**
 * Session creation response
 */
export interface SessionResponse {
  session_id: string;
  created_at: string;
}

/**
 * Message history response
 */
export interface MessageHistoryResponse {
  messages: Array<{
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
    sources?: Citation[];
  }>;
  session_id: string;
}

/**
 * Widget configuration options
 */
export interface ChatWidgetConfig {
  apiUrl: string;
  sessionTtlHours: number;
  maxMessages: number;
  enableSelectedText: boolean;
  position: 'bottom-right' | 'bottom-left';
  theme: 'cyber' | 'light' | 'dark';
}
