---
id: 0002
title: fix-ui-theme-planning
stage: plan
date: 2025-12-16
surface: agent
model: claude-sonnet-4-5
feature: 002-fix-ui-theme
branch: 002-fix-ui-theme
user: neela
command: /sp.plan
labels: ["planning", "ui-fix", "theme", "docusaurus", "css", "swizzling"]
links:
  spec: specs/002-fix-ui-theme/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-fix-ui-theme/plan.md
  - specs/002-fix-ui-theme/research.md
  - specs/002-fix-ui-theme/quickstart.md
tests:
  - Constitution Check completed (all principles COMPLIANT)
  - Post-Design Re-Check completed (approved complexity)
---

## Prompt

```
/sp.plan
```

## Response snapshot

**Planning Phase Complete**: Created comprehensive implementation plan for fixing 5 UI and theme issues in RoboBook Docusaurus site.

**Phase 0 - Research (research.md)**:
- 6 technical decisions documented with rationale and alternatives
- Decision 1: Logo configuration with PNG transparency (config-only, low complexity)
- Decision 2: Navbar layout customization (hybrid: config first, swizzle if needed)
- Decision 3: Light theme CSS variables with WCAG AA compliance verification (8.7:1 contrast)
- Decision 4: Sidebar vertical text fix (CSS diagnostic approach)
- Decision 5: Content buttons placement via DocItem/Layout swizzling (official API)
- Decision 6: Docusaurus swizzling best practices (wrap mode, minimal customization)

**Phase 1 - Design (quickstart.md)**:
- 5 task groups with step-by-step implementation instructions
- Complete code examples for all modifications
- Testing checklists for each task group
- Troubleshooting guide for common issues
- Git workflow and commit message template
- Estimated 4-6 hours total implementation time

**Technical Approach**:
- 60% CSS-only work (logo, light theme, sidebar)
- 20% Configuration changes (docusaurus.config.ts, navbar items)
- 20% Component swizzling (ContentButtons, DocItem/Layout wrapper)
- Zero new npm dependencies required
- ~500-800 LOC modifications total

**Constitution Compliance**:
- ✅ Principle IV: Accessibility & Inclusivity (light/dark themes, responsive, WCAG AA)
- ✅ Principle I: Educational Excellence (content unchanged, navigation improved)
- ✅ Book Platform Requirements (Docusaurus 3.9.2, responsive, sidebar preserved)
- ⚠️ Complexity justified: Swizzling uses official "wrap" mode, supports constitution features

**Project Structure Defined**:
- frontend/docusaurus.config.ts (logo path, navbar config)
- frontend/src/css/custom.css (light theme variables)
- frontend/src/css/components/navbar.css (vertical centering, layout)
- frontend/src/css/components/sidebar.css (horizontal text fix)
- frontend/src/components/ContentButtons/ (NEW: React component)
- frontend/src/theme/DocItem/Layout/ (SWIZZLE: content button injection)

## Outcome

- ✅ Impact: Complete technical plan for 5 discrete UI fixes with zero content modifications, ready for /sp.tasks phase
- 🧪 Tests: Constitution Check passed, Post-Design Re-Check approved, all constraints validated
- 📁 Files: plan.md (169 lines), research.md (450+ lines with 6 decisions), quickstart.md (800+ lines with 5 task groups)
- 🔁 Next prompts: `/sp.tasks` to generate actionable task breakdown with test cases
- 🧠 Reflection: Hybrid approach (config-first, swizzle-when-needed) minimizes complexity while achieving all 23 functional requirements; light theme CSS fully specified with WCAG verification; swizzling justified as official Docusaurus pattern

## Evaluation notes (flywheel)

- Failure modes observed: None - planning phase completed successfully with comprehensive documentation
- Graders run and results (PASS/FAIL): Constitution Check PASS (all principles COMPLIANT), Complexity Tracking APPROVED
- Prompt variant (if applicable): Standard /sp.plan workflow with Phase 0 (research) and Phase 1 (quickstart) completed
- Next experiment (smallest change to try): Proceed to /sp.tasks to create testable, dependency-ordered task breakdown for implementation
