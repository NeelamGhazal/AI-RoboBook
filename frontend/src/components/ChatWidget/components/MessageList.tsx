/**
 * Message List Component
 *
 * Scrollable container for chat messages with auto-scroll to bottom.
 */

import React, { useEffect, useRef } from 'react';
import { useChatWidget } from '../context/ChatWidgetContext';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';
import styles from './MessageList.module.css';

export default function MessageList() {
  const { messages, isStreaming, isLoading } = useChatWidget();
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isStreaming]);

  return (
    <div className={styles.container}>
      {messages.length === 0 && !isLoading && (
        <div className={styles.emptyState}>
          <svg
            width="64"
            height="64"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className={styles.emptyIcon}
          >
            <path
              d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <h3 className={styles.emptyTitle}>Start a Conversation</h3>
          <p className={styles.emptyText}>
            Ask questions about the textbook content or select text on the page to ask about it specifically.
          </p>
        </div>
      )}
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
      {isStreaming && <TypingIndicator />}
      <div ref={bottomRef} />
    </div>
  );
}
