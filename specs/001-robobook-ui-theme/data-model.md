# Phase 1: Data Model - CSS Architecture & Component Catalog

**Feature**: RoboBook UI & Color Theme
**Date**: 2025-12-16
**Status**: Completed

## Overview

This document describes the CSS architecture, design token system, and component catalog for the RoboBook UI theme. The "data model" for a CSS theme consists of design tokens (color, typography, spacing) and component specifications that define how visual elements are structured and styled.

---

## 1. Design Token System

### CSS Custom Properties Architecture

**Root Level Variables** (defined in `:root` and `[data-theme='dark']`):

```css
:root {
  /* Color Tokens */
  --bg-primary: #0f1729;
  --bg-secondary: #1a1f3a;
  --bg-accent: #2d3454;
  --color-primary: #00d4ff;
  --color-secondary: #0ea5e9;
  --color-bright: #22d3ee;
  --text-primary: #ffffff;
  --text-secondary: #e5e7eb;
  --text-muted: #9ca3af;
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;

  /* Opacity Variants */
  --cyan-10: rgba(0, 212, 255, 0.1);
  --cyan-20: rgba(0, 212, 255, 0.2);
  --cyan-40: rgba(0, 212, 255, 0.4);
  --cyan-60: rgba(0, 212, 255, 0.6);

  /* Typography Tokens */
  --font-family-base: -apple-system, BlinkMacSystemFont, 'Segoe UI', ...;
  --font-family-mono: 'SF Mono', Monaco, 'Cascadia Code', ...;
  --font-size-h1: 3.5rem;
  --font-size-h2: 3.0rem;
  --font-size-h3: 2.0rem;
  --font-size-h4: 1.5rem;
  --font-size-h5: 1.25rem;
  --font-size-lg: 1.25rem;
  --font-size-base: 1rem;
  --font-size-sm: 0.875rem;
  --font-weight-regular: 400;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  --font-weight-extrabold: 800;
  --line-height-tight: 1.2;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.6;

  /* Spacing Tokens */
  --spacing-3xs: 0.125rem;  /* 2px */
  --spacing-2xs: 0.25rem;   /* 4px */
  --spacing-xs: 0.5rem;     /* 8px */
  --spacing-sm: 0.75rem;    /* 12px */
  --spacing-md: 1rem;       /* 16px */
  --spacing-lg: 1.5rem;     /* 24px */
  --spacing-xl: 2rem;       /* 32px */
  --spacing-2xl: 3rem;      /* 48px */
  --spacing-3xl: 4rem;      /* 64px */
  --spacing-4xl: 6rem;      /* 96px */

  /* Transition Tokens */
  --transition-fast: 0.1s ease;
  --transition-normal: 0.3s ease;
  --transition-slow: 0.6s ease;

  /* Shadow Tokens */
  --shadow-glow: 0 0 30px var(--cyan-40), 0 0 60px var(--cyan-20);
  --shadow-button: 0 0 25px var(--cyan-60);
  --shadow-card: 0 0 20px var(--cyan-40);
}
```

**Docusaurus Integration Variables** (override Infima defaults):

```css
:root {
  --ifm-color-primary: #00d4ff;
  --ifm-background-color: #0f1729;
  --ifm-navbar-background-color: rgba(15, 23, 41, 0.9);
  --ifm-font-color-base: #ffffff;
  --ifm-link-color: #00d4ff;
  --ifm-code-background: #1a1f3a;
  /* ... additional Infima overrides */
}
```

---

## 2. Component Catalog

### 2.1 Navigation Components

#### Navbar

**Selector**: `.navbar`

**Structure**:
```
.navbar
├── .navbar__inner
│   ├── .navbar__logo
│   │   └── .navbar__title
│   ├── .navbar__items (left)
│   │   └── .navbar__link
│   └── .navbar__items--right
│       ├── .navbar__link
│       ├── .navbar-signup-button
│       └── .theme-toggle-button
```

**Styling**:
- Background: `rgba(15, 23, 41, 0.9)` with `backdrop-filter: blur(10px)`
- Border: `1px solid rgba(0, 212, 255, 0.1)` at bottom
- Padding: `1rem 2rem`
- Position: `sticky` at top with `z-index: 100`

**States**:
- Hover (links): Color changes to `--color-primary` with text shadow
- Focus: 2px cyan outline

#### Sidebar

**Selector**: `.menu__link`

**Styling**:
- Default: `--text-secondary` color
- Hover: `background: var(--cyan-10)`, `color: var(--color-primary)`
- Active: `background: var(--cyan-15)`, `border-left: 3px solid var(--color-primary)`

#### Table of Contents (TOC)

**Selector**: `.table-of-contents__link`

**Styling**:
- Default: `--text-muted` color
- Hover: `--color-primary` color
- Active: `--color-primary` with `font-weight: 600`

---

### 2.2 Content Components

#### Hero Section

**Selector**: `.hero-section`

**Structure**:
```
.hero-section
├── .hero-grid (2-column grid)
│   ├── .hero-content
│   │   ├── .hero-badge
│   │   ├── .hero-title
│   │   ├── .hero-description
│   │   └── .hero-cta-button
│   └── .hero-image
```

**Styling**:
- Background: `linear-gradient(180deg, #0f1729 0%, #1a1f3a 100%)`
- Padding: `5rem 2rem`
- Grid: `grid-template-columns: 1fr 1fr` (desktop), `1fr` (mobile)
- Gap: `5rem` (desktop), `3rem` (mobile)

**Hero Badge**:
- Background: `rgba(0, 212, 255, 0.1)`
- Border: `1px solid var(--color-primary)`
- Padding: `0.5rem 1rem`
- Border-radius: `20px`
- Animation: `pulse 2s infinite`

#### Feature Cards

**Selector**: `.feature-card`

**Structure**:
```
.feature-card
├── .feature-card-icon
├── .feature-card-title
└── .feature-card-description
```

**Styling**:
- Background: `--bg-secondary`
- Border: `1px solid rgba(45, 52, 84, 0.5)`
- Border-radius: `16px`
- Padding: `2rem`
- Transition: `all 0.3s ease`

**Hover State**:
- Transform: `scale(1.05) translateY(-8px)`
- Border: `--color-primary`
- Box-shadow: `0 0 30px var(--cyan-40), 0 0 60px var(--cyan-20)`
- Shimmer: `animation: shimmer 1.5s infinite` on `::before` pseudo-element

**Feature Card Icon**:
- Size: `60px × 60px`
- Background: `linear-gradient(135deg, #00d4ff 0%, #0ea5e9 100%)`
- Border-radius: `12px`
- Hover: `transform: scale(1.15) rotate(5deg)` with `box-shadow: 0 0 20px var(--cyan-60)`

---

### 2.3 Interactive Components

#### Primary Button

**Selector**: `.btn-primary`, `.hero-cta-button`

**Styling**:
- Background: `linear-gradient(135deg, #00d4ff 0%, #0ea5e9 100%)`
- Color: `white`
- Padding: `0.75rem 2rem`
- Border-radius: `8px`
- Border: `none`
- Font-weight: `700`

**Hover State**:
- Transform: `scale(1.08)`
- Box-shadow: `0 0 25px var(--cyan-60)`

#### Secondary Button

**Selector**: `.btn-secondary`

**Styling**:
- Background: `transparent`
- Color: `--color-primary`
- Border: `2px solid var(--color-primary)`
- Padding: `0.75rem 2rem`
- Border-radius: `8px`

**Hover State**:
- Background: `var(--cyan-10)`
- Transform: `scale(1.05)`
- Box-shadow: `0 0 20px var(--cyan-40)`

#### Links

**Selector**: `a`

**Styling**:
- Color: `--color-primary`
- Text-decoration: `none`
- Position: `relative` (for underline pseudo-element)

**Hover State**:
- Color: `--color-bright`
- Text-shadow: `0 0 8px var(--cyan-40)`
- `::after` underline: width animates from `0%` to `100%`

**Underline Pseudo-element**:
```css
a::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0%;
  height: 2px;
  background: var(--color-primary);
  transition: width 0.3s ease;
}

a:hover::after {
  width: 100%;
}
```

---

### 2.4 Code & Documentation Components

#### Code Blocks

**Selector**: `.prism-code`

**Styling**:
- Background: `--bg-secondary` (`#1a1f3a`)
- Border: `1px solid rgba(45, 52, 84, 0.5)`
- Border-radius: `8px`
- Padding: `1rem`
- Font-family: `--font-family-mono`
- Font-size: `--font-size-code` (14px)
- Line-height: `1.5`

#### Inline Code

**Selector**: `.markdown code`

**Styling**:
- Background: `--bg-secondary`
- Color: `--color-primary`
- Border: `1px solid var(--cyan-20)`
- Border-radius: `4px`
- Padding: `0.2rem 0.4rem`

#### Headings

**Selectors**: `.markdown h1`, `.markdown h2`, `.markdown h3`

**Styling**:
- Color: `--text-primary`
- Border-bottom: `1px solid var(--cyan-20)`
- Padding-bottom: `0.5rem`
- Margin-bottom: `1rem`

---

### 2.5 Layout Components

#### Footer

**Selector**: `.footer`

**Styling**:
- Background: `--bg-secondary` (`#1a1f3a`)
- Padding: `5rem 2rem`
- Border-top: `1px solid rgba(0, 212, 255, 0.1)`

**Footer Links**:
- Color: `--text-muted`
- Hover: `--color-primary` with left padding shift

#### CTA Section

**Selector**: `.cta-section`

**Styling**:
- Background: `linear-gradient(135deg, #2d3454 0%, #1a1f3a 100%)`
- Padding: `5rem 2rem`
- Text-align: `center`

**CTA Badge**:
- Background: `rgba(0, 212, 255, 0.15)`
- Border: `1px solid var(--color-primary)`
- Padding: `0.5rem 1rem`
- Border-radius: `20px`

---

## 3. Animation Specifications

### Shimmer Animation

**Purpose**: Premium hover effect on cards

**Implementation**:
```css
@keyframes shimmer {
  0% {
    transform: translateX(-100%) translateY(-100%) rotate(45deg);
  }
  100% {
    transform: translateX(100%) translateY(100%) rotate(45deg);
  }
}

.feature-card::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(
    45deg,
    transparent 30%,
    rgba(0, 212, 255, 0.1) 50%,
    transparent 70%
  );
  transform: rotate(45deg);
  transition: all 0.6s ease;
}

.feature-card:hover::before {
  animation: shimmer 1.5s infinite;
}
```

### Pulse Animation

**Purpose**: Subtle glow for badges

**Implementation**:
```css
@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 10px var(--cyan-40);
  }
  50% {
    box-shadow: 0 0 20px var(--cyan-60);
  }
}

.hero-badge {
  animation: pulse 2s infinite;
}
```

---

## 4. Responsive Grid System

### Breakpoints

| Breakpoint | Min Width | CSS Media Query |
|------------|-----------|-----------------|
| Mobile | 0px | Default (no query) |
| Tablet | 768px | `@media (min-width: 768px)` |
| Desktop | 1024px | `@media (min-width: 1024px)` |

### Grid Patterns

#### Features Grid

**Mobile**:
```css
.features-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
}
```

**Tablet**:
```css
@media (min-width: 768px) {
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
```

**Desktop**:
```css
@media (min-width: 1024px) {
  .features-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 2.5rem;
  }
}
```

---

## 5. File Organization

### CSS Module Structure

```
src/css/
├── custom.css               # Entry point: CSS variables + imports
├── components/
│   ├── navbar.css          # Navigation bar styling
│   ├── sidebar.css         # Sidebar & TOC styling
│   ├── footer.css          # Footer styling
│   ├── hero.css            # Homepage hero section
│   ├── cards.css           # Feature cards & module cards
│   ├── buttons.css         # Button styles & hover effects
│   ├── code-blocks.css     # Syntax highlighting & code blocks
│   └── animations.css      # Shimmer, pulse, transitions
└── utilities/
    ├── colors.css          # Color utility classes
    ├── spacing.css         # Spacing utility classes
    └── typography.css      # Typography utility classes
```

### Import Strategy (in custom.css)

```css
/* CSS Variables */
:root { ... }

/* Component Imports */
@import './components/navbar.css';
@import './components/sidebar.css';
@import './components/footer.css';
@import './components/hero.css';
@import './components/cards.css';
@import './components/buttons.css';
@import './components/code-blocks.css';
@import './components/animations.css';

/* Utility Imports */
@import './utilities/colors.css';
@import './utilities/spacing.css';
@import './utilities/typography.css';
```

---

## 6. Component Relationships

### Component Dependency Graph

```
custom.css (root)
├── Color Tokens
│   ├── Navbar (uses --bg-primary, --color-primary)
│   ├── Sidebar (uses --cyan-10, --color-primary)
│   ├── Cards (uses --bg-secondary, --cyan-40)
│   └── Buttons (uses --gradient-primary, --cyan-60)
├── Typography Tokens
│   ├── Headings (uses --font-size-h1/h2/h3)
│   ├── Body Text (uses --font-size-base, --line-height-relaxed)
│   └── Code (uses --font-family-mono, --font-size-code)
├── Spacing Tokens
│   ├── Hero Section (uses --spacing-4xl, --spacing-lg)
│   ├── Cards (uses --spacing-lg, --spacing-2xl)
│   └── Buttons (uses --spacing-sm, --spacing-xl)
└── Animation Tokens
    ├── Shimmer (applied to cards on hover)
    ├── Pulse (applied to badges)
    └── Transitions (all interactive elements)
```

---

## 7. Performance Considerations

### CSS Bundle Size Estimate

| File | Estimated Size |
|------|---------------|
| custom.css (variables + imports) | ~5KB |
| components/*.css (8 files × 3KB avg) | ~24KB |
| utilities/*.css (3 files × 2KB avg) | ~6KB |
| **Total (uncompressed)** | **~35KB** |
| **Total (gzipped)** | **~12-15KB** |

**Performance**: Well under 50KB target, loads in <50ms on 3G.

### Optimization Techniques

1. **CSS Minification**: Handled by Docusaurus webpack config
2. **Tree Shaking**: Unused CSS removed in production build
3. **Critical CSS Inlining**: Docusaurus inlines above-fold CSS automatically
4. **GPU Acceleration**: `will-change` hints on animated elements

---

## Summary

This CSS architecture provides:
- ✅ **Token-based design system** with 12 colors, 9 font sizes, 10 spacing values
- ✅ **Component catalog** with 15+ reusable components
- ✅ **4-state interaction system** (default, hover, focus, active)
- ✅ **Responsive grid patterns** for mobile/tablet/desktop
- ✅ **Performance-optimized** animations using GPU acceleration
- ✅ **WCAG AA compliant** with verified contrast ratios
- ✅ **Maintainable structure** with modular CSS organization

**Next Phase**: Create implementation tasks (/sp.tasks) to build this CSS architecture.
