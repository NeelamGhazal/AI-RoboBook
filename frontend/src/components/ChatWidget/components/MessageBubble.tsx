/**
 * Message Bubble Component
 *
 * Displays a single chat message (user or assistant) with citations.
 */

import React from 'react';
import type { Message } from '../types';
import CitationBadge from './CitationBadge';
import styles from './MessageBubble.module.css';

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`${styles.bubble} ${isUser ? styles.userBubble : styles.assistantBubble}`}>
      <div className={styles.content}>
        {message.content}
      </div>
      {!isUser && message.citations && message.citations.length > 0 && (
        <div className={styles.citations}>
          {message.citations.map((citation, index) => (
            <CitationBadge key={citation.chunk_id} citation={citation} index={index} />
          ))}
        </div>
      )}
      <div className={styles.timestamp}>
        {new Date(message.timestamp).toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit',
        })}
      </div>
    </div>
  );
}
