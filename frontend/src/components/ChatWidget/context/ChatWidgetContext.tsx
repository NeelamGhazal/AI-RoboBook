/**
 * Chat Widget Context Provider
 *
 * Manages global state for the chat widget including:
 * - Widget open/closed state
 * - Messages and conversation history
 * - Session management
 * - Selected text mode
 */

import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import type { Message, WidgetState, Citation } from '../types';
import { createSession } from '../api/chatApi';
import { getSessionId, saveSessionId, getWidgetState, saveWidgetState } from '../utils/localStorage';

interface ChatWidgetContextValue {
  // Widget state
  isOpen: boolean;
  isLoading: boolean;
  isStreaming: boolean;
  error: string | null;

  // Session
  sessionId: string | null;

  // Messages
  messages: Message[];

  // Selected text mode
  selectedText: string | null;

  // Actions
  toggleWidget: () => void;
  openWidget: () => void;
  closeWidget: () => void;
  addMessage: (message: Message) => void;
  updateLastMessage: (content: string, citations?: Citation[]) => void;
  setSelectedText: (text: string | null) => void;
  setIsLoading: (loading: boolean) => void;
  setIsStreaming: (streaming: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  initializeSession: () => Promise<void>;
}

const ChatWidgetContext = createContext<ChatWidgetContextValue | null>(null);

/**
 * Hook to access chat widget context
 */
export function useChatWidget() {
  const context = useContext(ChatWidgetContext);
  if (!context) {
    throw new Error('useChatWidget must be used within ChatWidgetProvider');
  }
  return context;
}

/**
 * Chat Widget Provider Component
 */
export function ChatWidgetProvider({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [selectedText, setSelectedText] = useState<string | null>(null);

  // Track if session initialization is in progress
  const initializingRef = useRef(false);

  /**
   * Initialize session on mount
   */
  const initializeSession = useCallback(async () => {
    if (initializingRef.current) return;
    initializingRef.current = true;

    try {
      // Check for existing session
      const existingSessionId = getSessionId();

      if (existingSessionId) {
        setSessionId(existingSessionId);
      } else {
        // Create new session
        const newSessionId = await createSession();
        setSessionId(newSessionId);
        saveSessionId(newSessionId);
      }
    } catch (err) {
      console.error('[ChatWidget] Failed to initialize session:', err);
      setError('Failed to initialize chat session. Please refresh the page.');
    } finally {
      initializingRef.current = false;
    }
  }, []);

  /**
   * Restore widget state from localStorage on mount
   */
  useEffect(() => {
    const savedState = getWidgetState();
    setIsOpen(savedState.isOpen);

    // Initialize session
    initializeSession();
  }, [initializeSession]);

  /**
   * Save widget state to localStorage when it changes
   */
  useEffect(() => {
    saveWidgetState({ isOpen });
  }, [isOpen]);

  /**
   * Toggle widget open/closed
   */
  const toggleWidget = useCallback(() => {
    setIsOpen(prev => !prev);
  }, []);

  /**
   * Open widget
   */
  const openWidget = useCallback(() => {
    setIsOpen(true);
  }, []);

  /**
   * Close widget
   */
  const closeWidget = useCallback(() => {
    setIsOpen(false);
    setSelectedText(null); // Clear selected text when closing
  }, []);

  /**
   * Add a new message to the conversation
   */
  const addMessage = useCallback((message: Message) => {
    setMessages(prev => [...prev, message]);
  }, []);

  /**
   * Update the last message (used for streaming)
   */
  const updateLastMessage = useCallback((content: string, citations?: Citation[]) => {
    console.log('[ChatWidgetContext] updateLastMessage called with content length:', content.length);
    console.log('[ChatWidgetContext] Content preview:', content.substring(0, 100));

    setMessages(prev => {
      if (prev.length === 0) {
        console.warn('[ChatWidgetContext] No messages to update!');
        return prev;
      }

      const updated = [...prev];
      const lastMessage = updated[updated.length - 1];

      console.log('[ChatWidgetContext] Updating message ID:', lastMessage.id);
      console.log('[ChatWidgetContext] Old content length:', lastMessage.content.length);
      console.log('[ChatWidgetContext] New content length:', content.length);

      updated[updated.length - 1] = {
        ...lastMessage,
        content,
        citations: citations || lastMessage.citations,
      };

      return updated;
    });
  }, []);

  /**
   * Clear error message
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const value: ChatWidgetContextValue = {
    isOpen,
    isLoading,
    isStreaming,
    error,
    sessionId,
    messages,
    selectedText,
    toggleWidget,
    openWidget,
    closeWidget,
    addMessage,
    updateLastMessage,
    setSelectedText,
    setIsLoading,
    setIsStreaming,
    setError,
    clearError,
    initializeSession,
  };

  return (
    <ChatWidgetContext.Provider value={value}>
      {children}
    </ChatWidgetContext.Provider>
  );
}
