/**
 * Docusaurus Root Component (Swizzled)
 *
 * This component wraps the entire application and persists across all pages.
 * Used for global chat widget injection with SSR/SSG safety.
 *
 * CRITICAL: Must be 100% SSR-safe for Docusaurus build to work.
 */

import React, { Suspense, lazy } from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';

// Lazy load ChatWidget to ensure it only loads in browser
const ChatWidget = lazy(() =>
  import('@site/src/components/ChatWidget').catch((err) => {
    console.error('[Root] Failed to load ChatWidget:', err);
    // Return empty component on error
    return { default: () => null };
  })
);

/**
 * Root component wrapper
 * Injects ChatWidget globally while ensuring SSR compatibility
 */
export default function Root({ children }: { children: React.ReactNode }) {
  return (
    <>
      {children}
      <BrowserOnly fallback={<div />}>
        {() => (
          <Suspense fallback={<div />}>
            <ChatWidget />
          </Suspense>
        )}
      </BrowserOnly>
    </>
  );
}
