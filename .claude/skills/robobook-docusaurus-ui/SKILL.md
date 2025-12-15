---
name: "robobook-docusaurus-ui"
description: "Design and build RoboBook's visual identity in Docusaurus: dark navy backgrounds (#0f1729, #1a1f3a), bright cyan accents (#00d4ff, #0ea5e9), glassmorphism cards, custom navbar styling, hero sections, button designs, hover effects with shimmer/glow animations, and typography. Focuses ONLY on CSS styling, component appearance, and visual polish. Use when user wants RoboBook look, custom theme colors, or UI/UX improvements. Does NOT handle architecture, plugins, or build configuration."
version: "1.0.0"
---

# RoboBook Docusaurus UI Skill

## When to Use This Skill

- User wants RoboBook visual design applied to Docusaurus
- User asks for dark theme with cyan/blue accents
- User requests custom styling, hover effects, or UI polish
- User mentions "make it look professional" or "apply RoboBook theme"
- User needs CSS customization or component styling
- **Does NOT handle**: Architecture, plugins, build config, or file structure

## Color Palette (CRITICAL - Always Use These)

### Background Colors
- **Primary Dark**: `#0f1729` - Main background
- **Secondary Dark**: `#1a1f3a` - Cards and sections
- **Accent Dark**: `#2d3454` - Hover states and borders

### Accent Colors
- **Primary Cyan**: `#00d4ff` - Main accent (headings, icons, buttons)
- **Secondary Blue**: `#0ea5e9` - Links and secondary accents
- **Bright Cyan**: `#22d3ee` - Hover effects and shimmer

### Text Colors
- **Primary Text**: `#ffffff` - Main headings
- **Secondary Text**: `#e5e7eb` - Body text
- **Muted Text**: `#9ca3af` - Descriptions

## Design Principles

1. **High Contrast**: White text on dark backgrounds - always readable
2. **Glassmorphism**: Subtle borders, backdrop blur effects on cards
3. **Cyan Accents**: Use cyan/blue for all interactive elements
4. **Smooth Animations**: All hover effects should be smooth with transitions
5. **Clean Typography**: Large, bold headings with generous spacing
6. **Modern Layout**: Grid-based, responsive, spacious sections

## Interactive Elements & Hover Effects (CRITICAL)

### Hover Effect Requirements
Every interactive section MUST include:

1. **Smooth Enlargement**: Scale transformation on hover
2. **Shimmer/Glow Animation**: Cyan glow effect around borders
3. **Pointer Cursor**: Show `cursor: pointer` for clickable elements
4. **Smooth Transitions**: All animations should be smooth (0.3s ease)

### CSS Implementation for Hover Effects

```css
/* Card Hover Effect - REQUIRED for all cards */
.feature-card,
.doc-card,
.blog-card {
  background: #1a1f3a;
  border: 1px solid rgba(45, 52, 84, 0.5);
  border-radius: 16px;
  padding: 2rem;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

/* Hover State - Enlarge + Glow */
.feature-card:hover,
.doc-card:hover,
.blog-card:hover {
  transform: scale(1.05) translateY(-8px);
  border-color: #00d4ff;
  box-shadow: 0 0 30px rgba(0, 212, 255, 0.4),
              0 0 60px rgba(0, 212, 255, 0.2);
}

/* Shimmer Animation Effect */
.feature-card::before,
.doc-card::before,
.blog-card::before {
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

.feature-card:hover::before,
.doc-card:hover::before,
.blog-card:hover::before {
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%) translateY(-100%) rotate(45deg);
  }
  100% {
    transform: translateX(100%) translateY(100%) rotate(45deg);
  }
}

/* Button Hover Effects */
.btn-primary {
  background: linear-gradient(135deg, #00d4ff 0%, #0ea5e9 100%);
  color: white;
  padding: 0.75rem 2rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.btn-primary:hover {
  transform: scale(1.08);
  box-shadow: 0 0 25px rgba(0, 212, 255, 0.6);
}

.btn-secondary {
  background: transparent;
  color: #00d4ff;
  border: 2px solid #00d4ff;
  padding: 0.75rem 2rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background: rgba(0, 212, 255, 0.1);
  transform: scale(1.05);
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
}

/* Link Hover Effects */
a {
  color: #00d4ff;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

a:hover {
  color: #22d3ee;
  text-shadow: 0 0 8px rgba(0, 212, 255, 0.5);
}

a::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0%;
  height: 2px;
  background: #00d4ff;
  transition: width 0.3s ease;
}

a:hover::after {
  width: 100%;
}
```

## Component Styling Guide

### Navigation Bar
```css
.navbar {
  background: rgba(15, 23, 41, 0.9);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 212, 255, 0.1);
  padding: 1rem 2rem;
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-logo {
  cursor: pointer;
  transition: transform 0.3s ease;
}

.navbar-logo:hover {
  transform: scale(1.1);
}

.navbar-link {
  color: #e5e7eb;
  cursor: pointer;
  transition: all 0.3s ease;
}

.navbar-link:hover {
  color: #00d4ff;
  text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
}
```

### Hero Section
```css
.hero-section {
  background: linear-gradient(180deg, #0f1729 0%, #1a1f3a 100%);
  padding: 5rem 2rem;
  text-align: center;
}

.hero-badge {
  display: inline-block;
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid #00d4ff;
  color: #00d4ff;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.875rem;
  margin-bottom: 1rem;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
  }
  50% {
    box-shadow: 0 0 20px rgba(0, 212, 255, 0.6);
  }
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 1rem;
}

.hero-title .highlight {
  color: #00d4ff;
  text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
}

.hero-description {
  font-size: 1.25rem;
  color: #9ca3af;
  max-width: 700px;
  margin: 0 auto 2rem;
}
```

### Content Cards
```css
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  padding: 4rem 2rem;
}

.feature-card-icon {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #00d4ff 0%, #0ea5e9 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
  transition: all 0.3s ease;
}

.feature-card:hover .feature-card-icon {
  transform: scale(1.15) rotate(5deg);
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.6);
}

.feature-card-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: white;
  margin-bottom: 0.75rem;
}

.feature-card-description {
  font-size: 1rem;
  color: #9ca3af;
  line-height: 1.6;
}
```

### Footer/CTA Section
```css
.cta-section {
  background: linear-gradient(135deg, #2d3454 0%, #1a1f3a 100%);
  padding: 5rem 2rem;
  text-align: center;
  margin-top: 4rem;
}

.cta-badge {
  display: inline-block;
  background: rgba(0, 212, 255, 0.15);
  border: 1px solid #00d4ff;
  color: #00d4ff;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}
```

## Docusaurus-Specific CSS Overrides

### Custom CSS File (src/css/custom.css)
```css
/* Override ALL Docusaurus defaults with RoboBook theme */
:root {
  --ifm-color-primary: #00d4ff;
  --ifm-color-primary-dark: #00bfe6;
  --ifm-color-primary-darker: #00b3d9;
  --ifm-color-primary-darkest: #0094b3;
  --ifm-color-primary-light: #1addff;
  --ifm-color-primary-lighter: #2de0ff;
  --ifm-color-primary-lightest: #52e6ff;
  
  --ifm-background-color: #0f1729;
  --ifm-navbar-background-color: rgba(15, 23, 41, 0.9);
  --ifm-footer-background-color: #1a1f3a;
  
  --ifm-font-color-base: #ffffff;
  --ifm-heading-color: #ffffff;
  --ifm-link-color: #00d4ff;
  --ifm-link-hover-color: #22d3ee;
  
  --ifm-code-background: #1a1f3a;
  --ifm-blockquote-border-left-color: #00d4ff;
}

/* Dark mode overrides */
[data-theme='dark'] {
  --ifm-background-color: #0f1729;
  --ifm-background-surface-color: #1a1f3a;
}

/* Sidebar styling */
.menu__link {
  color: #e5e7eb;
  cursor: pointer;
  transition: all 0.2s ease;
}

.menu__link:hover {
  background: rgba(0, 212, 255, 0.1);
  color: #00d4ff;
}

.menu__link--active {
  background: rgba(0, 212, 255, 0.2);
  color: #00d4ff;
  border-left: 3px solid #00d4ff;
}

/* Table of Contents (TOC) */
.table-of-contents__link {
  color: #9ca3af;
  cursor: pointer;
  transition: all 0.2s ease;
}

.table-of-contents__link:hover {
  color: #00d4ff;
}

.table-of-contents__link--active {
  color: #00d4ff;
  font-weight: 600;
}

/* Documentation content */
.markdown {
  color: #e5e7eb;
}

.markdown h1,
.markdown h2,
.markdown h3 {
  color: white;
  border-bottom: 1px solid rgba(0, 212, 255, 0.2);
  padding-bottom: 0.5rem;
}

.markdown code {
  background: #1a1f3a;
  color: #00d4ff;
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 4px;
  padding: 0.2rem 0.4rem;
}

/* Code blocks */
.prism-code {
  background: #1a1f3a !important;
  border: 1px solid rgba(45, 52, 84, 0.5);
  border-radius: 8px;
}
```

## Critical Rules for UI Skill

- ✅ ALWAYS use the exact color codes provided above
- ✅ ALL interactive elements MUST have hover effects with:
  - Smooth scale transformation
  - Cyan glow/shimmer animation
  - `cursor: pointer`
- ✅ White text must be clearly visible on dark backgrounds
- ✅ All transitions should be smooth (0.3s ease)
- ✅ Cards must enlarge and glow on hover
- ✅ Buttons must scale and glow on hover
- ✅ Links must show underline animation on hover
- ✅ Include hover effects on all clickable elements
- ✅ Use large, bold typography for headings
- ✅ Maintain consistent spacing
- ❌ NEVER remove hover effects from interactive elements
- ❌ NEVER use light backgrounds - always dark navy/black
- ❌ NEVER use colors outside the palette
- ❌ NEVER create static elements without hover feedback

## Responsive Design

```css
/* Mobile breakpoints */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .feature-card {
    padding: 1.5rem;
  }
}

/* Tablet breakpoints */
@media (max-width: 1024px) {
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
```

## Quality Checklist for UI

Before delivering, verify:
- [ ] All backgrounds use #0f1729 or #1a1f3a
- [ ] All accents use #00d4ff or #0ea5e9
- [ ] White text is clearly visible everywhere
- [ ] **ALL cards have hover effects (scale + glow + shimmer)**
- [ ] **ALL buttons have hover effects (scale + glow)**
- [ ] **ALL links have hover effects (color + underline animation)**
- [ ] **cursor: pointer on all clickable elements**
- [ ] CTAs are prominent with cyan backgrounds
- [ ] Layout is responsive (mobile-friendly)
- [ ] Icons use cyan color
- [ ] Spacing feels generous and modern
- [ ] All transitions are smooth (no jarring animations)

## Notes

This skill focuses PURELY on visual design and CSS styling. It does NOT handle:
- Docusaurus configuration
- File structure setup
- Plugin installation
- Build processes
- Architecture decisions

For those tasks, use the **robobook-docusaurus-architect** skill.

**Default Docusaurus Panels** (Keep as-is, just style them):
- Left panel → Docs navigation (style with cyan accents)
- Right panel → TOC / section headings (style with hover effects)