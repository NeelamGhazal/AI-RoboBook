/**
 * Input Bar Component
 *
 * Text input and send button for user messages.
 */

import React, { useState, useRef, KeyboardEvent } from 'react';
import { useChatWidget } from '../context/ChatWidgetContext';
import { useChatStream } from '../hooks/useChatStream';
import styles from './InputBar.module.css';

export default function InputBar() {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { isStreaming, isLoading, selectedText } = useChatWidget();
  const { sendMessage } = useChatStream();

  const handleSubmit = async () => {
    const trimmedInput = input.trim();
    if (!trimmedInput || isStreaming || isLoading) return;

    // Send message with optional selected text context
    await sendMessage(trimmedInput, selectedText || undefined);

    // Clear input
    setInput('');

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);

    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  };

  const isDisabled = isStreaming || isLoading;

  return (
    <div className={styles.container}>
      {selectedText && (
        <div className={styles.selectedTextBadge}>
          <span className={styles.badgeIcon}>📌</span>
          <span className={styles.badgeText}>
            Asking about: "{selectedText.substring(0, 50)}..."
          </span>
        </div>
      )}
      <div className={styles.inputContainer}>
        <textarea
          ref={textareaRef}
          className={styles.textarea}
          value={input}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder={selectedText ? "Ask about the selected text..." : "Ask a question..."}
          disabled={isDisabled}
          rows={1}
          aria-label="Message input"
        />
        <button
          className={styles.sendButton}
          onClick={handleSubmit}
          disabled={isDisabled || !input.trim()}
          aria-label="Send message"
          type="button"
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            aria-hidden="true"
          >
            <path
              d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>
    </div>
  );
}
