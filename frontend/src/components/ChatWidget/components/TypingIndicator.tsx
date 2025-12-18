/**
 * Typing Indicator Component
 *
 * Animated dots to indicate assistant is typing/thinking.
 */

import React from 'react';
import styles from './TypingIndicator.module.css';

export default function TypingIndicator() {
  return (
    <div className={styles.indicator}>
      <div className={styles.dot}></div>
      <div className={styles.dot}></div>
      <div className={styles.dot}></div>
    </div>
  );
}
