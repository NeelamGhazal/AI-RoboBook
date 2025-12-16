---
name: "robobook-docusaurus-ui"
description: "Design and build RoboBook's visual identity in Docusaurus with Tech Cyber theme (modern cyan/blue). Includes light mode (sky blue backgrounds) and dark mode (dark navy backgrounds), glassmorphism cards, custom navbar styling, hero sections, button designs, hover effects with shimmer/glow animations, and typography. Focuses ONLY on CSS styling, component appearance, and visual polish. Use when user wants RoboBook look, custom theme colors, or UI/UX improvements. Does NOT handle architecture, plugins, or build configuration."
version: "3.0.0"
---

# RoboBook Docusaurus UI Skill

## When to Use This Skill

- User wants RoboBook visual design applied to Docusaurus
- User asks for Tech Cyber theme styling
- User requests custom styling, hover effects, or UI polish
- User mentions "make it look professional" or "apply RoboBook theme"
- User needs CSS customization or component styling
- **Does NOT handle**: Architecture, plugins, build config, or file structure

---

## 🎨 Theme: Tech Cyber

**Colors**: 
- **Light Mode**: Sky blue (`#f0f9ff`) with cyan accents (`#0284c7`)
- **Dark Mode**: Dark navy (`#0f1729`) with bright cyan accents (`#00d4ff`)

**Vibe**: Modern, futuristic, high-tech  
**Best for**: Tech-forward, cutting-edge digital aesthetic

---

## 🚀 Tech Cyber Theme

### Color Palette

#### Light Mode Colors
**Background Colors**
- **Primary Background**: `#f0f9ff` - Sky blue, fresh and modern
- **Secondary Background**: `#e0f2fe` - Light cyan sections
- **Card Background**: `#ffffff` - Pure white for cards and navbar

**Primary Colors**
- **Primary Cyan**: `#0284c7` - Main accent (headings, icons, buttons)
- **Secondary Blue**: `#0369a1` - Secondary accents and links
- **Bright Cyan**: `#06b6d4` - Hover effects and shimmer

**Text Colors**
- **Primary Text**: `#0c4a6e` - Dark blue for headings
- **Secondary Text**: `#0e7490` - Medium blue for body text
- **Muted Text**: `#64748b` - Gray blue for descriptions

**Border & UI Elements**
- **Border**: `#bae6fd` - Light cyan borders
- **Hover Glow**: `rgba(2, 132, 199, 0.3)` - Cyan glow effect

#### Dark Mode Colors
**Background Colors**
- **Primary Background**: `#0f1729` - Deep navy background
- **Secondary Background**: `#1a1f3a` - Dark sections
- **Card Background**: `#1a1f3a` - Dark cards with subtle depth

**Primary Colors**
- **Primary Cyan**: `#00d4ff` - Bright cyan accent
- **Secondary Blue**: `#0ea5e9` - Secondary cyan
- **Bright Cyan**: `#22d3ee` - Hover effects and shimmer

**Text Colors**
- **Primary Text**: `#ffffff` - Pure white for headings
- **Secondary Text**: `#e5e7eb` - Light gray for body text
- **Muted Text**: `#9ca3af` - Muted gray for descriptions

**Border & UI Elements**
- **Border**: `rgba(45, 52, 84, 0.5)` - Dark subtle borders
- **Hover Glow**: `rgba(0, 212, 255, 0.4)` - Cyan glow effect

### Design Principles
1. **High Contrast**: Clear text readability on all backgrounds (light & dark)
2. **Glassmorphism**: Subtle borders, backdrop blur effects on cards
3. **Cyan Accents**: Use cyan/blue for all interactive elements
4. **Smooth Animations**: All hover effects should be smooth with transitions
5. **Clean Typography**: Large, bold headings with generous spacing
6. **Modern Layout**: Grid-based, responsive, spacious sections
7. **Futuristic Feel**: Glowing effects and shimmer animations

### CSS Variables Setup
```css
/* Tech Cyber Theme - CSS Variables */
:root {
  /* Light Mode (Default) */
  --bg-primary: #f0f9ff;
  --bg-secondary: #e0f2fe;
  --card-bg: #ffffff;
  
  --primary-cyan: #0284c7;
  --secondary-blue: #0369a1;
  --bright-cyan: #06b6d4;
  
  --text-primary: #0c4a6e;
  --text-secondary: #0e7490;
  --text-muted: #64748b;
  
  --border-color: #bae6fd;
  --hover-glow: rgba(2, 132, 199, 0.3);
  
  /* Docusaurus Overrides (Light) */
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
}

/* Dark Mode Overrides */
[data-theme='dark'] {
  --bg-primary: #0f1729;
  --bg-secondary: #1a1f3a;
  --card-bg: #1a1f3a;
  
  --primary-cyan: #00d4ff;
  --secondary-blue: #0ea5e9;
  --bright-cyan: #22d3ee;
  
  --text-primary: #ffffff;
  --text-secondary: #e5e7eb;
  --text-muted: #9ca3af;
  
  --border-color: rgba(45, 52, 84, 0.5);
  --hover-glow: rgba(0, 212, 255, 0.4);
  
  /* Docusaurus Overrides (Dark) */
  --ifm-color-primary: #00d4ff;
  --ifm-color-primary-dark: #00bfe6;
  --ifm-color-primary-darker: #00b3d9;
  --ifm-color-primary-darkest: #0094b3;
  --ifm-color-primary-light: #1addff;
  --ifm-color-primary-lighter: #2de0ff;
  --ifm-color-primary-lightest: #52e6ff;
  
  --ifm-background-color: #0f1729;
  --ifm-background-surface-color: #1a1f3a;
  --ifm-navbar-background-color: rgba(15, 23, 41, 0.9);
  --ifm-footer-background-color: #1a1f3a;
  
  --ifm-font-color-base: #ffffff;
  --ifm-heading-color: #ffffff;
  --ifm-link-color: #00d4ff;
  --ifm-link-hover-color: #22d3ee;
  
  --ifm-code-background: #1a1f3a;
  --ifm-blockquote-border-left-color: #00d4ff;
}
```

---

## 🎯 Interactive Elements & Hover Effects (CRITICAL)

### Hover Effect Requirements
Every interactive section MUST include:

1. **Smooth Enlargement**: Scale transformation on hover
2. **Shimmer/Glow Animation**: Colored glow effect around borders
3. **Pointer Cursor**: Show `cursor: pointer` for clickable elements
4. **Smooth Transitions**: All animations should be smooth (0.3s ease)

### CSS Implementation for Hover Effects

```css
/* Card Hover Effect - REQUIRED for all cards */
.feature-card,
.doc-card,
.blog-card {
  background: var(--card-bg);
  border: 2px solid var(--border-color);
  border-radius: 16px;
  padding: 2.5rem;
  cursor: pointer;
  transition: all 0.4s ease;
  position: relative;
  overflow: hidden;
}

/* Hover State - Enlarge + Glow */
.feature-card:hover,
.doc-card:hover,
.blog-card:hover {
  transform: translateY(-12px) scale(1.02);
  border-color: var(--primary-cyan);
  box-shadow: 0 20px 60px var(--hover-glow);
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
    rgba(2, 132, 199, 0.1) 50%,
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

/* Dark Mode Shimmer */
[data-theme='dark'] .feature-card::before,
[data-theme='dark'] .doc-card::before,
[data-theme='dark'] .blog-card::before {
  background: linear-gradient(
    45deg,
    transparent 30%,
    rgba(0, 212, 255, 0.1) 50%,
    transparent 70%
  );
}

/* Button Hover Effects */
.btn-primary {
  background: linear-gradient(135deg, var(--primary-cyan) 0%, var(--secondary-blue) 100%);
  color: white;
  padding: 1.1rem 2.8rem;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.4s ease;
  border: none;
  font-weight: 700;
  box-shadow: 0 8px 25px var(--hover-glow);
}

.btn-primary:hover {
  transform: translateY(-4px) scale(1.05);
  box-shadow: 0 15px 45px var(--hover-glow);
}

.btn-secondary {
  background: transparent;
  color: var(--primary-cyan);
  border: 2px solid var(--primary-cyan);
  padding: 11px 22px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
}

.btn-secondary:hover {
  background: rgba(2, 132, 199, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px var(--hover-glow);
}

/* Dark Mode Button Hover */
[data-theme='dark'] .btn-secondary:hover {
  background: rgba(0, 212, 255, 0.1);
}

/* Link Hover Effects */
a {
  color: var(--primary-cyan);
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

a:hover {
  color: var(--secondary-blue);
  text-shadow: 0 0 8px var(--hover-glow);
}

a::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0%;
  height: 2px;
  background: var(--primary-cyan);
  transition: width 0.3s ease;
}

a:hover::after {
  width: 100%;
}
```

---

## 🧩 Component Styling Guide

### Navigation Bar
```css
.navbar {
  background: var(--card-bg);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border-color);
  padding: 1rem 2rem;
  transition: all 0.3s ease;
}

.navbar__logo:hover {
  transform: scale(1.1);
}

.navbar__link {
  color: var(--text-primary);
  transition: all 0.3s ease;
}

.navbar__link:hover {
  color: var(--primary-cyan);
  text-shadow: 0 0 10px var(--hover-glow);
}
```

### Hero Section
```css
.hero-section {
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
  padding: 6rem 2rem;
  transition: all 0.4s ease;
}

.hero-badge {
  display: inline-block;
  background: rgba(2, 132, 199, 0.15);
  border: 2px solid var(--primary-cyan);
  color: var(--primary-cyan);
  padding: 8px 18px;
  border-radius: 30px;
  font-size: 0.85rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.hero-title {
  font-size: 3.8rem;
  font-weight: 900;
  line-height: 1.15;
  margin-bottom: 1.8rem;
  background: linear-gradient(135deg, var(--primary-cyan), var(--secondary-blue));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -1px;
}

.hero-description {
  font-size: 1.3rem;
  color: var(--text-secondary);
  line-height: 1.8;
  margin-bottom: 3rem;
  font-weight: 400;
}
```

### Feature Cards Section
```css
.features-section {
  padding: 7rem 2rem;
  background: var(--bg-secondary);
  transition: all 0.4s ease;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

.feature-card-icon {
  width: 70px;
  height: 70px;
  border-radius: 16px;
  background: linear-gradient(135deg, var(--primary-cyan), var(--secondary-blue));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 2rem;
  transition: all 0.4s ease;
  box-shadow: 0 8px 20px var(--hover-glow);
}

.feature-card:hover .feature-card-icon {
  transform: scale(1.15) rotate(5deg);
  box-shadow: 0 12px 30px var(--hover-glow);
}

.feature-card-title {
  font-size: 1.6rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: var(--text-primary);
}

.feature-card-description {
  font-size: 1.05rem;
  color: var(--text-secondary);
  line-height: 1.75;
}
```

### CTA Section
```css
.cta-section {
  padding: 7rem 2rem;
  background: linear-gradient(135deg, rgba(2, 132, 199, 0.12), rgba(6, 182, 212, 0.12));
  text-align: center;
  transition: all 0.4s ease;
  border-top: 2px solid var(--border-color);
  border-bottom: 2px solid var(--border-color);
}

.cta-badge {
  display: inline-block;
  background: rgba(2, 132, 199, 0.2);
  border: 2px solid var(--primary-cyan);
  color: var(--primary-cyan);
  padding: 10px 24px;
  border-radius: 30px;
  font-size: 0.9rem;
  font-weight: 700;
  margin-bottom: 2rem;
  text-transform: uppercase;
  letter-spacing: 1.5px;
}

.cta-title {
  font-size: 3.2rem;
  font-weight: 900;
  margin-bottom: 1.8rem;
  color: var(--text-primary);
  letter-spacing: -0.5px;
}
```

### Footer
```css
.footer {
  background: var(--card-bg);
  border-top: 2px solid var(--border-color);
  padding: 4rem 2rem 2rem;
  transition: all 0.4s ease;
}

.footer__title {
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 1.2rem;
  color: var(--text-primary);
}

.footer__link-item {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 1rem;
  transition: all 0.3s ease;
  display: inline-block;
}

.footer__link-item:hover {
  color: var(--primary-cyan);
  padding-left: 8px;
}
```

---

## 📄 Docusaurus-Specific CSS Overrides

### Custom CSS File (src/css/custom.css)
```css
/* ============================================
   RoboBook Tech Cyber Theme
   ============================================ */

/* CSS Variables - Tech Cyber Theme */
:root {
  /* Light Mode Colors */
  --bg-primary: #f0f9ff;
  --bg-secondary: #e0f2fe;
  --card-bg: #ffffff;
  
  --primary-cyan: #0284c7;
  --secondary-blue: #0369a1;
  --bright-cyan: #06b6d4;
  
  --text-primary: #0c4a6e;
  --text-secondary: #0e7490;
  --text-muted: #64748b;
  
  --border-color: #bae6fd;
  --hover-glow: rgba(2, 132, 199, 0.3);
  
  /* Docusaurus Overrides */
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
}

/* Dark Mode Overrides */
[data-theme='dark'] {
  --bg-primary: #0f1729;
  --bg-secondary: #1a1f3a;
  --card-bg: #1a1f3a;
  
  --primary-cyan: #00d4ff;
  --secondary-blue: #0ea5e9;
  --bright-cyan: #22d3ee;
  
  --text-primary: #ffffff;
  --text-secondary: #e5e7eb;
  --text-muted: #9ca3af;
  
  --border-color: rgba(45, 52, 84, 0.5);
  --hover-glow: rgba(0, 212, 255, 0.4);
  
  /* Docusaurus Dark Overrides */
  --ifm-color-primary: #00d4ff;
  --ifm-color-primary-dark: #00bfe6;
  --ifm-color-primary-darker: #00b3d9;
  --ifm-color-primary-darkest: #0094b3;
  --ifm-color-primary-light: #1addff;
  --ifm-color-primary-lighter: #2de0ff;
  --ifm-color-primary-lightest: #52e6ff;
  
  --ifm-background-color: #0f1729;
  --ifm-background-surface-color: #1a1f3a;
  --ifm-navbar-background-color: rgba(15, 23, 41, 0.9);
  --ifm-footer-background-color: #1a1f3a;
  
  --ifm-font-color-base: #ffffff;
  --ifm-heading-color: #ffffff;
  --ifm-link-color: #00d4ff;
  --ifm-link-hover-color: #22d3ee;
  
  --ifm-code-background: #1a1f3a;
  --ifm-blockquote-border-left-color: #00d4ff;
}

/* Global Styles */
* {
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Sidebar styling */
.menu__link {
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 6px;
}

.menu__link:hover {
  background: rgba(2, 132, 199, 0.15);
  color: var(--primary-cyan);
}

.menu__link--active {
  background: rgba(2, 132, 199, 0.15);
  color: var(--primary-cyan);
  border-left: 3px solid var(--primary-cyan);
  font-weight: 600;
}

/* Table of Contents (TOC) */
.table-of-contents__link {
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.table-of-contents__link:hover {
  color: var(--primary-cyan);
}

.table-of-contents__link--active {
  color: var(--primary-cyan);
  font-weight: 600;
}

/* Documentation content */
.markdown {
  color: var(--text-primary);
}

.markdown h1,
.markdown h2,
.markdown h3 {
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0.5rem;
}

.markdown code {
  background: var(--bg-secondary);
  color: var(--primary-cyan);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 0.2rem 0.4rem;
}

/* Code blocks */
.prism-code {
  background: var(--bg-secondary) !important;
  border: 1px solid var(--border-color);
  border-radius: 8px;
}
```

---

## 📱 Responsive Design
```css
/* Mobile breakpoints */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-grid {
    grid-template-columns: 1fr;
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
  
  .hero-grid {
    gap: 3rem;
  }
}
```

---

## ✅ Quality Checklist for UI

### Light Mode
- [ ] Light mode uses sky blue backgrounds (`#f0f9ff`)
- [ ] Text is clearly visible in light mode (dark blue text)
- [ ] All hover effects work in light mode
- [ ] Cards use white backgrounds (`#ffffff`)

### Dark Mode
- [ ] Dark mode uses navy backgrounds (`#0f1729`)
- [ ] Text is clearly visible in dark mode (white text)
- [ ] All hover effects work in dark mode
- [ ] Cards use dark backgrounds (`#1a1f3a`)

### Universal Requirements
- [ ] **ALL cards have hover effects (scale + glow + shimmer)**
- [ ] **ALL buttons have hover effects (scale + glow)**
- [ ] **ALL links have hover effects (color + underline animation)**
- [ ] **cursor: pointer on all clickable elements**
- [ ] Transitions are smooth (0.3-0.4s)
- [ ] Cyan glow effects visible on hover
- [ ] All interactive elements have `cursor: pointer`
- [ ] Layout is responsive (mobile-friendly)
- [ ] Spacing feels generous and modern

---

## 🚫 Critical Rules for UI Skill

### Must Do ✅
- ✅ ALWAYS use exact color codes from the palette
- ✅ ALL interactive elements MUST have hover effects
- ✅ Text must be clearly visible in BOTH light and dark modes
- ✅ All transitions should be smooth (0.3-0.4s ease)
- ✅ Cards must enlarge and glow on hover
- ✅ Buttons must scale and glow on hover
- ✅ Links must show underline animation on hover

### Never Do ❌
- ❌ NEVER use colors outside the palette
- ❌ NEVER remove hover effects from interactive elements
- ❌ NEVER create static elements without hover feedback
- ❌ NEVER use poor contrast (text must be readable)

---

## 📝 Notes

This skill focuses PURELY on visual design and CSS styling. It does NOT handle:
- Docusaurus configuration
- File structure setup
- Plugin installation
- Build processes
- Architecture decisions

For those tasks, use the **robobook-docusaurus-architect** skill.

**Default Docusaurus Panels** (Keep as-is, just style them):
- Left panel → Docs navigation (style with theme accents)
- Right panel → TOC / section headings (style with hover effects)