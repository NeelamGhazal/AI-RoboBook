import React from 'react';
import styles from './styles.module.css';

export default function ContentButtons() {
  return (
    <div className={styles.contentButtons}>
      <button className={styles.personalizedModeBtn}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
        Personalized Mode
      </button>
      <button className={styles.languageToggleBtn}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M5 8h14M5 8a2 2 0 1 1 0-4h14a2 2 0 1 1 0 4M5 8v4a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8"/>
        </svg>
        English / اردو
      </button>
    </div>
  );
}
