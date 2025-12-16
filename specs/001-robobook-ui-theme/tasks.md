# Implementation Tasks: RoboBook UI & Color Theme

**Feature**: RoboBook UI & Color Theme
**Branch**: `001-robobook-ui-theme`
**Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)
**Generated**: 2025-12-16

---

## Task Summary

**Total Tasks**: 45
**User Stories**: 4 (2× P1, 1× P2, 1× P3)
**Parallel Opportunities**: 28 tasks marked [P]
**Testing Approach**: Visual + Accessibility + Responsive testing (no automated tests - visual QA)

### Tasks by Phase

| Phase | Tasks | Description |
|-------|-------|-------------|
| **Phase 1: Setup** | 3 | Project initialization and directory structure |
| **Phase 2: Design Tokens** | 4 | CSS variables foundation (blocking for all stories) |
| **Phase 3: US4 + US1** | 12 | P1 stories - Homepage + Content navigation (MVP) |
| **Phase 4: US2** | 8 | P2 story - Instructor navigation features |
| **Phase 5: US3** | 8 | P3 story - Mobile responsive design |
| **Phase 6: Polish** | 10 | Cross-cutting concerns + optimization |

---

## Dependencies & Execution Strategy

### User Story Completion Order

```
Phase 1: Setup (prerequisites)
   ↓
Phase 2: Design Tokens (blocking for all stories)
   ↓
Phase 3: US4 (Homepage) + US1 (Content Navigation) ← MVP SCOPE
   ↓
Phase 4: US2 (Instructor Features) ← PARALLEL with Phase 5
   ↓
Phase 5: US3 (Mobile Responsive) ← PARALLEL with Phase 4
   ↓
Phase 6: Polish & Optimization
```

### Independent Testing Points

- **After Phase 3**: Test US4 (Homepage loads with module cards) + US1 (Can navigate docs with styled code blocks)
- **After Phase 4**: Test US2 (Sidebar navigation, search styling, collapsible sections)
- **After Phase 5**: Test US3 (Mobile layouts, hamburger menu, responsive grids)
- **After Phase 6**: Full accessibility + performance validation

### Parallel Execution Examples

**Phase 3 Parallelization** (6 tasks can run simultaneously):
```
T007 [P] [US4] Hero section styling
T008 [P] [US4] Module cards styling
T011 [P] [US1] Code block styling
T012 [P] [US1] Markdown content styling
T013 [P] [US1] TOC styling
T014 [P] [US1] Footer styling
```

**Phase 4 Parallelization** (5 tasks can run simultaneously):
```
T019 [P] [US2] Sidebar menu styling
T020 [P] [US2] Collapsible sections
T021 [P] [US2] Search results styling
T022 [P] [US2] Search input styling
T023 [P] [US2] Module navigation
```

---

## Phase 1: Setup

**Goal**: Initialize CSS file structure and validate environment

**Acceptance**: Directory structure created, Docusaurus dev server runs without errors

- [X] T001 Verify Docusaurus 3.9.2 is running with `npm start` in frontend/
- [X] T002 Create CSS directory structure: frontend/src/css/components/ and frontend/src/css/utilities/
- [X] T003 Backup existing frontend/src/css/custom.css to custom.css.backup

---

## Phase 2: Design Tokens (Foundational - Blocking)

**Goal**: Establish CSS custom properties foundation for all components

**Acceptance**: All design tokens defined and accessible via CSS variables

**Why Blocking**: All subsequent user stories depend on these design tokens for colors, typography, and spacing

- [X] T004 Create design token system in frontend/src/css/custom.css with color variables (12 colors from contracts/color-palette.json)
- [X] T005 [P] Add typography tokens to frontend/src/css/custom.css (9 font sizes, 4 weights from contracts/typography-scale.json)
- [X] T006 [P] Add spacing tokens to frontend/src/css/custom.css (10 spacing values from contracts/spacing-system.json)
- [X] T007 [P] Add Docusaurus Infima overrides to frontend/src/css/custom.css (--ifm-* variables for integration)

---

## Phase 3: User Story 4 + User Story 1 (P1 - MVP)

### User Story 4: First-Time Visitor Understanding Content Scope

**Goal**: Homepage clearly communicates curriculum value with visual hierarchy

**Acceptance Test**:
1. Load http://localhost:3000
2. Hero section displays with cyan accent colors and clear tagline
3. Module cards show all 4 modules with distinct visual treatment
4. "Get Started" button is prominently visible

**Tasks**:

- [X] T008 [US4] Create hero section styles in frontend/src/css/components/hero.css with gradient background, badge animation, and CTA button
- [X] T009 [US4] Style module cards in frontend/src/css/components/cards.css with hover effects (scale + glow + shimmer)
- [X] T010 [US4] Implement shimmer animation in frontend/src/css/components/animations.css with @keyframes shimmer
- [X] T011 [US4] Import hero.css, cards.css, and animations.css in frontend/src/css/custom.css

### User Story 1: Student Navigating Course Content

**Goal**: Students can read documentation with clear typography, syntax highlighting, and navigation

**Acceptance Test**:
1. Navigate to /docs/module1/chapter1
2. Code blocks have dark background with cyan syntax highlighting
3. Sidebar shows current location with active state (cyan border-left)
4. Text is readable with WCAG AA contrast (4.5:1+)

**Tasks**:

- [X] T012 [P] [US1] Create navbar styles in frontend/src/css/components/navbar.css with sticky positioning, backdrop blur, and hover states
- [X] T013 [P] [US1] Create sidebar styles in frontend/src/css/components/sidebar.css with active states and hover effects
- [X] T014 [P] [US1] Create code block styles in frontend/src/css/components/code-blocks.css with syntax highlighting overrides
- [X] T015 [P] [US1] Create content typography styles overriding .markdown h1/h2/h3, p, code in frontend/src/css/custom.css
- [X] T016 [P] [US1] Create TOC (Table of Contents) styles for .table-of-contents__link in frontend/src/css/components/sidebar.css
- [X] T017 [P] [US1] Create footer styles in frontend/src/css/components/footer.css with link hover effects
- [X] T018 [US1] Import all component CSS files (navbar, sidebar, code-blocks, footer) in frontend/src/css/custom.css
- [ ] T019 [US1] Test navigation flow: homepage → docs → chapter → prev/next buttons work with styled UI

---

## Phase 4: User Story 2 (P2 - Instructor Features)

**Goal**: Instructors can efficiently explore and navigate the course structure

**Acceptance Test**:
1. Open sidebar navigation
2. All 4 modules are clearly grouped with visual hierarchy
3. Collapsible sections expand/collapse smoothly
4. Search results display with module context and are easy to scan

**Tasks**:

- [X] T020 [P] [US2] Add collapsible section indicators to sidebar with CSS transitions in frontend/src/css/components/sidebar.css
- [X] T021 [P] [US2] Style category headers in sidebar with distinct typography and spacing in frontend/src/css/components/sidebar.css
- [X] T022 [P] [US2] Create search results styles in frontend/src/css/components/search.css with result cards and hover states
- [X] T023 [P] [US2] Style search input field with focus states and placeholder text in frontend/src/css/components/search.css
- [X] T024 [P] [US2] Add visual grouping for module sections with background colors and borders in frontend/src/css/components/sidebar.css
- [X] T025 [US2] Style breadcrumb navigation with separators and active states in frontend/src/css/custom.css overriding .breadcrumbs
- [X] T026 [US2] Import search.css in frontend/src/css/custom.css
- [ ] T027 [US2] Test instructor workflow: explore sidebar → collapse/expand modules → search for "VSLAM" → verify clear results

---

## Phase 5: User Story 3 (P3 - Mobile Responsive)

**Goal**: Site is fully functional and touch-friendly on mobile devices

**Acceptance Test**:
1. Resize browser to 375px width (or use device)
2. Navigation hamburger menu appears and functions
3. Content reflows to single column
4. Text remains legible (16px minimum) without zooming

**Tasks**:

- [X] T028 [P] [US3] Add mobile breakpoint (<768px) styles to frontend/src/css/custom.css with responsive font sizes
- [X] T029 [P] [US3] Create responsive grid styles in frontend/src/css/utilities/responsive.css with mobile/tablet/desktop columns
- [X] T030 [P] [US3] Add mobile navbar styles with hamburger menu in frontend/src/css/components/navbar.css
- [X] T031 [P] [US3] Add mobile sidebar styles with slide-in animation in frontend/src/css/components/sidebar.css
- [X] T032 [P] [US3] Add mobile hero section styles with single column layout in frontend/src/css/components/hero.css
- [X] T033 [P] [US3] Add mobile card grid (1 column) in frontend/src/css/components/cards.css
- [X] T034 [P] [US3] Add mobile code block horizontal scroll in frontend/src/css/components/code-blocks.css
- [X] T035 [US3] Import responsive.css in frontend/src/css/custom.css
- [ ] T036 [US3] Test mobile workflow: load site on 375px width → open hamburger menu → navigate docs → scroll code blocks

---

## Phase 6: Polish & Cross-Cutting Concerns

**Goal**: Optimize performance, ensure accessibility, and add finishing touches

**Acceptance Criteria**:
- Lighthouse accessibility score 90+
- All focus indicators visible (2px cyan outline)
- CSS bundle <50KB
- No console errors or warnings

**Tasks**:

### Accessibility & Focus States

- [X] T037 [P] Add focus indicator styles for all interactive elements (.navbar__link:focus, .menu__link:focus, a:focus, button:focus) in frontend/src/css/custom.css
- [X] T038 [P] Add skip-to-main-content link styling in frontend/src/css/custom.css with .skip-to-main class
- [ ] T039 [P] Test keyboard navigation: Tab through all interactive elements, verify focus indicators visible

### Button & Link Styling

- [X] T040 [P] Create primary button styles in frontend/src/css/components/buttons.css with gradient and hover effects
- [X] T041 [P] Create secondary button styles in frontend/src/css/components/buttons.css with border and hover effects
- [X] T042 [P] Create link hover effects with underline animation in frontend/src/css/custom.css overriding a::after pseudo-element
- [X] T043 Import buttons.css in frontend/src/css/custom.css

### Performance & Optimization

- [X] T044 Add GPU acceleration hints (will-change: transform, box-shadow) to hover states in frontend/src/css/components/animations.css
- [X] T045 Add @media (prefers-reduced-motion: reduce) fallback disabling animations in frontend/src/css/custom.css
- [X] T046 Run `npm run build` and verify CSS bundle size <50KB in build/assets/css/
- [ ] T047 Run Lighthouse audit: verify Accessibility 90+, Performance 90+, no console errors

---

## Validation Checklist

Before marking complete, verify ALL of these:

### User Story Testing

- [ ] **US4**: Homepage loads with hero section, module cards, and clear CTAs
- [ ] **US1**: Can navigate docs with styled sidebar, code blocks, and prev/next buttons
- [ ] **US2**: Sidebar is organized, collapsible, search results are styled
- [ ] **US3**: Site is responsive on mobile (320px-480px) with hamburger menu

### Functional Requirements (from spec.md)

- [ ] FR-001: Consistent color palette (cyan #00d4ff primary) used throughout
- [ ] FR-002: Code blocks have syntax highlighting for Python, C++, YAML, Bash
- [ ] FR-003: Prev/next chapter buttons are clearly visible
- [ ] FR-004: Sidebar collapses on mobile, expands on desktop
- [ ] FR-005: Typography meets WCAG AA (4.5:1 contrast, 16px body text, 1.6 line-height)
- [ ] FR-006: Homepage displays 4 module cards with visual hierarchy
- [ ] FR-007: All interactive elements have hover/focus states
- [ ] FR-008: Dark/light mode toggle works (dark is default)
- [ ] FR-009: Consistent 8px-based spacing used throughout
- [ ] FR-010: Code blocks have copy button (Docusaurus default - verify styling)
- [ ] FR-011: System fonts load instantly (zero latency)
- [ ] FR-012: Search interface styled consistently with theme
- [ ] FR-013: Footer contains copyright, license, community links
- [ ] FR-014: Navbar is sticky at top with logo and navigation
- [ ] FR-015: Site responsive from 320px to 2560px

### Accessibility (WCAG 2.1 AA)

- [ ] All text contrast ratios 4.5:1+ (verify with WebAIM Contrast Checker)
- [ ] Focus indicators 2px cyan outline on all interactive elements
- [ ] Keyboard navigation: Tab, Shift+Tab, Enter, Space all work
- [ ] Skip-to-main-content link appears on Tab (for screen readers)
- [ ] No animations if user has prefers-reduced-motion enabled

### Performance

- [ ] CSS bundle <50KB gzipped (check build/assets/css/)
- [ ] First Contentful Paint <1.5s (Lighthouse)
- [ ] Lighthouse Performance score 90+
- [ ] No layout shift (CLS <0.1)
- [ ] All animations use GPU-accelerated properties (transform, opacity)

### Browser Compatibility

- [ ] Chrome (latest): All features work
- [ ] Firefox (latest): All features work
- [ ] Safari (latest): All features work
- [ ] Mobile Safari (iOS): Responsive layouts work

---

## Quick Reference

### File Locations

| Component | File Path |
|-----------|-----------|
| Entry Point | frontend/src/css/custom.css |
| Navbar | frontend/src/css/components/navbar.css |
| Sidebar | frontend/src/css/components/sidebar.css |
| Footer | frontend/src/css/components/footer.css |
| Hero Section | frontend/src/css/components/hero.css |
| Cards | frontend/src/css/components/cards.css |
| Buttons | frontend/src/css/components/buttons.css |
| Code Blocks | frontend/src/css/components/code-blocks.css |
| Animations | frontend/src/css/components/animations.css |
| Search | frontend/src/css/components/search.css |
| Responsive | frontend/src/css/utilities/responsive.css |

### Key Design Tokens

**Colors**: `--color-primary` (#00d4ff), `--bg-primary` (#0f1729), `--text-primary` (#ffffff)

**Typography**: `--font-size-base` (1rem/16px), `--line-height-relaxed` (1.6)

**Spacing**: `--spacing-md` (1rem/16px), `--spacing-lg` (1.5rem/24px), `--spacing-xl` (2rem/32px)

**Transitions**: `--transition-normal` (0.3s ease)

**Shadows**: `--shadow-glow` (cyan glow effect), `--shadow-card` (subtle glow)

### Testing Commands

```bash
# Start dev server
cd frontend && npm start

# Build for production
cd frontend && npm run build

# Check bundle size
du -sh frontend/build/assets/css/*

# Run Lighthouse
lighthouse http://localhost:3000 --view
```

---

## Implementation Strategy

**MVP (Minimum Viable Product)**: Complete Phase 1, 2, and 3 only
- Phase 1: Setup
- Phase 2: Design Tokens
- Phase 3: US4 (Homepage) + US1 (Content Navigation)

**Result**: First-time visitors see an attractive homepage and students can navigate documentation with clear styling. This validates the core value proposition.

**Incremental Delivery**:
1. MVP (Phases 1-3) → Deploy to staging for user feedback
2. Phase 4 (US2 - Instructor Features) → Enhance navigation
3. Phase 5 (US3 - Mobile Responsive) → Expand device support
4. Phase 6 (Polish) → Optimize and finalize

**Parallel Work**: After Phase 2 completes, Phases 4 and 5 can be developed simultaneously as they modify different CSS files with minimal overlap.

---

**Total Estimated Time**: 2-3 hours (MVP), 4-5 hours (complete)

**Next Steps**: Start with T001 (verify Docusaurus is running), then proceed sequentially through Phase 1 and 2. Once Phase 2 completes, parallelize Phase 3 tasks where marked [P].
