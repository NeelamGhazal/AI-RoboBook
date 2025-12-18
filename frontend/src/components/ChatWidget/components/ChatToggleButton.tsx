/**
 * Chat Toggle Button Component
 *
 * Floating button that opens/closes the chat widget.
 * Always visible in bottom-right corner with cyan glow on hover.
 */

import React from 'react';
import styles from './ChatToggleButton.module.css';

interface ChatToggleButtonProps {
  isOpen: boolean;
  onClick: () => void;
}

export default function ChatToggleButton({ isOpen, onClick }: ChatToggleButtonProps) {
  console.log('[ChatToggleButton] Rendering button - isOpen:', isOpen);
  console.log('[ChatToggleButton] Toggle button inline styles applied — should be visible now');

  // MAXIMUM VISIBILITY INLINE STYLES - bypasses all CSS conflicts
  const fallbackStyle: React.CSSProperties = {
    // Position (strongest possible)
    position: 'fixed',
    bottom: '32px',
    right: '32px',

    // Size and shape
    width: '60px',
    height: '60px',
    borderRadius: '50%',

    // Visibility enforcement
    display: 'block',
    visibility: 'visible',
    opacity: 1,
    pointerEvents: 'auto',

    // Background (bright cyan gradient for maximum contrast)
    background: 'linear-gradient(135deg, #00d4ff 0%, #0ea5e9 100%)',

    // Border (white border for sharp contrast)
    border: '3px solid white',

    // Shadow (strong cyan glow)
    boxShadow: '0 8px 30px rgba(0, 212, 255, 0.4)',

    // Layout (flexbox centering)
    alignItems: 'center',
    justifyContent: 'center',

    // Interaction
    cursor: 'pointer',
    color: 'white',

    // Z-index (maximum)
    zIndex: 9999,

    // Animation
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',

    // Remove defaults
    outline: 'none',
    margin: '0',
    padding: '0',
  };

  return (
    <button
      className={styles.toggleButton}
      style={fallbackStyle}
      onClick={onClick}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'scale(1.15)'; // Stronger grow effect
        e.currentTarget.style.boxShadow = '0 0 40px rgba(0, 212, 255, 0.9)'; // Intense cyan glow
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'scale(1)';
        e.currentTarget.style.boxShadow = '0 8px 30px rgba(0, 212, 255, 0.4)'; // Return to default glow
      }}
      aria-label={isOpen ? 'Close chat widget' : 'Open chat widget'}
      aria-expanded={isOpen}
      type="button"
    >
      {isOpen ? (
        <svg
          width="24"
          height="24"
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
      ) : (
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          aria-hidden="true"
        >
          <path
            d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      )}
    </button>
  );
}
