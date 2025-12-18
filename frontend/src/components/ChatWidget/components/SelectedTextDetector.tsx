/**
 * Selected Text Detector Component
 *
 * Global listener for text selection events.
 * Shows "Ask about this" button when user selects text.
 * Opens widget with selected text context when button is clicked.
 */

import React, { useEffect, useState } from 'react';
import { useChatWidget } from '../context/ChatWidgetContext';
import AskAboutButton from './AskAboutButton';
import { WIDGET_CONSTANTS } from '../config';

const { MIN_SELECTED_TEXT_LENGTH, MAX_SELECTED_TEXT_LENGTH, SELECTION_THROTTLE_MS } = WIDGET_CONSTANTS;

interface SelectionPosition {
  text: string;
  x: number;
  y: number;
}

export default function SelectedTextDetector() {
  const { setSelectedText, openWidget, isOpen } = useChatWidget();
  const [selectionPosition, setSelectionPosition] = useState<SelectionPosition | null>(null);

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;

    const handleSelectionChange = () => {
      clearTimeout(timeoutId);

      timeoutId = setTimeout(() => {
        if (typeof window === 'undefined') return;

        const selection = window.getSelection();
        const text = selection?.toString().trim();

        // Debug logging for selection
        if (text && text.length > 0) {
          console.log('[SelectedTextDetector] Selection detected:', {
            length: text.length,
            minRequired: MIN_SELECTED_TEXT_LENGTH,
            maxAllowed: MAX_SELECTED_TEXT_LENGTH,
            tooShort: text.length < MIN_SELECTED_TEXT_LENGTH,
            tooLong: text.length > MAX_SELECTED_TEXT_LENGTH,
            preview: text.substring(0, 50) + (text.length > 50 ? '...' : ''),
          });
        }

        if (
          text &&
          text.length >= MIN_SELECTED_TEXT_LENGTH &&
          text.length <= MAX_SELECTED_TEXT_LENGTH
        ) {
          // Get selection position
          const range = selection?.getRangeAt(0);
          const rect = range?.getBoundingClientRect();

          if (rect) {
            // Get parent element to log what type of element was selected
            const parentElement = range.commonAncestorContainer.parentElement;
            const elementType = parentElement?.tagName || 'TEXT';

            // Position button at TOP CENTER of selection (not to the right)
            // Button width is approximately 150px, so offset by half
            const buttonWidth = 150;
            const centerX = rect.left + (rect.width / 2) - (buttonWidth / 2);

            setSelectionPosition({
              text,
              x: centerX + window.scrollX,
              y: rect.top + window.scrollY,
            });

            console.log('[SelectedTextDetector] Text selected (showing button):', {
              length: text.length,
              elementType,
              preview: text.substring(0, 50) + (text.length > 50 ? '...' : ''),
              position: { x: centerX, y: rect.top - 45 }, // Top of selection, 45px above
            });
          }
        } else {
          // Clear if selection is too short or too long
          setSelectionPosition(null);
        }
      }, SELECTION_THROTTLE_MS);
    };

    console.log('[SelectedTextDetector] Installing selection listeners');

    // Use mouseup/touchend for better performance than selectionchange
    document.addEventListener('mouseup', handleSelectionChange);
    document.addEventListener('touchend', handleSelectionChange);

    return () => {
      clearTimeout(timeoutId);
      document.removeEventListener('mouseup', handleSelectionChange);
      document.removeEventListener('touchend', handleSelectionChange);
    };
  }, []);

  /**
   * Handle "Ask about this" button click
   */
  const handleAskAbout = () => {
    if (selectionPosition) {
      console.log('[SelectedTextDetector] Opening widget with selected text');
      setSelectedText(selectionPosition.text);
      openWidget();
      setSelectionPosition(null); // Hide button after opening
    }
  };

  // Hide button if panel is open or no selection
  if (!selectionPosition || isOpen) return null;

  return (
    <AskAboutButton
      x={selectionPosition.x}
      y={selectionPosition.y}
      onClick={handleAskAbout}
    />
  );
}
