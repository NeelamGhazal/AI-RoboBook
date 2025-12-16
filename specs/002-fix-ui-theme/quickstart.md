# Developer Quickstart: Fix RoboBook UI and Theme Issues

**Feature**: 002-fix-ui-theme
**Branch**: `002-fix-ui-theme`
**Prerequisites**: Node.js 18+, npm 9+, Git

## Overview

This feature fixes 5 UI and theme issues in the RoboBook Docusaurus site:
1. Logo rendering with transparent PNG
2. Navbar layout reorganization
3. Light theme implementation
4. Docs sidebar horizontal text restoration
5. Content buttons placement above doc content

**Estimated Time**: 4-6 hours
**Complexity**: Medium (CSS + Configuration + Swizzling)

---

## Quick Setup

### 1. Clone and Switch Branch

```bash
# If not already cloned
git clone https://github.com/phyai-humanoid-textbook/phyai-humanoid-textbook.git
cd phyai-humanoid-textbook

# Switch to feature branch
git checkout 002-fix-ui-theme

# Verify branch
git branch --show-current
# Should output: 002-fix-ui-theme
```

### 2. Install Dependencies

```bash
cd frontend
npm install

# Verify Docusaurus version
npm list @docusaurus/core
# Should show: @docusaurus/core@3.9.2
```

### 3. Start Development Server

```bash
npm start

# Site will open at http://localhost:3000
# Hot reload enabled for instant CSS/config changes
```

### 4. Verify Current Issues

Before making changes, verify the 5 issues exist:

| Issue | How to Verify | Expected Current State |
|-------|---------------|------------------------|
| Logo | Check navbar | Shows .svg logo (not .png) |
| Navbar | Check right section | Has GitHub icon, no Sign In/Sign Up |
| Light Theme | Toggle theme | Light theme broken/unstyled |
| Sidebar | Go to any `/docs/*` page | Text may be vertical |
| Content Buttons | Go to any `/docs/*` page | No buttons above content |

---

## Development Workflow

### Task Group 1: Logo Fix

**Files to modify**:
- `frontend/docusaurus.config.ts` (line 68)
- `frontend/static/img/robobook-logo.png` (verify exists)

**Steps**:

```bash
# 1. Verify PNG logo exists
ls -lh frontend/static/img/robobook-logo.png
# Should show file (~106KB)

# 2. Check if PNG has transparency (optional)
file frontend/static/img/robobook-logo.png
# Should mention "PNG image data" with alpha channel

# 3. Edit docusaurus.config.ts
# Change line 68 from:
#   src: 'img/robobook-logo.svg',
# To:
#   src: 'img/robobook-logo.png',

# 4. Test hot reload
# Navbar logo should update immediately
# Verify transparency against both light/dark themes
```

**Acceptance Criteria**:
- ✅ Logo displays as PNG with transparent background
- ✅ Logo visible in both light and dark themes
- ✅ Logo height ~40px (controlled by navbar.css)

---

### Task Group 2: Navbar Layout

**Files to modify**:
- `frontend/docusaurus.config.ts` (navbar.items array, lines 70-82)
- `frontend/src/css/components/navbar.css` (lines 76-81 for vertical centering)

**Phase 2A: Configuration Changes**

```typescript
// frontend/docusaurus.config.ts
navbar: {
  items: [
    {
      type: 'docSidebar',
      sidebarId: 'tutorialSidebar',
      position: 'left',
      label: 'Modules',
    },
    // RIGHT SIDE ITEMS (left to right order)
    // Search automatically injected by plugin
    {
      type: 'html',
      position: 'right',
      value: '<a href="/signin" class="navbar-signin-link"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M21 12H9"/></svg>Sign In</a>',
    },
    {
      type: 'html',
      position: 'right',
      value: '<a href="/signup" class="navbar-signup-link"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2M12 11A4 4 0 1 0 12 3a4 4 0 0 0 0 8z"/></svg>Sign Up</a>',
    },
    // GitHub icon removed (FR-007)
    // Theme toggle auto-positioned at extreme right
  ],
},
```

**Phase 2B: CSS Updates**

```css
/* frontend/src/css/components/navbar.css */

/* Ensure vertical centering (FR-003) */
.navbar__inner {
  display: flex;
  align-items: center;  /* Center all navbar content vertically */
}

.navbar__items {
  display: flex;
  align-items: center;  /* Center items within their container */
  gap: var(--spacing-md);
}

/* Style custom Sign In/Sign Up links */
.navbar-signin-link,
.navbar-signup-link {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-weight: var(--font-weight-semibold);
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: var(--radius-sm);
  transition: all var(--transition-normal);
  text-decoration: none;
}

.navbar-signin-link:hover,
.navbar-signup-link:hover {
  color: var(--color-primary);
  background: var(--cyan-10);
  text-decoration: none;
}

.navbar-signup-link {
  background: var(--gradient-primary);
  color: var(--text-primary) !important;
  border-radius: var(--radius-md);
}

.navbar-signup-link:hover {
  transform: scale(1.05);
  box-shadow: 0 0 20px var(--cyan-60);
}
```

**Testing Checklist**:
- [ ] Navbar items vertically centered
- [ ] Left side: Modules link present
- [ ] Right side (L-R): Search, Sign In, Sign Up, Theme Toggle
- [ ] GitHub icon removed
- [ ] All links functional (even if routes don't exist yet)
- [ ] Responsive on mobile (hamburger menu works)

---

### Task Group 3: Light Theme CSS

**Files to modify**:
- `frontend/src/css/custom.css` (add after line 150)

**Steps**:

```bash
# 1. Open custom.css
code frontend/src/css/custom.css

# 2. Add light theme variables after existing :root block (around line 150)
# See implementation in research.md Decision 3

# 3. Test theme switching
# Click theme toggle in navbar
# Verify colors change smoothly (<300ms transition)

# 4. Test WCAG contrast
# Use browser DevTools Accessibility Inspector
# Verify all text meets AA standard (4.5:1 for normal, 3:1 for large)
```

**Light Theme Variables** (Add to custom.css):

```css
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

  /* Component-specific */
  --cyan-10: rgba(2, 132, 199, 0.1);
  --cyan-15: rgba(2, 132, 199, 0.15);
  --cyan-20: rgba(2, 132, 199, 0.2);
  --cyan-40: rgba(2, 132, 199, 0.4);
  --cyan-60: rgba(2, 132, 199, 0.6);

  /* Docusaurus Infima Overrides */
  --ifm-color-primary: #0284c7;
  --ifm-background-color: #f0f9ff;
  --ifm-navbar-background-color: rgba(255, 255, 255, 0.95);
  --ifm-font-color-base: #0c4a6e;
  --ifm-heading-color: #0c4a6e;
  --ifm-link-color: #0284c7;
  --ifm-code-background: #e0f2fe;
}
```

**Testing Checklist**:
- [ ] Light theme background is sky blue (#f0f9ff)
- [ ] Text is readable (dark blue #0c4a6e on light bg)
- [ ] Links are cyan (#0284c7)
- [ ] Code blocks have light cyan background (#e0f2fe)
- [ ] Navbar has white/translucent background
- [ ] Theme persists on page reload (localStorage)
- [ ] Smooth transition between themes (<300ms)

---

### Task Group 4: Sidebar Text Fix

**Files to modify**:
- `frontend/src/css/components/sidebar.css`
- Potentially `frontend/sidebars.js` (verify structure)

**Diagnostic Steps**:

```bash
# 1. Inspect sidebar in browser DevTools
# Go to any /docs/* page
# Right-click sidebar link → Inspect

# 2. Check computed styles for:
#    - writing-mode (should be horizontal-tb)
#    - text-orientation (should be mixed or upright)
#    - transform (should not have rotate)

# 3. Search for problematic CSS
grep -n "writing-mode" frontend/src/css/components/sidebar.css
grep -n "rotate" frontend/src/css/components/sidebar.css
grep -n "flex-direction" frontend/src/css/components/sidebar.css

# 4. If found, remove or override
```

**Fix CSS** (add to sidebar.css if needed):

```css
/* Force horizontal text orientation (if vertical text present) */
.menu__link,
.menu__link--sublist {
  writing-mode: horizontal-tb !important;
  text-orientation: mixed !important;
  transform: none !important;
}

/* Ensure proper flexbox alignment */
.menu__link {
  display: flex;
  flex-direction: row;  /* NOT column */
  align-items: center;
}
```

**Verify Sidebar Structure** (sidebars.js):

```javascript
// Should match this structure
const sidebars = {
  tutorialSidebar: [
    {
      type: 'category',
      label: 'Module 1: ROS 2',
      items: [
        'module1/chapter1',
        'module1/chapter2',
      ],
    },
    // ...more modules
  ],
};
```

**Testing Checklist**:
- [ ] Sidebar text reads left-to-right horizontally
- [ ] Module labels are horizontal
- [ ] Chapter titles are horizontal
- [ ] Sidebar collapsible sections work
- [ ] Active page highlight shows correctly
- [ ] Mobile sidebar (< 996px) displays correctly

---

### Task Group 5: Content Buttons

**Files to create/modify**:
- `frontend/src/components/ContentButtons/index.tsx` (NEW)
- `frontend/src/components/ContentButtons/styles.module.css` (NEW)
- `frontend/src/theme/DocItem/Layout/index.tsx` (SWIZZLE)

**Phase 5A: Create ContentButtons Component**

```bash
# 1. Create component directory
mkdir -p frontend/src/components/ContentButtons

# 2. Create component file
```

```tsx
// frontend/src/components/ContentButtons/index.tsx
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
```

```css
/* frontend/src/components/ContentButtons/styles.module.css */
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
  font-size: 14px;
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

@media (max-width: 767px) {
  .contentButtons {
    flex-direction: column;
    gap: 12px;
  }

  .personalizedModeBtn,
  .languageToggleBtn {
    width: 100%;
    justify-content: center;
  }
}
```

**Phase 5B: Swizzle DocItem Layout**

```bash
# 1. Run swizzle command
cd frontend
npm run swizzle @docusaurus/theme-classic DocItem/Layout -- --wrap

# This creates: frontend/src/theme/DocItem/Layout/index.tsx
```

```tsx
// frontend/src/theme/DocItem/Layout/index.tsx
/**
 * Swizzled Component: DocItem/Layout (WRAP mode)
 * Purpose: Inject ContentButtons above doc content (FR-019, FR-020)
 * Original: @docusaurus/theme-classic/src/theme/DocItem/Layout
 * Swizzled: 2025-12-16
 * Feature: 002-fix-ui-theme
 */
import React from 'react';
import Layout from '@theme-original/DocItem/Layout';
import type LayoutType from '@theme/DocItem/Layout';
import type {WrapperProps} from '@docusaurus/types';
import ContentButtons from '@site/src/components/ContentButtons';

type Props = WrapperProps<typeof LayoutType>;

export default function LayoutWrapper(props: Props): JSX.Element {
  return (
    <>
      <Layout {...props}>
        <ContentButtons />
        {props.children}
      </Layout>
    </>
  );
}
```

**Testing Checklist**:
- [ ] Buttons appear on ALL `/docs/*` pages
- [ ] Buttons do NOT appear on landing page (`/`)
- [ ] Buttons positioned above main content
- [ ] 2 buttons side-by-side on desktop
- [ ] 2 buttons stacked on mobile
- [ ] Hover effects work (scale + glow)
- [ ] No console errors or warnings
- [ ] Build succeeds: `npm run build`

---

## Testing & Verification

### Manual Testing Checklist

**Logo (FR-001, FR-002)**:
- [ ] PNG logo displays in navbar
- [ ] Transparent background visible
- [ ] Visible in both themes
- [ ] No pixelation at 40px height

**Navbar (FR-003-009)**:
- [ ] All elements vertically centered
- [ ] Left side unchanged (Modules link)
- [ ] Right side order: Search, Sign In, Sign Up, Theme Toggle
- [ ] GitHub icon removed
- [ ] Responsive on mobile (< 996px)

**Light Theme (FR-011-014)**:
- [ ] Sky blue background (#f0f9ff)
- [ ] Dark blue text readable
- [ ] Theme toggle works
- [ ] Persists on reload
- [ ] Smooth transition (<300ms)
- [ ] WCAG AA contrast ratios met

**Sidebar (FR-015-018)**:
- [ ] Text reads horizontally
- [ ] Navigation hierarchy preserved
- [ ] Collapsible sections work
- [ ] Active state visible
- [ ] Mobile sidebar functional

**Content Buttons (FR-019-022)**:
- [ ] Exactly 2 buttons
- [ ] Appear on all docs pages
- [ ] Above main content
- [ ] Do not break layout
- [ ] Hover effects smooth

### Cross-Browser Testing

```bash
# Test in:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

# Viewports:
- Desktop: 1920x1080, 1366x768
- Tablet: 768x1024 (iPad)
- Mobile: 375x667 (iPhone), 360x640 (Android)
```

### Build Verification

```bash
# Production build
npm run build

# Check bundle size
du -sh build/assets/css/*.css

# Serve production build
npm run serve

# Open http://localhost:3000
# Verify all features work in production mode
```

---

## Troubleshooting

### Issue: Logo not displaying

**Symptom**: Navbar shows broken image or alt text

**Solutions**:
```bash
# 1. Verify file exists
ls frontend/static/img/robobook-logo.png

# 2. Check path in config (should NOT start with /)
# Correct: src: 'img/robobook-logo.png'
# Wrong: src: '/img/robobook-logo.png'

# 3. Clear build cache
rm -rf frontend/.docusaurus
npm start
```

### Issue: Light theme not applying

**Symptom**: Light theme looks same as dark or unstyled

**Solutions**:
```bash
# 1. Verify CSS syntax (no typos in selectors)
# Check: [data-theme='light'] not [data-theme="light"]

# 2. Check browser localStorage
# Open DevTools → Application → Local Storage
# Key should be: theme
# Value should be: light

# 3. Force theme reload
localStorage.setItem('theme', 'light');
location.reload();
```

### Issue: Sidebar text still vertical

**Symptom**: Sidebar links unreadable, text rotated 90°

**Solutions**:
```bash
# 1. Inspect computed styles
# DevTools → Elements → Select .menu__link
# Check: writing-mode, transform, flex-direction

# 2. Add CSS override with !important
.menu__link {
  writing-mode: horizontal-tb !important;
  transform: none !important;
}

# 3. Check for conflicting plugins
npm list | grep docusaurus
# Disable third-party plugins one by one
```

### Issue: Content buttons not appearing

**Symptom**: Docs pages load without buttons above content

**Solutions**:
```bash
# 1. Verify swizzle succeeded
ls frontend/src/theme/DocItem/Layout/index.tsx
# File should exist

# 2. Check import path
# Should be: @site/src/components/ContentButtons
# NOT: ../../../components/ContentButtons

# 3. Rebuild with verbose output
npm run build -- --debug

# 4. Check browser console for errors
# Open DevTools → Console
# Look for import/module errors
```

### Issue: Build fails after swizzling

**Symptom**: `npm run build` errors with TypeScript issues

**Solutions**:
```bash
# 1. Verify TypeScript types
npm install --save-dev @types/react

# 2. Check tsconfig.json includes theme directory
# Should have: "include": ["src/**/*"]

# 3. Use JavaScript instead (rename .tsx → .js, remove types)
mv frontend/src/theme/DocItem/Layout/index.tsx \
   frontend/src/theme/DocItem/Layout/index.js

# 4. Clear TypeScript cache
rm -rf frontend/.docusaurus/
rm -rf frontend/build/
npm run build
```

---

## Git Workflow

```bash
# 1. Stage changes
git add frontend/docusaurus.config.ts
git add frontend/src/css/
git add frontend/src/components/ContentButtons/
git add frontend/src/theme/

# 2. Commit with descriptive message
git commit -m "feat(ui): Fix 5 UI/theme issues

- Update logo to PNG with transparency (FR-001, FR-002)
- Reorganize navbar with auth icons (FR-003-009)
- Implement light theme CSS (FR-011-014)
- Fix sidebar vertical text (FR-015-018)
- Add content buttons via swizzling (FR-019-022)

Includes:
- docusaurus.config.ts updates
- Light theme CSS variables
- ContentButtons React component
- Swizzled DocItem/Layout (wrap mode)

Testing: Manual verification on Chrome/Firefox/Safari
Verified: WCAG AA contrast, responsive design, build success"

# 3. Push to feature branch
git push origin 002-fix-ui-theme
```

---

## Next Steps

After completing all 5 task groups:

1. **Manual QA**: Test all acceptance criteria from spec.md
2. **Cross-browser testing**: Chrome, Firefox, Safari, Edge
3. **Responsive testing**: Desktop, tablet, mobile viewports
4. **Performance check**: Lighthouse audit (score > 90)
5. **Create PR**: Use `/sp.git.commit_pr` command
6. **Demo**: Record 90-second video showing all 5 fixes

---

## Resources

- **Docusaurus Docs**: https://docusaurus.io/docs
- **Swizzling Guide**: https://docusaurus.io/docs/swizzling
- **Theme Configuration**: https://docusaurus.io/docs/api/themes/configuration
- **WCAG Contrast Checker**: https://webaim.org/resources/contrastchecker/
- **robobook-docusaurus-ui Skill**: `.claude/skills/robobook-docusaurus-ui/SKILL.md`

---

**Estimated Completion Time**: 4-6 hours
- Task Group 1 (Logo): 15 minutes
- Task Group 2 (Navbar): 45 minutes
- Task Group 3 (Light Theme): 60 minutes
- Task Group 4 (Sidebar): 30 minutes
- Task Group 5 (Content Buttons): 90 minutes
- Testing & QA: 60-90 minutes
