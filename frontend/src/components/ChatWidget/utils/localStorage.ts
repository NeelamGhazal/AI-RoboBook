/**
 * localStorage utilities for chat session persistence
 *
 * Handles session ID storage with TTL (Time-To-Live) expiration
 */

import { WIDGET_CONSTANTS, defaultConfig } from '../config';

const { SESSION_KEY, SESSION_TIMESTAMP_KEY, WIDGET_STATE_KEY } = WIDGET_CONSTANTS;

/**
 * Check if localStorage is available
 * (may be blocked by browser privacy settings or SSR)
 */
function isLocalStorageAvailable(): boolean {
  try {
    const testKey = '__localStorage_test__';
    localStorage.setItem(testKey, 'test');
    localStorage.removeItem(testKey);
    return true;
  } catch (e) {
    return false;
  }
}

/**
 * Get session ID from localStorage
 * Returns null if expired or not found
 */
export function getSessionId(): string | null {
  if (!isLocalStorageAvailable()) return null;

  try {
    const sessionId = localStorage.getItem(SESSION_KEY);
    const timestamp = localStorage.getItem(SESSION_TIMESTAMP_KEY);

    if (!sessionId || !timestamp) return null;

    // Check if session has expired (24 hours TTL)
    const sessionAge = Date.now() - parseInt(timestamp, 10);
    const ttlMs = defaultConfig.sessionTtlHours * 60 * 60 * 1000;

    if (sessionAge > ttlMs) {
      // Session expired - clear it
      clearSession();
      return null;
    }

    return sessionId;
  } catch (e) {
    console.error('[ChatWidget] Failed to get session ID:', e);
    return null;
  }
}

/**
 * Save session ID to localStorage with current timestamp
 */
export function saveSessionId(sessionId: string): void {
  if (!isLocalStorageAvailable()) return;

  try {
    localStorage.setItem(SESSION_KEY, sessionId);
    localStorage.setItem(SESSION_TIMESTAMP_KEY, Date.now().toString());
  } catch (e) {
    console.error('[ChatWidget] Failed to save session ID:', e);
  }
}

/**
 * Clear session ID and timestamp from localStorage
 */
export function clearSession(): void {
  if (!isLocalStorageAvailable()) return;

  try {
    localStorage.removeItem(SESSION_KEY);
    localStorage.removeItem(SESSION_TIMESTAMP_KEY);
  } catch (e) {
    console.error('[ChatWidget] Failed to clear session:', e);
  }
}

/**
 * Get widget state from localStorage (isOpen)
 */
export function getWidgetState(): { isOpen: boolean } {
  if (!isLocalStorageAvailable()) return { isOpen: false };

  try {
    const state = localStorage.getItem(WIDGET_STATE_KEY);
    if (!state) return { isOpen: false };

    return JSON.parse(state);
  } catch (e) {
    console.error('[ChatWidget] Failed to get widget state:', e);
    return { isOpen: false };
  }
}

/**
 * Save widget state to localStorage
 */
export function saveWidgetState(state: { isOpen: boolean }): void {
  if (!isLocalStorageAvailable()) return;

  try {
    localStorage.setItem(WIDGET_STATE_KEY, JSON.stringify(state));
  } catch (e) {
    console.error('[ChatWidget] Failed to save widget state:', e);
  }
}
