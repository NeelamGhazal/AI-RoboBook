/**
 * Text Selection Hook
 *
 * Detects when user selects text on the page and provides selection info.
 */

import { useState, useEffect, useCallback } from 'react';
import { WIDGET_CONSTANTS } from '../config';

const { MIN_SELECTED_TEXT_LENGTH, MAX_SELECTED_TEXT_LENGTH, SELECTION_THROTTLE_MS } =
  WIDGET_CONSTANTS;

export interface SelectionInfo {
  text: string;
  x: number; // Mouse X position
  y: number; // Mouse Y position
}

/**
 * Hook to track text selection on the page
 */
export function useTextSelection() {
  const [selection, setSelection] = useState<SelectionInfo | null>(null);
  const [throttleTimeout, setThrottleTimeout] = useState<NodeJS.Timeout | null>(null);

  /**
   * Handle selection change with throttling
   */
  const handleSelectionChange = useCallback(() => {
    // Clear previous timeout
    if (throttleTimeout) {
      clearTimeout(throttleTimeout);
    }

    // Throttle selection updates
    const timeout = setTimeout(() => {
      const windowSelection = window.getSelection();
      const selectedText = windowSelection?.toString().trim();

      // Check if selection meets minimum length
      if (
        selectedText &&
        selectedText.length >= MIN_SELECTED_TEXT_LENGTH &&
        selectedText.length <= MAX_SELECTED_TEXT_LENGTH
      ) {
        // Get selection position
        const range = windowSelection?.getRangeAt(0);
        const rect = range?.getBoundingClientRect();

        if (rect) {
          setSelection({
            text: selectedText,
            x: rect.right + window.scrollX,
            y: rect.top + window.scrollY,
          });

          console.log('[TextSelection] Text selected:', {
            length: selectedText.length,
            position: { x: rect.right, y: rect.top },
          });
        }
      } else {
        // Clear selection if too short or too long
        setSelection(null);
      }
    }, SELECTION_THROTTLE_MS);

    setThrottleTimeout(timeout);
  }, [throttleTimeout]);

  /**
   * Handle mouseup event (when user releases mouse after selecting)
   */
  const handleMouseUp = useCallback(() => {
    // Delay to ensure selection is complete
    setTimeout(() => {
      handleSelectionChange();
    }, 50);
  }, [handleSelectionChange]);

  /**
   * Clear selection
   */
  const clearSelection = useCallback(() => {
    setSelection(null);
    window.getSelection()?.removeAllRanges();
  }, []);

  /**
   * Set up and clean up event listeners
   */
  useEffect(() => {
    if (typeof window === 'undefined') return;

    console.log('[TextSelection] Installing text selection listener');

    // Listen for selection changes
    document.addEventListener('selectionchange', handleSelectionChange);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      console.log('[TextSelection] Removing text selection listener');
      document.removeEventListener('selectionchange', handleSelectionChange);
      document.removeEventListener('mouseup', handleMouseUp);

      if (throttleTimeout) {
        clearTimeout(throttleTimeout);
      }
    };
  }, [handleSelectionChange, handleMouseUp, throttleTimeout]);

  return {
    selection,
    clearSelection,
  };
}
