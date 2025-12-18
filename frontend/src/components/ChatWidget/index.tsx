/**
 * RAG Chatbot Frontend Widget
 *
 * Main entry point for the chat widget component.
 * Provides AI-powered Q&A with streaming responses, citations, and selected-text mode.
 *
 * IMPORTANT: This component is lazy-loaded in Root.tsx for SSR safety.
 * DO NOT import window/document/localStorage at module level.
 */

import React from 'react';
import { ChatWidgetProvider, useChatWidget } from './context/ChatWidgetContext';
import ChatToggleButton from './components/ChatToggleButton';
import ChatPanel from './components/ChatPanel';
import SelectedTextDetector from './components/SelectedTextDetector';
import { defaultConfig } from './config';

/**
 * Internal widget component (uses context)
 */
function ChatWidgetInternal() {
  const { isOpen, toggleWidget, closeWidget } = useChatWidget();

  return (
    <>
      <ChatToggleButton isOpen={isOpen} onClick={toggleWidget} />
      <ChatPanel isOpen={isOpen} onClose={closeWidget} />
      {defaultConfig.enableSelectedText && <SelectedTextDetector />}
    </>
  );
}

/**
 * Main ChatWidget component (provides context)
 * This is the default export that gets lazy-loaded in Root.tsx
 */
export default function ChatWidget() {
  // Ensure we're in browser before rendering
  if (typeof window === 'undefined') {
    console.log('[ChatWidget] SSR mode - skipping render');
    return null;
  }

  console.log('[ChatWidget] Rendering in browser - widget should be visible');

  return (
    <ChatWidgetProvider>
      <ChatWidgetInternal />
    </ChatWidgetProvider>
  );
}
