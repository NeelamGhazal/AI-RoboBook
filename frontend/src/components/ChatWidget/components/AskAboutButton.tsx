/**
 * Ask About Button Component
 *
 * Floating button that appears when text is selected.
 * Clicking opens the chat widget with selected text context.
 */

import React from 'react';

interface AskAboutButtonProps {
  x: number;
  y: number;
  onClick: () => void;
}

export default function AskAboutButton({ x, y, onClick }: AskAboutButtonProps) {
  // Position button at top-center of selection
  // x is already calculated as center position by SelectedTextDetector
  const style: React.CSSProperties = {
    position: 'absolute',
    left: `${x}px`, // Center of selection (pre-calculated)
    top: `${y - 45}px`,  // 45px above selection top
    zIndex: 900, // Below chat panel (which is 1000+) but above content
    padding: '8px 12px',
    background: 'linear-gradient(135deg, #00d4ff 0%, #0ea5e9 100%)',
    border: '2px solid white',
    borderRadius: '20px',
    color: 'white',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
    boxShadow: '0 4px 20px rgba(0, 212, 255, 0.5)',
    whiteSpace: 'nowrap',
    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.2s ease-in-out',
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    opacity: 1,
    animation: 'fadeIn 0.2s ease-in-out',
  };

  const handleMouseEnter = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.currentTarget.style.transform = 'scale(1.05)';
    e.currentTarget.style.boxShadow = '0 6px 24px rgba(0, 212, 255, 0.7)';
  };

  const handleMouseLeave = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.currentTarget.style.transform = 'scale(1)';
    e.currentTarget.style.boxShadow = '0 4px 20px rgba(0, 212, 255, 0.5)';
  };

  return (
    <button
      style={style}
      onClick={onClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      aria-label="Ask about selected text"
      type="button"
    >
      <svg
        width="16"
        height="16"
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
        <path
          d="M12 8v4M12 16h.01"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      Ask about this
    </button>
  );
}
