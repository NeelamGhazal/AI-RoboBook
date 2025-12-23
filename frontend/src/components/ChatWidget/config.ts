/**
 * Configuration for RAG Chatbot Frontend Widget
 */

import type { ChatWidgetConfig } from './types';

/**
 * Get API URL with browser-safe fallback
 * Checks browser window global first, then falls back to hardcoded default
 * IMPORTANT: process.env is NOT available in browser - causes "process is not defined" error
 */
function getApiUrl(): string {
  // Check for browser runtime config
  if (typeof window !== 'undefined' && (window as any).CHAT_API_URL) {
    return (window as any).CHAT_API_URL;
  }

  // Fallback to localhost for development
  // TODO: In production, set window.CHAT_API_URL or update this to production URL
  return 'https://proud-nourishment-production-7f99.up.railway.app/';
}

/**
 * Default widget configuration
 *
 * API URL can be overridden by setting window.CHAT_API_URL
 * Default: http://localhost:8000 (for development)
 */
export const defaultConfig: ChatWidgetConfig = {
  // API endpoint - browser-safe (NO process.env)
  apiUrl: getApiUrl(),

  // Session persistence duration (24 hours)
  sessionTtlHours: 24,

  // Maximum messages to load from history
  maxMessages: 50,

  // Enable selected text "Ask about this" feature
  enableSelectedText: true,

  // Widget position on screen
  position: 'bottom-right',

  // Theme variant (matches RoboBook Tech Cyber theme)
  theme: 'cyber',
};

/**
 * API endpoints (relative to apiUrl)
 */
export const API_ENDPOINTS = {
  createSession: '/api/v1/sessions',
  chat: '/api/v1/chat',
  chatStream: '/api/v1/chat/stream',
  chatHistory: (sessionId: string) => `/api/v1/chat/history/${sessionId}`,
} as const;

/**
 * Widget behavior constants
 */
export const WIDGET_CONSTANTS = {
  // localStorage keys
  SESSION_KEY: 'robobook_chat_session_id',
  SESSION_TIMESTAMP_KEY: 'robobook_chat_session_timestamp',
  WIDGET_STATE_KEY: 'robobook_chat_widget_state',

  // Selected text detection
  MIN_SELECTED_TEXT_LENGTH: 50, // Minimum 50 chars to show "Ask about this" button
  MAX_SELECTED_TEXT_LENGTH: 500,
  SELECTION_THROTTLE_MS: 200,

  // Streaming
  STREAM_TIMEOUT_MS: 30000, // 30 seconds
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY_MS: 1000,

  // UI animations
  PANEL_ANIMATION_DURATION_MS: 300,
  TYPING_INDICATOR_DOT_COUNT: 3,
  TYPING_INDICATOR_ANIMATION_MS: 600,

  // Touch targets (mobile)
  MIN_TOUCH_TARGET_SIZE: 44, // pixels
} as const;

/**
 * Error messages for user-facing errors
 */
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Unable to connect. Please check your internet connection and try again.',
  TIMEOUT_ERROR: 'Request timed out. Please try again.',
  SESSION_ERROR: 'Failed to create session. Please refresh the page.',
  RATE_LIMIT_ERROR: 'Too many requests. Please wait a moment and try again.',
  UNKNOWN_ERROR: 'Something went wrong. Please try again.',
} as const;

/**
 * Merge user config with defaults
 */
export function mergeConfig(userConfig?: Partial<ChatWidgetConfig>): ChatWidgetConfig {
  return {
    ...defaultConfig,
    ...userConfig,
  };
}
