import React, { useState } from 'react';
import styles from './styles.module.css';
import { SignInButton, SignUpButton } from '@theme/Navbar/CustomButtons';
import NavbarColorModeToggle from '@theme/Navbar/ColorModeToggle';
import SearchBar from '@theme/SearchBar';

export function MobileMenuToggle() {
  const [isOpen, setIsOpen] = useState(false);

  const toggleMenu = () => setIsOpen(!isOpen);

  return (
    <>
      {/* Hamburger button - only visible on mobile */}
      <button
        className={styles.mobileMenuToggle}
        onClick={toggleMenu}
        aria-label="Toggle mobile menu"
        aria-expanded={isOpen}
      >
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          {isOpen ? (
            // X icon when menu is open
            <>
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </>
          ) : (
            // Hamburger icon when menu is closed
            <>
              <line x1="3" y1="12" x2="21" y2="12" />
              <line x1="3" y1="6" x2="21" y2="6" />
              <line x1="3" y1="18" x2="21" y2="18" />
            </>
          )}
        </svg>
      </button>

      {/* Slide-in menu */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div className={styles.backdrop} onClick={toggleMenu} />

          {/* Menu panel */}
          <div className={styles.mobileMenu}>
            <div className={styles.menuItems}>
              <div className={styles.searchContainer}>
                <SearchBar />
              </div>
              <SignInButton />
              <SignUpButton />
              <NavbarColorModeToggle />
            </div>
          </div>
        </>
      )}
    </>
  );
}
