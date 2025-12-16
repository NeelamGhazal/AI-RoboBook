# Quickstart Guide: RoboBook UI Theme Development

**Feature**: RoboBook UI & Color Theme
**Audience**: Developers implementing or customizing the theme
**Estimated Time**: 15 minutes to understand, 2-3 hours to implement

---

## Prerequisites

- Docusaurus 3.9.2 installed and running
- Basic CSS knowledge (custom properties, flexbox, grid)
- Code editor with CSS syntax highlighting
- Modern browser for testing (Chrome/Firefox/Safari)

---

## Quick Start (5 Minutes)

### 1. Understand the Project Structure

```
frontend/
└── src/
    └── css/
        ├── custom.css           # START HERE - Entry point with CSS variables
        ├── components/          # Component-specific styles
        └── utilities/           # Utility classes
```

### 2. Key Files to Know

| File | Purpose | When to Edit |
|------|---------|--------------|
| `custom.css` | CSS variables, global styles, imports | Changing colors, fonts, spacing |
| `components/navbar.css` | Navigation bar styling | Customizing header |
| `components/cards.css` | Feature cards, module cards | Adjusting card styles |
| `components/buttons.css` | Button styles & hovers | Tweaking button appearance |
| `components/animations.css` | Shimmer, pulse, transitions | Modifying animations |

### 3. Run the Site Locally

```bash
cd frontend
npm start
# Opens http://localhost:3000
```

---

## Theme Customization (10 Minutes)

### Change Primary Accent Color

**File**: `frontend/src/css/custom.css`

```css
:root {
  /* Change from cyan to another color */
  --color-primary: #ff6b6b;  /* Example: red accent */
  --color-secondary: #ff8787;
  --color-bright: #ffa5a5;

  /* Update opacity variants */
  --cyan-10: rgba(255, 107, 107, 0.1);  /* Adjust RGB to match */
  --cyan-40: rgba(255, 107, 107, 0.4);
  --cyan-60: rgba(255, 107, 107, 0.6);
}
```

**Impact**: Changes all interactive elements (links, buttons, hovers, glows).

### Adjust Spacing

**File**: `frontend/src/css/custom.css`

```css
:root {
  /* Make spacing more compact */
  --spacing-lg: 1.25rem;  /* Was 1.5rem */
  --spacing-xl: 1.75rem;  /* Was 2rem */
  --spacing-2xl: 2.5rem;  /* Was 3rem */
}
```

**Impact**: Reduces padding/margins across all components.

### Change Font Sizes

**File**: `frontend/src/css/custom.css`

```css
:root {
  /* Make headings smaller */
  --font-size-h1: 3rem;    /* Was 3.5rem */
  --font-size-h2: 2.5rem;  /* Was 3rem */
  --font-size-h3: 1.75rem; /* Was 2rem */
}
```

**Impact**: Adjusts heading hierarchy across documentation.

---

## Component Development Guide

### Adding a New Card Style

**File**: `frontend/src/css/components/cards.css`

```css
/* Add new variant */
.doc-card {
  background: var(--bg-secondary);
  border: 1px solid rgba(45, 52, 84, 0.5);
  border-radius: 16px;
  padding: var(--spacing-lg);
  cursor: pointer;
  transition: all 0.3s ease;
}

.doc-card:hover {
  transform: translateY(-8px) scale(1.05);
  border-color: var(--color-primary);
  box-shadow: 0 0 30px var(--cyan-40), 0 0 60px var(--cyan-20);
}
```

**Usage**: Add class `doc-card` to HTML/MDX elements.

### Creating Custom Button Variant

**File**: `frontend/src/css/components/buttons.css`

```css
.btn-outline {
  background: transparent;
  color: var(--color-secondary);
  border: 2px solid var(--color-secondary);
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-outline:hover {
  background: var(--cyan-10);
  transform: scale(1.05);
  box-shadow: 0 0 20px var(--cyan-40);
}
```

**Usage**: `<button className="btn-outline">Click Me</button>`

---

## Testing Checklist

### Visual Testing

- [ ] **Desktop** (1920×1080): Open http://localhost:3000, check homepage
- [ ] **Tablet** (768×1024): Resize browser, verify responsive layout
- [ ] **Mobile** (375×667): Check hamburger menu, mobile navigation
- [ ] **Dark/Light Toggle**: Verify theme switching works smoothly

### Interaction Testing

- [ ] **Hover Effects**: Hover over cards, buttons, links - verify glow/scale
- [ ] **Keyboard Navigation**: Press Tab - check focus indicators visible
- [ ] **Code Blocks**: View documentation page - verify syntax highlighting
- [ ] **Sidebar**: Click navigation - verify active states

### Accessibility Testing

```bash
# Run Lighthouse in Chrome DevTools
# 1. Open DevTools (F12)
# 2. Go to "Lighthouse" tab
# 3. Select "Accessibility"
# 4. Click "Analyze page load"
# Target: 90+ score
```

**Key Checks**:
- Contrast ratios: All text readable (WCAG AA)
- Focus indicators: 2px cyan outline visible
- Keyboard navigation: All interactive elements accessible

---

## Common Tasks

### Task 1: Add Shimmer Effect to New Component

```css
.my-component {
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.my-component::before {
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
}

.my-component:hover::before {
  animation: shimmer 1.5s infinite;
}
```

### Task 2: Override Docusaurus Component Style

**File**: `frontend/src/css/custom.css`

```css
/* Override default Docusaurus navbar link */
.navbar__link {
  color: var(--text-secondary);
  font-weight: 600;
}

.navbar__link:hover {
  color: var(--color-primary);
  text-shadow: 0 0 10px var(--cyan-40);
}
```

### Task 3: Create Responsive Grid

```css
.my-grid {
  display: grid;
  gap: var(--spacing-lg);
}

/* Mobile: 1 column */
@media (max-width: 767px) {
  .my-grid {
    grid-template-columns: 1fr;
  }
}

/* Tablet: 2 columns */
@media (min-width: 768px) and (max-width: 1023px) {
  .my-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Desktop: 3 columns */
@media (min-width: 1024px) {
  .my-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

---

## Debugging Tips

### Issue: Colors Not Changing

**Solution**: Clear browser cache and Docusaurus cache

```bash
# Clear Docusaurus cache
npm run clear

# Restart dev server
npm start

# Hard refresh browser: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
```

### Issue: Hover Effects Not Working

**Checklist**:
- [ ] Is `cursor: pointer` set on the element?
- [ ] Is `transition` property defined?
- [ ] Is the element position `relative` (for pseudo-elements)?
- [ ] Are you using `transform` (not `top`/`left` for performance)?

### Issue: Layout Breaks on Mobile

**Solution**: Check responsive breakpoints

```css
/* Ensure mobile-first approach */
.my-element {
  /* Default: mobile styles */
  padding: var(--spacing-md);
}

/* Add tablet/desktop enhancements */
@media (min-width: 768px) {
  .my-element {
    padding: var(--spacing-xl);
  }
}
```

---

## Performance Optimization

### Reduce Animation Jank

**Use GPU-accelerated properties**:
```css
/* ✅ GOOD: GPU-accelerated */
.card:hover {
  transform: translateY(-8px) scale(1.05);
  will-change: transform, box-shadow;
}

/* ❌ BAD: Triggers layout recalculation */
.card:hover {
  top: -8px;  /* Don't use top/left */
  width: 105%;  /* Don't animate width */
}
```

### Optimize Shimmer Animation

```css
/* Only animate on hover (save CPU when idle) */
.card::before {
  /* No animation by default */
}

.card:hover::before {
  animation: shimmer 1.5s infinite;  /* Animate only on hover */
}
```

---

## Reference

### Quick Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Primary Cyan | `#00d4ff` | Links, buttons, accents |
| Secondary Blue | `#0ea5e9` | Secondary accents |
| Bright Cyan | `#22d3ee` | Hover states |
| Dark Navy | `#0f1729` | Main background |
| Card Background | `#1a1f3a` | Cards, sections |

### Common CSS Variables

```css
/* Colors */
var(--color-primary)
var(--bg-primary)
var(--text-primary)

/* Typography */
var(--font-size-h1)
var(--font-family-base)
var(--line-height-relaxed)

/* Spacing */
var(--spacing-md)
var(--spacing-lg)
var(--spacing-xl)

/* Effects */
var(--shadow-glow)
var(--transition-normal)
var(--gradient-primary)
```

---

## Next Steps

1. **Review Contracts**: Check `specs/001-robobook-ui-theme/contracts/` for full design system specs
2. **Implement Components**: Follow tasks in `tasks.md` (created by `/sp.tasks`)
3. **Test Thoroughly**: Use checklist above before marking complete
4. **Deploy**: Build and deploy to production once tested

**Need Help?**
- Check research.md for design rationale
- Review data-model.md for component specifications
- See contracts/ for detailed design tokens

---

**Happy Theming!** 🎨
