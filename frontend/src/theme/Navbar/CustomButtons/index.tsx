/**
 * Custom Navbar Buttons
 * RoboBook Tech Cyber Theme
 * Sign In and Sign Up buttons with icons
 */
import React from 'react';
import styles from './styles.module.css';

export function SignInButton() {
  return (
    <a href="/signin" className={styles.signInBtn}>
      <svg
        width="18"
        height="18"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M21 12H9" />
      </svg>
      <span>Sign In</span>
    </a>
  );
}

export function SignUpButton() {
  return (
    <a href="/signup" className={styles.signUpBtn}>
      <svg
        width="18"
        height="18"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
        <circle cx="12" cy="7" r="4" />
      </svg>
      <span>Sign Up</span>
    </a>
  );
}
