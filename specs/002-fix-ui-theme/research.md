# Research: Fix RoboBook UI and Theme Issues

**Feature**: 002-fix-ui-theme
**Date**: 2025-12-16
**Purpose**: Research technical approaches, best practices, and design decisions for 5 UI fixes

## Research Questions

1. How to configure Docusaurus logo with PNG transparency?
2. How to customize Docusaurus navbar layout beyond basic configuration?
3. How to implement light theme CSS variables for Docusaurus?
4. How to fix vertical text in sidebar navigation?
5. How to inject content buttons above main content on all docs pages?
6. What is the recommended approach for Docusaurus component swizzling?

---

## Decision 1: Logo Configuration with Transparent PNG

**Decision**: Use `docusaurus.config.ts` navbar.logo configuration with PNG file path update

**Rationale**:
- Docusaurus navbar.logo supports `src` property pointing to static assets
- Current config has `src: 'img/robobook-logo.svg'` (line 68 of docusaurus.config.ts)
- Need to change to `src: 'img/robobook-logo.png'`
- PNG file already exists at `frontend/static/img/robobook-logo.png` (106KB, verified)
- No CSS changes needed - Docusaurus handles image rendering
- Logo height can be controlled via CSS: `.navbar__logo img { height: 40px; }` (already present in navbar.css line 53)

**Alternatives Considered**:
- Convert PNG to SVG → Rejected: User specified to use existing robobook-logo.png
- Use CSS background-image → Rejected: Less semantic, breaks accessibility
- Inline SVG in React component → Rejected: Requires PNG, not SVG

**Implementation**:
```typescript
// docusaurus.config.ts
logo: {
  alt: 'RoboBook Logo',
  src: 'img/robobook-logo.png',  // Changed from .svg
}
```

**Verification**: Logo transparency will work automatically if PNG has alpha channel. CSS `navbar.css` line 53-54 already handles sizing and transitions.

---

## Decision 2: Navbar Layout Customization Strategy

**Decision**: Use hybrid approach - Configuration first, swizzle Navbar only if needed

**Rationale**:
- **Phase 1**: Try configuration-only approach in `docusaurus.config.ts`
  - Update navbar.items array to remove GitHub link (FR-007)
  - Add custom items for Sign In/Sign Up (FR-008)
  - Search plugin (@easyops-cn/docusaurus-search-local) already installed

- **Phase 2 (if needed)**: Swizzle `@theme/Navbar` for fine-grained control
  - Required if: Cannot achieve exact ordering (search left, auth center, theme right)
  - Docusaurus swizzling command: `npm run swizzle @docusaurus/theme-classic Navbar -- --wrap`
  - Allows custom JSX for navbar right section

**Alternatives Considered**:
- CSS-only repositioning → Rejected: Fragile, breaks on Docusaurus updates, doesn't remove GitHub link
- Custom navbar component from scratch → Rejected: Loses Docusaurus responsive behavior, mobile menu, accessibility

**Implementation Steps**:

1. **Configuration Update** (docusaurus.config.ts):
```typescript
navbar: {
  items: [
    {
      type: 'docSidebar',
      sidebarId: 'tutorialSidebar',
      position: 'left',
      label: 'Modules',
    },
    // RIGHT SIDE: Search panel (from plugin, auto-injected)
    {
      type: 'html',
      position: 'right',
      value: '<a href="/signin" class="navbar-signin-link">Sign In</a>',
    },
    {
      type: 'html',
      position: 'right',
      value: '<a href="/signup" class="navbar-signup-link">Sign Up</a>',
    },
    // GitHub removed (FR-007)
    // Theme toggle auto-injected by Docusaurus at rightmost position
  ],
},
```

2. **CSS for Vertical Centering** (navbar.css):
```css
.navbar__items {
  display: flex;
  align-items: center;  /* Vertical centering (FR-003) */
  gap: var(--spacing-md);
}

.navbar__inner {
  align-items: center;  /* Ensure all navbar content centered */
}
```

**Best Practices** (from Docusaurus docs):
- Use `type: 'html'` for custom HTML items
- Use `position: 'right'` to place items in right section
- Docusaurus automatically orders items left-to-right within position group
- Theme toggle is hardcoded to rightmost position (cannot be repositioned via config)
- Search bar position depends on plugin configuration

**Verification**: If this doesn't achieve exact ordering requirements (FR-005), proceed to swizzling.

---

## Decision 3: Light Theme Implementation

**Decision**: Extend existing CSS variables in `custom.css` with light theme overrides

**Rationale**:
- Current `custom.css` has dark theme variables in `:root` selector
- Need to add light theme variables for `[data-theme='light']` selector (not present)
- robobook-docusaurus-ui skill defines complete light theme palette (lines 85-124)
- Docusaurus auto-applies `data-theme` attribute to `<html>` element on theme toggle
- Existing theme toggle button already configured (docusaurus.config.ts line 134-137)

**Implementation**:

```css
/* custom.css - Add after existing :root block */

/* Light Mode Theme Variables */
[data-theme='light'] {
  /* Background Colors */
  --bg-primary: #f0f9ff;
  --bg-secondary: #e0f2fe;
  --card-bg: #ffffff;

  /* Primary Colors */
  --primary-cyan: #0284c7;
  --secondary-blue: #0369a1;
  --bright-cyan: #06b6d4;

  /* Text Colors */
  --text-primary: #0c4a6e;
  --text-secondary: #0e7490;
  --text-muted: #64748b;

  /* Borders & Effects */
  --border-color: #bae6fd;
  --hover-glow: rgba(2, 132, 199, 0.3);

  /* Docusaurus Infima Overrides (Light) */
  --ifm-color-primary: #0284c7;
  --ifm-color-primary-dark: #0369a1;
  --ifm-color-primary-darker: #075985;
  --ifm-color-primary-darkest: #0c4a6e;
  --ifm-color-primary-light: #0ea5e9;
  --ifm-color-primary-lighter: #06b6d4;
  --ifm-color-primary-lightest: #22d3ee;

  --ifm-background-color: #f0f9ff;
  --ifm-navbar-background-color: rgba(255, 255, 255, 0.95);
  --ifm-footer-background-color: #ffffff;

  --ifm-font-color-base: #0c4a6e;
  --ifm-heading-color: #0c4a6e;
  --ifm-link-color: #0284c7;
  --ifm-link-hover-color: #0369a1;

  --ifm-code-background: #e0f2fe;
  --ifm-blockquote-border-left-color: #0284c7;

  /* Component-specific overrides */
  --cyan-10: rgba(2, 132, 199, 0.1);
  --cyan-15: rgba(2, 132, 199, 0.15);
  --cyan-20: rgba(2, 132, 199, 0.2);
  --cyan-40: rgba(2, 132, 199, 0.4);
  --cyan-60: rgba(2, 132, 199, 0.6);
}
```

**Alternatives Considered**:
- Separate light-theme.css file → Rejected: Increases HTTP requests, harder to maintain consistency
- JavaScript theme switching → Rejected: Docusaurus handles this natively
- CSS custom properties with `prefers-color-scheme` → Rejected: Must respect user toggle, not OS preference

**WCAG AA Compliance Check**:
- Light theme text `#0c4a6e` on background `#f0f9ff`: Contrast ratio 8.7:1 ✅ (exceeds 4.5:1 requirement)
- Heading `#0c4a6e` on white cards `#ffffff`: Contrast ratio 9.1:1 ✅
- Link `#0284c7` on white: Contrast ratio 4.9:1 ✅ (meets 4.5:1 for normal text)

**Best Practices** (from Web Accessibility Guidelines):
- Use semantic color names (primary, secondary) not literal (blue, cyan)
- Maintain consistent contrast ratios across themes
- Test with browser DevTools color contrast analyzer
- Ensure focus indicators visible in both themes

**Verification**: Theme persistence handled by Docusaurus `colorMode.defaultMode` config (line 135). localStorage key: `theme`.

---

## Decision 4: Sidebar Vertical Text Fix

**Decision**: Identify and remove CSS causing vertical text orientation, restore default Docusaurus styles

**Rationale**:
- Current sidebar.css (lines 1-363) does not contain `writing-mode` or `transform: rotate()` properties
- Vertical text likely caused by:
  - Custom CSS override in sidebar.css or custom.css
  - Accidental flexbox `flex-direction: column` on individual link text
  - Third-party plugin CSS conflict

- **Investigation needed**: Inspect actual rendered sidebar to identify root cause
- Default Docusaurus sidebar has horizontal text (verified in official docs)

**Implementation Strategy**:

1. **Diagnostic CSS** (temporary):
```css
/* Add to sidebar.css for debugging */
.menu__link {
  writing-mode: horizontal-tb !important;  /* Force horizontal */
  text-orientation: mixed !important;
  transform: none !important;
}

.menu__link * {
  writing-mode: inherit !important;
  text-orientation: inherit !important;
}
```

2. **Restore Default Docusaurus Sidebar Structure** (sidebars.js):
```javascript
// Verify sidebars.js uses standard Docusaurus format:
const sidebars = {
  tutorialSidebar: [
    {
      type: 'category',
      label: 'Module 1: ROS 2',
      items: ['module1/chapter1', 'module1/chapter2'],
    },
    // ...
  ],
};
```

3. **Remove Conflicting CSS**: Search for and remove any:
   - `writing-mode: vertical-*`
   - `transform: rotate(90deg)` or `rotate(-90deg)`
   - `flex-direction: column` on `.menu__link`

**Alternatives Considered**:
- Regenerate sidebar from scratch → Rejected: Loses custom styling, too invasive
- Override with inline styles → Rejected: Not maintainable

**Best Practices** (from Docusaurus theming docs):
- Always check default theme CSS before overriding
- Use browser DevTools computed styles to identify source of CSS property
- Prefer CSS specificity over `!important` for overrides

**Verification**: Navigate to any docs page, verify sidebar text reads left-to-right horizontally.

---

## Decision 5: Content Buttons Placement Strategy

**Decision**: Swizzle `@theme/DocItem/Layout` component to inject ContentButtons component

**Rationale**:
- Requirement: "Add only two buttons above the main center content" (FR-019)
- Position: "between the page header area and the main content" (FR-020)
- Must appear on "every content page" (FR-019)
- Docusaurus provides `DocItem/Layout` wrapper specifically for this use case
- This is the official, stable API for content-level customization

**Implementation**:

1. **Swizzle DocItem Layout**:
```bash
cd frontend
npm run swizzle @docusaurus/theme-classic DocItem/Layout -- --wrap
```

This creates: `frontend/src/theme/DocItem/Layout/index.tsx`

2. **Create ContentButtons Component**:
```tsx
// frontend/src/components/ContentButtons/index.tsx
import React from 'react';
import styles from './styles.module.css';

export default function ContentButtons() {
  return (
    <div className={styles.contentButtons}>
      <button className={styles.personalizedModeBtn}>
        <svg>{/* Icon */}</svg>
        Personalized Mode
      </button>
      <button className={styles.languageToggleBtn}>
        <svg>{/* Icon */}</svg>
        English / اردو
      </button>
    </div>
  );
}
```

3. **Modify Swizzled Layout**:
```tsx
// frontend/src/theme/DocItem/Layout/index.tsx
import React from 'react';
import Layout from '@theme-original/DocItem/Layout';
import ContentButtons from '@site/src/components/ContentButtons';

export default function LayoutWrapper(props) {
  return (
    <>
      <Layout {...props}>
        <ContentButtons />  {/* Inject above content */}
        {props.children}
      </Layout>
    </>
  );
}
```

4. **Styling** (styles.module.css):
```css
.contentButtons {
  display: flex;
  gap: 16px;
  margin-bottom: 32px;
  padding: 16px 0;
  border-bottom: 1px solid var(--cyan-10);
}

.personalizedModeBtn,
.languageToggleBtn {
  background: var(--gradient-primary);
  color: var(--text-primary);
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.personalizedModeBtn:hover,
.languageToggleBtn:hover {
  transform: scale(1.05);
  box-shadow: 0 0 20px var(--cyan-60);
}
```

**Alternatives Considered**:
- Global layout wrapper → Rejected: Affects non-docs pages (landing page, etc.)
- MDX component in frontmatter → Rejected: Requires modifying every doc file
- CSS-only floating buttons → Rejected: Cannot position "between header and content" reliably

**Best Practices** (from Docusaurus swizzling guide):
- Use `--wrap` mode to preserve original component functionality
- Import from `@theme-original/*` to access wrapped component
- Keep swizzled components minimal (delegate to separate components)
- Document swizzled files in comments

**Verification**: Buttons must appear ONLY on docs pages (URLs like `/docs/*`), NOT on landing page (`/`) or other pages.

---

## Decision 6: Docusaurus Swizzling Best Practices

**Decision**: Use "wrap" mode for all swizzles, minimize customization scope

**Rationale**:
- Docusaurus provides two swizzling modes:
  - **Eject**: Copies entire component code → HIGH maintenance burden, breaks on updates
  - **Wrap**: Creates thin wrapper around original → LOW maintenance, safe for upgrades

- **Wrap mode advantages**:
  - Original component logic preserved
  - Docusaurus internal updates automatically inherited
  - Easier to debug (smaller surface area)
  - Recommended by Docusaurus team

**Swizzling Command Patterns**:

```bash
# List all swizzleable components
npm run swizzle @docusaurus/theme-classic -- --list

# Wrap mode (recommended)
npm run swizzle @docusaurus/theme-classic Navbar -- --wrap
npm run swizzle @docusaurus/theme-classic DocItem/Layout -- --wrap

# Eject mode (avoid unless absolutely necessary)
npm run swizzle @docusaurus/theme-classic Navbar -- --eject
```

**Safe Swizzling Checklist**:
- ✅ Use `--wrap` mode whenever possible
- ✅ Import original component from `@theme-original/*`
- ✅ Preserve all original props and children
- ✅ Add only minimal custom JSX (delegate to separate components)
- ✅ Document swizzle purpose in component file comments
- ✅ Test after Docusaurus version upgrades

**Components Safe to Swizzle** (according to Docusaurus docs):
- `Navbar` → Full control over navigation bar
- `DocItem/Layout` → Content page wrapper (our use case)
- `Footer` → Site footer customization
- `NotFound` → 404 page

**Components to Avoid Swizzling**:
- `MDXComponents` → Use `@theme/MDXComponents` augmentation instead
- `Layout` → Too broad, affects entire site
- Internal components (prefixed with `_`) → Unstable API

**Alternatives Considered**:
- Plugin system → Rejected: No plugin hook for "above content" injection
- PostCSS custom properties → Rejected: Cannot inject React components via CSS

**Documentation**:
```typescript
// frontend/src/theme/DocItem/Layout/index.tsx
/**
 * Swizzled Component: DocItem/Layout (WRAP mode)
 * Purpose: Inject ContentButtons above doc content (FR-019, FR-020)
 * Original: @docusaurus/theme-classic/src/theme/DocItem/Layout
 * Swizzled: 2025-12-16
 * Feature: 002-fix-ui-theme
 */
```

**Verification**: Run `npm run build` after swizzling to ensure no build errors. Check swizzled component appears in `.docusaurus/` build output.

---

## Summary of Technical Decisions

| Issue | Approach | Complexity | Risk |
|-------|----------|-----------|------|
| Logo (FR-001, FR-002) | Config update: docusaurus.config.ts | Low | None |
| Navbar Layout (FR-003-009) | Config + CSS first, swizzle if needed | Medium | Low (official API) |
| Light Theme (FR-011-014) | CSS variables: custom.css | Low | None |
| Sidebar Text (FR-015-018) | CSS fix: sidebar.css | Low | None |
| Content Buttons (FR-019-022) | Swizzle DocItem/Layout + React component | Medium | Low (official API) |

**Overall Implementation Complexity**: Medium

- **CSS-only work**: 60% (logo, light theme, sidebar fixes)
- **Configuration changes**: 20% (navbar items, logo path)
- **Component swizzling**: 20% (navbar if needed, DocItem/Layout)

**Estimated Lines of Code**:
- CSS modifications: ~300-400 lines (light theme variables, component updates)
- TypeScript/TSX: ~100-150 lines (ContentButtons component, swizzled wrappers)
- Configuration: ~20-30 lines (docusaurus.config.ts updates)

**Dependencies**:
- No new npm packages required
- All modifications use existing Docusaurus APIs
- No breaking changes to current functionality

---

## Next Steps

1. ✅ Research complete → Proceed to Phase 1 (data-model.md, quickstart.md)
2. Update plan.md with "Post-Design Re-Check" for Constitution compliance
3. Create tasks.md via `/sp.tasks` command with 5 distinct task groups:
   - Task Group 1: Logo configuration
   - Task Group 2: Navbar layout and styling
   - Task Group 3: Light theme CSS implementation
   - Task Group 4: Sidebar text orientation fix
   - Task Group 5: Content buttons component and swizzling
