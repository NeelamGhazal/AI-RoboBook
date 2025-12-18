---
id: 0003
title: RAG Chatbot Widget Implementation Tasks Breakdown
stage: tasks
date: 2025-12-17
surface: agent
model: claude-sonnet-4-5
feature: 004-chatbot-widget
branch: 004-chatbot-widget
user: system
command: /sp.tasks
labels: ["tasks", "breakdown", "implementation", "mvp", "user-stories"]
links:
  spec: specs/004-chatbot-widget/spec.md
  plan: specs/004-chatbot-widget/plan.md
  tasks: specs/004-chatbot-widget/tasks.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-chatbot-widget/tasks.md
tests:
  - N/A (task planning phase)
---

## Prompt

```text
Generate detailed implementation tasks for the RAG Chatbot Frontend Widget feature based on the validated plan.md and spec.md.

[Full prompt text preserved from command]
```

## Response

### Implementation Tasks Created

Successfully generated comprehensive task breakdown for RAG Chatbot Frontend Widget (Feature 004-chatbot-widget).

**Tasks Path**: `specs/004-chatbot-widget/tasks.md`

### Task Organization

**Total**: 70 atomic tasks (~120 hours, 15 working days)

**Organized by User Stories**:
- **Phase 1**: Setup & Configuration (4 tasks, 2 hours)
- **Phase 2**: SSR-Safe Global Integration (4 tasks, 3 hours)
- **Phase 3**: US1 - General Q&A with Streaming (18 tasks, 40 hours) **← MVP**
- **Phase 4**: US2 - Selected Text Mode (7 tasks, 12 hours)
- **Phase 5**: US4 - Session Continuity (7 tasks, 8 hours)
- **Phase 6**: US3 - Mobile + US5 - Error Handling (13 tasks, 16 hours)
- **Phase 7**: Polish, Optimization & Final Testing (17 tasks, 24 hours)

### MVP Definition (Phase 1-3)

**Tasks T001-T026** (50 hours, 6-7 days):
- Project setup + TypeScript types
- Docusaurus Root swizzle with BrowserOnly wrapper
- ChatWidget container with React Context
- ChatToggleButton + ChatPanel components
- ChatHeader + MessageList + MessageBubble + CitationBadge
- InputBar with send functionality
- API client with streaming (Fetch + ReadableStream)
- Session management (localStorage + backend)
- Citation click navigation
- End-to-end testing

**MVP Delivers**:
- ✅ Floating toggle button (bottom-right, cyan glow)
- ✅ Chat panel with smooth slide-in animation
- ✅ General Q&A with streaming responses
- ✅ Typing indicator during streaming
- ✅ Citations as clickable cyan badges
- ✅ Navigation to textbook sections on citation click
- ✅ Session persistence across page navigation
- ✅ Tech Cyber theme styling (gradients, glassmorphism)
- ✅ Zero SSR/SSG build errors

### Task Format (Strict Checklist)

Every task follows required format:
```
- [ ] [TaskID] [P?] [Story?] Description with file path
```

**Examples from tasks.md**:
- `- [ ] T001 Create ChatWidget directory structure in src/components/ChatWidget/`
- `- [ ] T011 [P] [US1] Create localStorage utilities in src/components/ChatWidget/utils/localStorage.ts`
- `- [ ] T027 [P] [US2] Create SelectedTextDetector component in src/components/ChatWidget/components/SelectedTextDetector.tsx`

**Format Components**:
- Checkbox: `- [ ]` (markdown checkbox)
- Task ID: T001-T070 (sequential)
- [P] marker: 25 tasks parallelizable
- [Story] label: [US1], [US2], [US3], [US4], [US5] for user story tasks
- Description: Clear action + exact file path

### User Stories Mapped (from spec.md Scenarios)

**US1 - General Question While Reading** (Scenario 1):
- Toggle button → widget opens
- Type question → streaming answer
- Citations displayed → click to navigate
- Conversation context maintained
- **Priority**: MVP (Phase 3)

**US2 - Question About Selected Text** (Scenario 2):
- Highlight text → "Ask about this" tooltip
- Click tooltip → widget opens with context
- Question includes selected_text parameter
- **Priority**: Post-MVP (Phase 4)

**US3 - Mobile Reading Experience** (Scenario 3):
- Full-width panel on mobile (<768px)
- Touch-friendly targets (≥44px)
- Citations close widget on mobile
- **Priority**: Post-MVP (Phase 6)

**US4 - Session Continuity** (Scenario 4):
- Session persists across browser sessions (24hr TTL)
- Conversation history loaded on widget open
- Clear History button available
- **Priority**: Post-MVP (Phase 5)

**US5 - Error Handling** (Scenario 5):
- Network errors show retry UI
- 3 auto-retry attempts with exponential backoff
- Manual retry button available
- **Priority**: Post-MVP (Phase 6)

### Dependency Graph

```
Setup (Phase 1)
  ↓
SSR-Safe Integration (Phase 2)
  ↓
US1 - MVP (Phase 3)
  ↓
├─→ US2 (Phase 4) [Can parallel with US4]
├─→ US4 (Phase 5) [Can parallel with US2]
└─→ US3 + US5 (Phase 6)
  ↓
Polish & Optimization (Phase 7)
```

**Blocking Prerequisites**:
- T001-T008: Setup + SSR (must complete before US1)
- T009-T010: Context (blocks all US1 component tasks)
- T013-T014: Toggle + Panel (blocks UI implementation)

**Parallel Opportunities**:
- Phase 3: T011 || T012 (localStorage || API client)
- Phase 3: T015 || T018 || T021 (Header || CitationBadge || TypingIndicator)
- Phase 4-5: US2 tasks || US4 tasks (independent user stories)
- Phase 7: Performance || Accessibility || Browser testing

### Key Technical Tasks

**SSR/SSG Safety** (Phase 2):
- T005: Swizzle Docusaurus Root.tsx
- T006: Add BrowserOnly wrapper with dynamic import
- T007: Create minimal ChatWidget container (no window/document outside useEffect)
- T008: Verify build succeeds (`npm run build`)

**Streaming Implementation** (Phase 3):
- T012: API client with Fetch + ReadableStream + manual SSE parsing
- T020: useStreamingChat hook (token events → append to message)
- T021: TypingIndicator component (animated cyan dots)
- T022: Integrate streaming into sendMessage action

**Tech Cyber Styling** (Phase 3):
- T003: CSS variables (--chat-primary-cyan, --chat-secondary-blue, --chat-card-bg)
- T013: ChatToggleButton (gradient, scale + glow on hover)
- T014: ChatPanel (glassmorphism, backdrop-filter blur, slide-in animation)
- T018: CitationBadge (pill shape, cyan border, hover brighter)

**Session Management** (Phase 3):
- T011: localStorage utils (24hr TTL, expiration check)
- T023: Session initialization (check localStorage → fetch history or create new)

**Selected Text Detection** (Phase 4):
- T027: SelectedTextDetector (mouseup/touchend listener, throttled 200ms)
- T028: "Ask about this" tooltip (positioned near selection)
- T030: Add selected_text parameter to API call

**Mobile Responsiveness** (Phase 6):
- T041: Mobile styles (full-width panel, 80vh height)
- T042: Mobile toggle button (48px, thumb-reachable)
- T044: Touch target enforcement (≥44px)
- T045: scrollIntoView for input on keyboard focus

**Error Handling** (Phase 6):
- T047: useErrorHandler hook (categorize errors, retry logic)
- T048: ErrorMessage component with retry button
- T050: Auto-retry with exponential backoff (1s, 2s, 4s)
- T051: Timeout handling (30s)

**Performance Optimization** (Phase 7):
- T054: Code splitting with React.lazy()
- T055: React.memo for MessageBubble + CitationBadge
- T056: webpack-bundle-analyzer + optimize imports (<100KB target)
- T057: CSS animation audit (60fps, transform/opacity only)

**Accessibility** (Phase 7):
- T058: ARIA labels on all interactive elements
- T059: Keyboard navigation (Tab, Enter, Esc)
- T060: Screen reader support (semantic HTML, aria-live)
- T061: Color contrast audit (WCAG AA: ≥4.5:1)

### Execution Strategy

**Week 1 (MVP)**:
- Day 1: T001-T012 (Setup, SSR-safe integration, API client)
- Day 2: T013-T019 (UI components: toggle, panel, header, messages, input)
- Day 3: T020-T024 (Streaming, typing indicator, citations)
- Day 4: T025-T026 (Integration, end-to-end testing)
- **Deliverable**: Working chat widget with core functionality

**Week 2 (Features)**:
- Day 1: T027-T033 (Selected text mode)
- Day 2: T034-T040 (Session persistence)
- Day 3: T041-T046 (Mobile responsiveness)
- Day 4: T047-T053 (Error handling)
- **Deliverable**: Full feature set from spec

**Week 3 (Polish)**:
- Day 1: T054-T057 (Performance optimization)
- Day 2: T058-T061 (Accessibility)
- Day 3: T062-T070 (Cross-browser testing, docs, final QA)
- **Deliverable**: Production-ready widget

### Effort Summary

**By Priority**:
- **MVP (P1)**: 35 tasks, ~50 hours (Phases 1-3)
- **High Value (P2)**: 27 tasks, ~36 hours (Phases 4-6)
- **Polish (P3)**: 17 tasks, ~24 hours (Phase 7)

**By Phase**:
- Phase 1: 2 hours (Setup)
- Phase 2: 3 hours (SSR-Safe)
- Phase 3: 40 hours (US1 - MVP)
- Phase 4: 12 hours (US2)
- Phase 5: 8 hours (US4)
- Phase 6: 16 hours (US3 + US5)
- Phase 7: 24 hours (Polish)

**Parallelizable**: 25 tasks marked [P] (30-40% reduction with parallel execution)

### Independent Test Criteria

**Phase 2 (SSR-Safe)**:
- `npm run build` succeeds without SSR errors
- Empty widget renders on all pages after build

**Phase 3 (US1 - MVP)**:
- Click toggle → widget opens with slide animation
- Type question → send → typing indicator appears
- Answer streams progressively
- Citations displayed as clickable badges
- Click citation → navigate + scroll to anchor
- Widget state persists across pages

**Phase 4 (US2)**:
- Highlight text (>10 chars) → tooltip appears
- Click tooltip → widget opens with context
- Send question → selected_text in request
- Answer references selected passage

**Phase 5 (US4)**:
- Close browser → reopen → session persists
- Widget shows previous conversation
- New message maintains context
- Clear History → new session created

**Phase 6 (US3 + US5)**:
- Mobile: Full-width panel, touch targets ≥44px
- Errors: Retry UI, 3 auto-attempts, manual retry

**Phase 7 (Polish)**:
- Bundle size <100KB gzipped
- Lighthouse Performance >90
- WCAG AA compliance
- Cross-browser compatibility verified

### Next Steps

**Recommended Command**:
```bash
# For MVP (hackathon base deliverable):
/sp.implement T001-T026

# Or bootstrap entire project:
/sp.bootstrap 004-chatbot-widget
```

**Stop Point for Hackathon**: After T026 (MVP complete)

**Continue Post-Hackathon**: T027-T070 (features + polish)

## Outcome

- ✅ Impact: Complete task breakdown for RAG Chatbot Frontend Widget with 70 atomic tasks organized by user story. MVP clearly defined (T001-T026, 50 hours). All tasks follow strict checklist format with IDs, parallelization markers, story labels, and file paths. Independent test criteria defined for each phase.

- 🧪 Tests: Test strategy integrated into task breakdown (Phase 3 T026, Phase 4 T033, Phase 5 T040, Phase 6 T046+T053, Phase 7 T062-T070). Total 8 explicit test/QA tasks for manual verification.

- 📁 Files: 2 files created:
  - specs/004-chatbot-widget/tasks.md (comprehensive 70-task breakdown)
  - history/prompts/004-chatbot-widget/0003-chatbot-widget-tasks-breakdown.tasks.prompt.md (this PHR)

- 🔁 Next prompts:
  - `/sp.implement T001-T026` - Implement MVP scope (recommended for hackathon)
  - `/sp.bootstrap 004-chatbot-widget` - Bootstrap entire project
  - Begin implementation with T001 (project setup)

- 🧠 Reflection: Task generation successful with clear MVP boundary and user story organization. Key strengths: (1) Atomic tasks (30-120 min each), (2) Strict checklist format for all 70 tasks, (3) 25 tasks marked parallelizable, (4) Independent test criteria per phase, (5) Clear dependency graph showing US2||US4 parallel execution opportunity. MVP scope (T001-T026) delivers core value quickly (~50 hours) enabling hackathon base deliverable. Post-MVP increments (T027-T070) add selected text, mobile, errors, and polish (~70 hours). Estimated total: 15 working days aligns with plan.md timeline.

## Evaluation notes (flywheel)

- Failure modes observed: None. Task generation successful with comprehensive coverage of all user scenarios from spec.md.

- Graders run and results (PASS/FAIL):
  - Task Format: PASS (all 70 tasks follow checklist format with IDs and file paths)
  - User Story Organization: PASS (tasks grouped by US1-US5 with clear story labels)
  - MVP Definition: PASS (T001-T026 clearly marked, 50-hour estimate)
  - Dependencies: PASS (blocking prerequisites identified, parallel opportunities marked)
  - Acceptance Criteria: PASS (each task has clear, testable acceptance criteria)
  - File Paths: PASS (every implementation task specifies exact file location)

- Prompt variant (if applicable): Standard /sp.tasks workflow with user story organization. Followed strict checklist format requirement. Emphasized MVP-first approach for hackathon timeline.

- Next experiment (smallest change to try): For future task breakdowns, consider adding estimated line counts for each component (e.g., "ChatToggleButton.tsx ~80 lines"). For this feature, file path + acceptance criteria is sufficient granularity.
