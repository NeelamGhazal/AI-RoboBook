/**
 * Chat Header Component
 *
 * Header bar with title and close button.
 */

import React from 'react';
import { useChatWidget } from '../context/ChatWidgetContext';
import styles from './ChatHeader.module.css';

interface ChatHeaderProps {
  onClose: () => void;
}

export default function ChatHeader({ onClose }: ChatHeaderProps) {
  const { selectedText } = useChatWidget();

  return (
    <div className={styles.header}>
      <div className={styles.titleContainer}>
        <h2 className={styles.title}>
          {selectedText ? 'Ask About Selection' : 'RoboBook Assistant'}
        </h2>
        {selectedText && (
          <span className={styles.badge}>Selected Text Mode</span>
        )}
      </div>
      <button
        className={styles.closeButton}
        onClick={onClose}
        aria-label="Close chat"
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
            d="M18 6L6 18M6 6l12 12"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>
    </div>
  );
}
