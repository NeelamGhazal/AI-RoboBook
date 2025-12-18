/**
 * Citation Badge Component
 *
 * Clickable badge that displays citation source and navigates to the referenced section.
 */

import React from 'react';
import type { Citation } from '../types';
import styles from './CitationBadge.module.css';

interface CitationBadgeProps {
  citation: Citation;
  index: number;
}

export default function CitationBadge({ citation, index }: CitationBadgeProps) {
  const handleClick = () => {
    if (citation.url) {
      // Navigate to the citation URL
      window.location.href = citation.url;
    }
  };

  return (
    <button
      className={styles.badge}
      onClick={handleClick}
      aria-label={`Citation ${index + 1}: ${citation.section}`}
      type="button"
      title={citation.text_snippet || `${citation.chapter} - ${citation.section}`}
    >
      <span className={styles.number}>{index + 1}</span>
      <span className={styles.text}>{citation.section}</span>
    </button>
  );
}
