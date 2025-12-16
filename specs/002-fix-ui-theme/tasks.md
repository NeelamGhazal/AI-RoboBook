# Tasks: Fix RoboBook UI and Theme Issues

**Feature**: 002-fix-ui-theme
**Branch**: `002-fix-ui-theme`
**Created**: 2025-12-16
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Overview

This feature fixes 5 UI and theme issues organized by user story for independent implementation and testing:
- **US1 (P1)**: Logo Display and Branding
- **US2 (P1)**: Navbar Layout and Alignment
- **US3 (P2)**: Light Theme Functionality
- **US4 (P1)**: Docs Sidebar Restoration
- **US5 (P2)**: Content Page Buttons

**Total Tasks**: 25 tasks across 7 phases
**Parallelization**: 12 tasks can run in parallel (marked with [P])
**MVP Scope**: User Story 1 (Logo Display) + User Story 4 (Sidebar Restoration)

---

## Implementation Strategy

### Independent User Stories

Each user story is **independently testable** and can be implemented separately:

**Priority 1 (P1) Stories** - Critical functionality:
- US1: Logo Display (no dependencies)
- US2: Navbar Layout (no dependencies)
- US4: Sidebar Restoration (no dependencies)

**Priority 2 (P2) Stories** - Enhanced functionality:
- US3: Light Theme (depends on Setup phase only)
- US5: Content Buttons (depends on Setup phase only)

### Dependency Graph

```
Setup Phase (Phase 1)
    ↓
Foundational Phase (Phase 2)
    ↓
    ├──→ US1: Logo Display (Phase 3) [P1] ───────┐
    ├──→ US2: Navbar Layout (Phase 4) [P1] ──────┤
    ├──→ US4: Sidebar Restoration (Phase 5) [P1] ┤
    ├──→ US3: Light Theme (Phase 6) [P2] ────────┤
    └──→ US5: Content Buttons (Phase 7) [P2] ────┤
                                                   ↓
                                            Polish Phase (Phase 8)
```

### Suggested Execution Order

**MVP First** (Minimal Viable Product):
1. Complete Setup + Foundational phases
2. Implement US1 (Logo) + US4 (Sidebar) → Delivers working branding and navigation
3. Test independently → Can ship if needed

**Incremental Delivery**:
1. Add US2 (Navbar) → Enhanced navigation
2. Add US3 (Light Theme) → Accessibility improvement
3. Add US5 (Content Buttons) → Feature completeness
4. Polish phase → Final QA

**Parallel Execution** (if multiple developers):
- After Foundational phase, ALL user stories (US1-US5) can be implemented in parallel
- Each story modifies different files
- Independent testing per story

---

## Phase 1: Setup

**Goal**: Initialize development environment and verify prerequisites

**Prerequisites**: None
**Estimated Time**: 15 minutes

### Tasks

- [ ] T001 Verify frontend directory exists and contains Docusaurus project at `/mnt/e/phyai-humanoid-textbook/frontend`
- [ ] T002 Verify Node.js 18+ and npm 9+ installed via `node --version && npm --version`
- [ ] T003 [P] Verify existing logo file at `/mnt/e/phyai-humanoid-textbook/frontend/static/img/robobook-logo.png` (should be ~106KB)
- [ ] T004 [P] Install npm dependencies in frontend directory via `cd frontend && npm install`
- [ ] T005 [P] Verify Docusaurus version is 3.9.2 via `npm list @docusaurus/core`
- [ ] T006 Start development server via `npm start` and verify site loads at http://localhost:3000

---

## Phase 2: Foundational

**Goal**: Verify current state and document baseline issues

**Prerequisites**: Phase 1 complete
**Estimated Time**: 30 minutes

### Tasks

- [ ] T007 Document current logo state: Check navbar at http://localhost:3000 and verify logo shows .svg (not .png)
- [ ] T008 Document navbar layout issues: Inspect right section and confirm GitHub icon present, Sign In/Sign Up absent
- [ ] T009 Document light theme state: Toggle theme and verify light theme broken/unstyled
- [ ] T010 Document sidebar text orientation: Navigate to /docs/intro and check if sidebar text is vertical or horizontal
- [ ] T011 Document content buttons state: Check any /docs/* page and verify no buttons above content

---

## Phase 3: User Story 1 - Logo Display and Branding (P1)

**User Story**: As a visitor to the RoboBook documentation site, I need to see a clear, properly-rendered RoboBook logo in the navbar so that I can identify the site's branding and navigate confidently.

**Independent Test Criteria**:
✅ **PASS**: Logo displays as PNG with transparent background in navbar
✅ **PASS**: Logo visible and clear in both light and dark themes
✅ **PASS**: Logo height ~40px without pixelation
✅ **PASS**: Logo loads in <100ms

**Files Modified**:
- `frontend/docusaurus.config.ts`

**Prerequisites**: Phase 2 complete
**Estimated Time**: 15 minutes

### Implementation Tasks

- [ ] T012 [P] [US1] Update logo path in `/mnt/e/phyai-humanoid-textbook/frontend/docusaurus.config.ts` line 68 from `src: 'img/robobook-logo.svg'` to `src: 'img/robobook-logo.png'`
- [ ] T013 [US1] Hot reload verification: Check navbar logo updates to PNG automatically
- [ ] T014 [US1] Test logo transparency: Toggle between light/dark themes and verify logo background is transparent

### Acceptance Testing

- [ ] T015 [US1] Verify acceptance scenario 1: Load any page, confirm robobook-logo.png displays with transparent background
- [ ] T016 [US1] Verify acceptance scenario 2: Inspect logo element, confirm no pixelation or distortion at 40px height
- [ ] T017 [US1] Verify acceptance scenario 3: Switch themes multiple times, confirm logo remains visible in both

**Story Complete**: ✅ All acceptance scenarios pass

---

## Phase 4: User Story 2 - Navbar Layout and Alignment (P1)

**User Story**: As a user navigating the RoboBook site, I need navbar elements to be properly aligned and organized so that I can easily access navigation controls and authentication options.

**Independent Test Criteria**:
✅ **PASS**: All navbar elements vertically centered
✅ **PASS**: Left side unchanged (Modules link present)
✅ **PASS**: Right side order (L-R): Search, Sign In, Sign Up, Theme Toggle
✅ **PASS**: GitHub icon removed
✅ **PASS**: Responsive on mobile (hamburger menu works)

**Files Modified**:
- `frontend/docusaurus.config.ts` (navbar.items array)
- `frontend/src/css/components/navbar.css`

**Prerequisites**: Phase 2 complete (can run parallel with US1, US3, US4, US5)
**Estimated Time**: 45 minutes

### Implementation Tasks

- [ ] T018 [P] [US2] Update navbar.items array in `/mnt/e/phyai-humanoid-textbook/frontend/docusaurus.config.ts` (lines 70-82): Remove GitHub link object
- [ ] T019 [P] [US2] Add Sign In link to navbar.items in `/mnt/e/phyai-humanoid-textbook/frontend/docusaurus.config.ts`: Insert `{type: 'html', position: 'right', value: '<a href="/signin" class="navbar-signin-link"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M21 12H9"/></svg>Sign In</a>'}`
- [ ] T020 [P] [US2] Add Sign Up link to navbar.items in `/mnt/e/phyai-humanoid-textbook/frontend/docusaurus.config.ts`: Insert `{type: 'html', position: 'right', value: '<a href="/signup" class="navbar-signup-link"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2M12 11A4 4 0 1 0 12 3a4 4 0 0 0 0 8z"/></svg>Sign Up</a>'}`
- [ ] T021 [US2] Add vertical centering CSS to `/mnt/e/phyai-humanoid-textbook/frontend/src/css/components/navbar.css` after line 40: `.navbar__inner { display: flex; align-items: center; }` and `.navbar__items { display: flex; align-items: center; gap: var(--spacing-md); }`
- [ ] T022 [US2] Add Sign In/Sign Up link styles to `/mnt/e/phyai-humanoid-textbook/frontend/src/css/components/navbar.css` after line 145: Complete styles from quickstart.md Phase 2B
- [ ] T023 [US2] Test navbar layout: Verify vertical centering, element ordering, and GitHub removal

### Acceptance Testing

- [ ] T024 [US2] Verify acceptance scenario 1: Check left side has Modules link vertically centered
- [ ] T025 [US2] Verify acceptance scenario 2: Check right side L-R order is Search, Sign In, Sign Up, Theme Toggle
- [ ] T026 [US2] Verify acceptance scenario 3: Confirm GitHub icon not present in navbar
- [ ] T027 [US2] Verify acceptance scenario 4: Resize browser window, confirm responsive behavior at 996px and 767px breakpoints

**Story Complete**: ✅ All acceptance scenarios pass

---

## Phase 5: User Story 4 - Docs Sidebar Restoration (P1)

**User Story**: As a user reading documentation, I need the docs sidebar to display horizontally-readable text and follow default Docusaurus structure so that I can navigate the documentation efficiently.

**Independent Test Criteria**:
✅ **PASS**: Sidebar text reads left-to-right horizontally (not vertical)
✅ **PASS**: Navigation hierarchy preserved with proper nesting
✅ **PASS**: Collapsible sections work correctly
✅ **PASS**: Active page highlight displays correctly
✅ **PASS**: Mobile sidebar functional on < 996px viewports

**Files Modified**:
- `frontend/src/css/components/sidebar.css`
- Potentially `frontend/sidebars.js` (if structure issues found)

**Prerequisites**: Phase 2 complete (can run parallel with US1, US2, US3, US5)
**Estimated Time**: 30 minutes

### Diagnostic Tasks

- [ ] T028 [P] [US4] Inspect sidebar in browser DevTools: Navigate to /docs/intro, right-click sidebar link, check computed styles for writing-mode, text-orientation, transform properties
- [ ] T029 [P] [US4] Search for problematic CSS in `/mnt/e/phyai-humanoid-textbook/frontend/src/css/components/sidebar.css`: Run `grep -n "writing-mode\|rotate\|flex-direction" frontend/src/css/components/sidebar.css`
- [ ] T030 [US4] Verify sidebar structure in `/mnt/e/phyai-humanoid-textbook/frontend/sidebars.js`: Confirm standard Docusaurus category format

### Implementation Tasks

- [ ] T031 [P] [US4] Add horizontal text CSS override to `/mnt/e/phyai-humanoid-textbook/frontend/src/css/components/sidebar.css` after line 43: Add `.menu__link, .menu__link--sublist { writing-mode: horizontal-tb !important; text-orientation: mixed !important; transform: none !important; }`
- [ ] T032 [P] [US4] Ensure proper flexbox alignment in `/mnt/e/phyai-humanoid-textbook/frontend/src/css/components/sidebar.css` after line 43: Add `.menu__link { display: flex; flex-direction: row; align-items: center; }`
- [ ] T033 [US4] Test sidebar text orientation: Navigate to multiple /docs/* pages and verify all text is horizontal

### Acceptance Testing

- [ ] T034 [US4] Verify acceptance scenario 1: Sidebar text displays horizontally on all docs pages
- [ ] T035 [US4] Verify acceptance scenario 2: Navigation structure follows default Docusaurus layout with nesting
- [ ] T036 [US4] Verify acceptance scenario 3: Click sidebar items, confirm navigation works without layout breaks
- [ ] T037 [US4] Verify acceptance scenario 4: Test mobile sidebar at 996px, 768px, 375px widths

**Story Complete**: ✅ All acceptance scenarios pass

---

## Phase 6: User Story 3 - Light Theme Functionality (P2)

**User Story**: As a user who prefers light mode, I need the light theme to display correctly with proper styling so that I can read content comfortably in well-lit environments.

**Independent Test Criteria**:
✅ **PASS**: Light theme background is sky blue (#f0f9ff)
✅ **PASS**: Text is dark blue (#0c4a6e) with readable contrast
✅ **PASS**: WCAG AA contrast ratio ≥ 4.5:1 (target: 8.7:1)
✅ **PASS**: Theme toggle completes in <300ms
✅ **PASS**: Theme persists across page reloads
✅ **PASS**: No visual artifacts when switching themes

**Files Modified**:
- `frontend/src/css/custom.css`

**Prerequisites**: Phase 2 complete (can run parallel with US1, US2, US4, US5)
**Estimated Time**: 60 minutes

### Implementation Tasks

- [ ] T038 [P] [US3] Add light theme variables to `/mnt/e/phyai-humanoid-textbook/frontend/src/css/custom.css` after line 150: Insert complete `[data-theme='light']` block with all CSS variables from research.md Decision 3
- [ ] T039 [US3] Test light theme toggle: Click theme toggle button and verify immediate color changes
- [ ] T040 [US3] Verify WCAG AA contrast: Use browser DevTools Accessibility Inspector to check text/background contrast ratios

### Acceptance Testing

- [ ] T041 [US3] Verify acceptance scenario 1: Toggle from dark to light, confirm sky blue background (#f0f9ff) and proper text contrast
- [ ] T042 [US3] Verify acceptance scenario 2: Navigate multiple pages in light theme, confirm consistent styling
- [ ] T043 [US3] Verify acceptance scenario 3: Reload page in light theme, confirm theme persists (check localStorage)
- [ ] T044 [US3] Verify acceptance scenario 4: Rapidly toggle themes 10 times, confirm no broken styles or visual artifacts

### Performance Testing

- [ ] T045 [US3] Measure theme switching time: Use browser Performance tab, verify transition completes in <300ms
- [ ] T046 [US3] Check CSS bundle size increase: Run `npm run build` and verify CSS gzip increase <10KB

**Story Complete**: ✅ All acceptance scenarios pass

---

## Phase 7: User Story 5 - Content Page Buttons (P2)

**User Story**: As a user reading content, I need to see two buttons positioned above the main content (as shown in reference image) so that I can access key features without disrupting the documentation structure.

**Independent Test Criteria**:
✅ **PASS**: Exactly 2 buttons appear above main content
✅ **PASS**: Buttons positioned between page header and content
✅ **PASS**: Buttons appear on ALL /docs/* pages (not landing page)
✅ **PASS**: Docs/book structure NOT broken by buttons
✅ **PASS**: No extra buttons or UI elements added
✅ **PASS**: Hover effects smooth (scale + glow)

**Files Created**:
- `frontend/src/components/ContentButtons/index.tsx`
- `frontend/src/components/ContentButtons/styles.module.css`
- `frontend/src/theme/DocItem/Layout/index.tsx` (swizzled)

**Prerequisites**: Phase 2 complete (can run parallel with US1, US2, US3, US4)
**Estimated Time**: 90 minutes

### Component Creation Tasks

- [ ] T047 [P] [US5] Create ContentButtons component directory: `mkdir -p /mnt/e/phyai-humanoid-textbook/frontend/src/components/ContentButtons`
- [ ] T048 [P] [US5] Create ContentButtons component at `/mnt/e/phyai-humanoid-textbook/frontend/src/components/ContentButtons/index.tsx`: Implement React component with 2 buttons (Personalized Mode + English/اردو) from quickstart.md Phase 5A
- [ ] T049 [P] [US5] Create ContentButtons styles at `/mnt/e/phyai-humanoid-textbook/frontend/src/components/ContentButtons/styles.module.css`: Add flexbox layout, gradient backgrounds, hover effects from quickstart.md Phase 5A

### Swizzling Tasks

- [ ] T050 [US5] Run Docusaurus swizzle command: `cd /mnt/e/phyai-humanoid-textbook/frontend && npm run swizzle @docusaurus/theme-classic DocItem/Layout -- --wrap`
- [ ] T051 [US5] Verify swizzle created file at `/mnt/e/phyai-humanoid-textbook/frontend/src/theme/DocItem/Layout/index.tsx`
- [ ] T052 [US5] Modify swizzled layout at `/mnt/e/phyai-humanoid-textbook/frontend/src/theme/DocItem/Layout/index.tsx`: Import ContentButtons and inject above props.children per quickstart.md Phase 5B
- [ ] T053 [US5] Add TypeScript types if needed: Import `WrapperProps` from '@docusaurus/types'

### Testing Tasks

- [ ] T054 [US5] Test buttons on docs pages: Navigate to /docs/intro and verify 2 buttons appear above content
- [ ] T055 [US5] Test buttons NOT on landing page: Navigate to / and confirm buttons absent
- [ ] T056 [US5] Test hover effects: Hover over each button and verify scale (1.05) and glow animations

### Acceptance Testing

- [ ] T057 [US5] Verify acceptance scenario 1: Check all /docs/* pages have exactly 2 buttons above content
- [ ] T058 [US5] Verify acceptance scenario 2: Measure button position - should be between page header and main content markdown
- [ ] T059 [US5] Verify acceptance scenario 3: Navigate between docs pages, confirm sidebar and navigation work correctly
- [ ] T060 [US5] Verify acceptance scenario 4: Check button consistency across 5+ different docs pages
- [ ] T061 [US5] Verify acceptance scenario 5: Inspect entire page, confirm only 2 buttons present (no extras added)

### Build Verification

- [ ] T062 [US5] Run production build: `cd /mnt/e/phyai-humanoid-textbook/frontend && npm run build` and verify no TypeScript errors
- [ ] T063 [US5] Serve production build: `npm run serve` and test buttons in production mode

**Story Complete**: ✅ All acceptance scenarios pass

---

## Phase 8: Polish & Cross-Cutting Concerns

**Goal**: Final integration testing, performance optimization, and documentation

**Prerequisites**: All user story phases complete (Phase 3-7)
**Estimated Time**: 60-90 minutes

### Integration Testing

- [ ] T064 Test all 5 features together: Verify logo, navbar, light theme, sidebar, and content buttons all work simultaneously
- [ ] T065 Cross-browser testing: Test on Chrome, Firefox, Safari, Edge (latest versions)
- [ ] T066 Responsive testing: Test at viewports 1920x1080, 1366x768, 768x1024, 375x667, 360x640
- [ ] T067 Theme switching stress test: Toggle between themes 20 times rapidly, verify no memory leaks or performance degradation

### Performance Testing

- [ ] T068 Run Lighthouse audit: Verify performance score >90 on http://localhost:3000
- [ ] T069 Measure CSS bundle size: Check `build/assets/css/*.css` gzipped size, confirm increase <10KB from baseline
- [ ] T070 Verify logo load time: Use Network tab, confirm robobook-logo.png loads in <100ms
- [ ] T071 Measure theme switch timing: Record 10 theme switches, verify average <300ms

### Edge Case Testing

- [ ] T072 Test very small mobile screens: Verify navbar and sidebar at 320px width
- [ ] T073 Test rapid theme toggling: Switch themes 50 times in 10 seconds, check for visual artifacts
- [ ] T074 Test deeply nested sidebar: Navigate to docs with >5 levels of nesting, verify text remains horizontal
- [ ] T075 Test long button labels: Temporarily modify button text to 50+ characters, verify mobile layout doesn't break

### Final Verification

- [ ] T076 Verify all FR requirements: Cross-check tasks against 23 functional requirements in spec.md
- [ ] T077 Verify all success criteria: Check 10 success criteria from spec.md are met
- [ ] T078 Run final build: `npm run build` without errors or warnings
- [ ] T079 Document any deviations: If any requirements not fully met, document in tasks.md

---

## Parallel Execution Examples

### After Phase 2 (Foundational Complete)

**Parallel Group 1** - Can ALL run simultaneously:
```bash
# Developer 1: US1 - Logo Display
Tasks: T012, T013, T014, T015, T016, T017

# Developer 2: US2 - Navbar Layout
Tasks: T018, T019, T020, T021, T022, T023, T024, T025, T026, T027

# Developer 3: US3 - Light Theme
Tasks: T038, T039, T040, T041, T042, T043, T044, T045, T046

# Developer 4: US4 - Sidebar Restoration
Tasks: T028, T029, T030, T031, T032, T033, T034, T035, T036, T037

# Developer 5: US5 - Content Buttons
Tasks: T047, T048, T049, T050, T051, T052, T053, T054, T055, T056, T057, T058, T059, T060, T061, T062, T063
```

**Reason for Independence**: Each user story modifies different files with no overlapping changes.

### Within User Stories

**US2 - Navbar Layout** - Parallel opportunities:
- T018 (remove GitHub) + T019 (add Sign In) + T020 (add Sign Up) → Can edit config file in 3 sections simultaneously if using merge tools
- T021 (CSS vertical centering) + T022 (CSS link styles) → Different sections of navbar.css

**US4 - Sidebar Restoration** - Parallel opportunities:
- T028 (DevTools inspection) + T029 (grep CSS) → Independent diagnostic tasks
- T031 (text override) + T032 (flexbox alignment) → Different CSS rules

**US5 - Content Buttons** - Parallel opportunities:
- T047 (create dir) + T048 (create component) + T049 (create styles) → Different files

---

## Success Metrics

### Per User Story

**US1 - Logo Display** (P1):
- ✅ 6 tasks completed
- ✅ 3 acceptance scenarios passed
- ✅ Independent test: Logo visible in both themes

**US2 - Navbar Layout** (P1):
- ✅ 10 tasks completed
- ✅ 4 acceptance scenarios passed
- ✅ Independent test: All navbar elements properly ordered

**US3 - Light Theme** (P2):
- ✅ 9 tasks completed
- ✅ 4 acceptance scenarios passed
- ✅ Independent test: WCAG AA contrast verified

**US4 - Sidebar Restoration** (P1):
- ✅ 10 tasks completed
- ✅ 4 acceptance scenarios passed
- ✅ Independent test: Sidebar text 100% horizontal

**US5 - Content Buttons** (P2):
- ✅ 17 tasks completed
- ✅ 5 acceptance scenarios passed
- ✅ Independent test: Buttons on all docs pages

### Overall Feature

- ✅ **Total Tasks**: 79 tasks
- ✅ **Parallel Tasks**: 12 tasks marked [P]
- ✅ **User Stories**: 5 stories (3 P1, 2 P2)
- ✅ **Acceptance Scenarios**: 21 scenarios total
- ✅ **Constitution Compliance**: All principles met
- ✅ **Performance Goals**: <100ms logo load, <300ms theme switch, <10KB CSS increase
- ✅ **Cross-Browser**: Chrome, Firefox, Safari, Edge
- ✅ **Responsive**: Desktop, tablet, mobile

---

## MVP Definition

**Minimum Viable Product** = US1 (Logo) + US4 (Sidebar)

**Rationale**:
- US1 fixes critical branding (logo display)
- US4 fixes critical navigation (sidebar readability)
- Together deliver: Professional appearance + Usable documentation
- Can ship to production if time-constrained
- Estimated time: ~45 minutes (15 min US1 + 30 min US4)

**Enhanced MVP** = MVP + US2 (Navbar)
- Adds proper navbar organization
- Estimated time: +45 minutes (90 minutes total)

**Complete Feature** = All 5 user stories
- Full accessibility (light theme)
- Enhanced UX (content buttons)
- Estimated time: 4-6 hours total

---

## Task Execution Checklist

### Before Starting Implementation

- [ ] All setup tasks (T001-T006) completed successfully
- [ ] Development server running at http://localhost:3000
- [ ] Baseline issues documented (T007-T011)
- [ ] Git branch `002-fix-ui-theme` checked out

### During Implementation

- [ ] Mark tasks complete immediately after finishing (not in batches)
- [ ] Test each user story independently after its phase completes
- [ ] Commit after each user story phase with descriptive message
- [ ] Hot reload working (changes reflect without restart)

### After Implementation

- [ ] All 21 acceptance scenarios verified
- [ ] All 10 success criteria met (spec.md)
- [ ] Production build succeeds without errors
- [ ] Cross-browser testing complete
- [ ] Responsive testing complete
- [ ] Performance metrics within targets

---

## Notes

**Testing Approach**: No automated tests requested in spec. All testing is manual verification against acceptance scenarios.

**Swizzling Safety**: US5 uses official Docusaurus "wrap" mode swizzling, which is safe for upgrades and recommended by Docusaurus team.

**CSS Organization**: Changes isolated to specific component CSS files (navbar.css, sidebar.css, custom.css) to minimize global impact.

**Zero Content Changes**: All tasks modify only configuration, CSS, and React components. Documentation content (markdown files) remains unchanged per requirements.

**Rollback Strategy**: Each user story can be reverted independently by reverting its phase's file changes. No database migrations or destructive operations.
