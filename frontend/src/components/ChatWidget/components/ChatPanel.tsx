/**
 * Chat Panel Component
 *
 * Main chat interface container with header, message list, and input bar.
 * Slides in/out from the right with smooth animation.
 */

import React from 'react';
import ChatHeader from './ChatHeader';
import MessageList from './MessageList';
import InputBar from './InputBar';
import styles from './ChatPanel.module.css';

interface ChatPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ChatPanel({ isOpen, onClose }: ChatPanelProps) {
  if (!isOpen) return null;

  return (
    <div className={styles.panel} role="dialog" aria-label="Chat widget">
      <ChatHeader onClose={onClose} />
      <MessageList />
      <InputBar />
    </div>
  );
}
