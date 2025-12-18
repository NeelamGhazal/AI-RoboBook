# Implementation Tasks: RAG Chatbot Frontend Widget

## Metadata

- **Feature ID**: 004-chatbot-widget
- **Feature Name**: Interactive Floating Chat Widget with Tech Cyber Theme
- **Total Estimated Effort**: ~120 hours (15 working days)
- **Created**: 2025-12-17
- **Status**: Ready for Implementation

---

## Overview

This document breaks down the implementation of the RAG Chatbot Frontend Widget into atomic, executable tasks organized by user story. Each task is designed to be completable in 30-120 minutes and includes clear acceptance criteria.

**User Stories (Scenarios from spec.md)**:
- **US1**: General Question While Reading (General Q&A + Streaming + Citations) - **MVP**
- **US2**: Question About Selected Text (Selected-text mode)
- **US3**: Mobile Reading Experience (Mobile responsiveness)
- **US4**: Session Continuity (Session persistence)
- **US5**: Error Handling (Error states + retry logic)

**Implementation Strategy**:
- Phase 1-2: Setup + Foundational (prerequisite for all stories)
- Phase 3: US1 (MVP - General Q&A with streaming and citations)
- Phase 4: US2 (Selected text mode)
- Phase 5: US4 (Session persistence)
- Phase 6: US3 (Mobile responsiveness) + US5 (Error handling)
- Phase 7: Polish & Optimization

---

## Phase 1: Project Setup & Configuration

**Goal**: Initialize project structure, configure TypeScript, and set up development environment.

**Duration**: 2-3 hours

### Tasks

- [ ] T001 Create ChatWidget directory structure in src/components/ChatWidget/
  - **Effort**: 15 min
  - **Files**:
    - `src/components/ChatWidget/index.tsx`
    - `src/components/ChatWidget/types.ts`
    - `src/components/ChatWidget/components/` (directory)
    - `src/components/ChatWidget/hooks/` (directory)
    - `src/components/ChatWidget/api/` (directory)
    - `src/components/ChatWidget/utils/` (directory)
    - `src/components/ChatWidget/styles/` (directory)
  - **Acceptance**: All directories exist, index.tsx exports placeholder component

- [ ] T002 Create TypeScript types file with core interfaces in src/components/ChatWidget/types.ts
  - **Effort**: 30 min
  - **Files**: `src/components/ChatWidget/types.ts`
  - **Acceptance**:
    - Message, Citation, Session, StreamEvent, WidgetState interfaces defined
    - All types properly exported
    - No TypeScript errors

- [ ] T003 Set up CSS Modules configuration and variables file in src/components/ChatWidget/styles/variables.module.css
  - **Effort**: 20 min
  - **Files**: `src/components/ChatWidget/styles/variables.module.css`
  - **Acceptance**:
    - CSS variables defined: --chat-primary-cyan, --chat-secondary-blue, --chat-card-bg
    - Fallback values provided for all variables
    - Mobile breakpoint variables defined

- [ ] T004 Create configuration file with API URL and widget options in src/components/ChatWidget/config.ts
  - **Effort**: 15 min
  - **Files**: `src/components/ChatWidget/config.ts`
  - **Acceptance**:
    - ChatWidgetConfig interface defined
    - defaultConfig exported with API URL from env
    - All configuration options documented

---

## Phase 2: Foundational - SSR-Safe Global Integration

**Goal**: Set up Docusaurus Root swizzle with BrowserOnly wrapper and lazy loading.

**Duration**: 3-4 hours

**Independent Test Criteria**:
- Run `npm run build` successfully without SSR errors
- Verify empty widget renders on all pages after build

### Tasks

- [ ] T005 Swizzle Docusaurus Root component by creating src/theme/Root.tsx
  - **Effort**: 20 min
  - **Files**: `src/theme/Root.tsx`
  - **Acceptance**:
    - Root.tsx created with proper export
    - Children prop rendered
    - No build errors

- [ ] T006 Add BrowserOnly wrapper with dynamic import in src/theme/Root.tsx
  - **Effort**: 30 min
  - **Files**: `src/theme/Root.tsx`
  - **Acceptance**:
    - BrowserOnly imported from @docusaurus/BrowserOnly
    - ChatWidget dynamically imported with require() in callback
    - Fallback prop provides empty div
    - `npm run build` succeeds without SSR errors

- [ ] T007 Create minimal ChatWidget container component in src/components/ChatWidget/ChatWidget.tsx
  - **Effort**: 45 min
  - **Files**: `src/components/ChatWidget/ChatWidget.tsx`
  - **Acceptance**:
    - Component exports default function
    - Returns placeholder div with "ChatWidget" text
    - No window/document access outside useEffect
    - Component renders in browser after build

- [ ] T008 Verify SSR/SSG build succeeds and widget appears on all pages
  - **Effort**: 30 min
  - **Acceptance**:
    - Run `npm run build` without errors
    - Run `npm run serve` and check multiple pages
    - Widget placeholder visible on docs, blog, and landing pages
    - No console errors related to window/document

---

## Phase 3: User Story 1 - General Q&A with Streaming (MVP)

**Goal**: Implement core chat functionality with streaming responses and citations.

**Duration**: ~40 hours (5 days)

**Independent Test Criteria**:
- Student can click toggle button, widget opens
- Student can type question and send
- Answer streams progressively with typing indicator
- Citations displayed as clickable badges
- Clicking citation navigates to textbook section
- Widget state persists across page navigation

### Core State Management (Foundational for US1)

- [ ] T009 [US1] Create ChatWidgetContext provider in src/components/ChatWidget/ChatWidgetContext.tsx
  - **Effort**: 60 min
  - **Dependencies**: T002 (types), T007 (container)
  - **Files**: `src/components/ChatWidget/ChatWidgetContext.tsx`
  - **Acceptance**:
    - ChatWidgetContextValue interface defined with all required state/actions
    - Context provider component with useState for widget state
    - useChatWidget hook exported
    - Context wraps children prop

- [ ] T010 [US1] Integrate ChatWidgetContext into ChatWidget.tsx
  - **Effort**: 20 min
  - **Dependencies**: T009
  - **Files**: `src/components/ChatWidget/ChatWidget.tsx`
  - **Acceptance**:
    - ChatWidgetProvider wraps all widget components
    - State accessible via useChatWidget hook
    - No prop drilling required

### API Client Implementation

- [ ] T011 [P] [US1] Create localStorage utilities in src/components/ChatWidget/utils/localStorage.ts
  - **Effort**: 45 min
  - **Dependencies**: T002 (types)
  - **Files**: `src/components/ChatWidget/utils/localStorage.ts`
  - **Acceptance**:
    - getStoredSessionId() checks expiration (24hr TTL)
    - storeSessionId() saves session with timestamps
    - updateSessionActivity() updates last_activity
    - All functions handle errors gracefully (try/catch)

- [ ] T012 [P] [US1] Implement API client module in src/components/ChatWidget/api/chatApi.ts
  - **Effort**: 90 min
  - **Dependencies**: T002 (types), T004 (config)
  - **Files**: `src/components/ChatWidget/api/chatApi.ts`
  - **Acceptance**:
    - createSession() function implemented
    - fetchHistory() function implemented
    - streamChat() function with Fetch + ReadableStream
    - Manual SSE parsing (data: {...} format)
    - onEvent callback for stream events (token, citations, metadata, done)
    - onError callback for failures
    - All functions properly typed

### Toggle Button & Panel Container

- [ ] T013 [US1] Create ChatToggleButton component in src/components/ChatWidget/components/ChatToggleButton.tsx
  - **Effort**: 60 min
  - **Dependencies**: T009 (context), T003 (CSS variables)
  - **Files**:
    - `src/components/ChatWidget/components/ChatToggleButton.tsx`
    - `src/components/ChatWidget/styles/ChatToggleButton.module.css`
  - **Acceptance**:
    - Fixed position bottom-right (24px from edges)
    - 56px circular button (48px on mobile)
    - Gradient background (cyan → blue)
    - Chat bubble SVG icon
    - onClick toggles isOpen state
    - Hover effects: scale(1.05) + cyan glow
    - Z-index 9999

- [ ] T014 [US1] Create ChatPanel container component in src/components/ChatWidget/components/ChatPanel.tsx
  - **Effort**: 75 min
  - **Dependencies**: T009 (context), T003 (CSS variables)
  - **Files**:
    - `src/components/ChatWidget/components/ChatPanel.tsx`
    - `src/components/ChatWidget/styles/ChatPanel.module.css`
  - **Acceptance**:
    - Fixed position bottom-right, 400x600px (desktop)
    - Conditional render when isOpen=true
    - Glassmorphism: backdrop-filter blur(10px)
    - Slide-in animation: translateX(0) when open, translateX(120%) when closed
    - Animation duration 300ms cubic-bezier(0.4, 0, 0.2, 1)
    - Contains ChatHeader, MessageList, InputBar (placeholders)

### Chat Header

- [ ] T015 [P] [US1] Create ChatHeader component in src/components/ChatWidget/components/ChatHeader.tsx
  - **Effort**: 45 min
  - **Dependencies**: T003 (CSS variables)
  - **Files**:
    - `src/components/ChatWidget/components/ChatHeader.tsx`
    - `src/components/ChatWidget/styles/ChatHeader.module.css`
  - **Acceptance**:
    - Height 60px, padding 0 20px
    - Gradient background (cyan → blue)
    - Title: "RoboBook Assistant"
    - Close button (X icon) on right
    - Close button triggers closeWidget() from context
    - Hover effect on close button: scale(1.1) + lighter background

### Message Display Components

- [ ] T016 [US1] Create MessageList component in src/components/ChatWidget/components/MessageList.tsx
  - **Effort**: 60 min
  - **Dependencies**: T009 (context for messages)
  - **Files**:
    - `src/components/ChatWidget/components/MessageList.tsx`
    - `src/components/ChatWidget/styles/MessageList.module.css`
  - **Acceptance**:
    - Scrollable container with flex layout
    - Renders MessageBubble for each message
    - messagesEndRef for auto-scroll
    - useEffect scrolls to bottom on new message
    - Empty state: "Ask a question to get started"
    - Padding and spacing correct

- [ ] T017 [US1] Create MessageBubble component in src/components/ChatWidget/components/MessageBubble.tsx
  - **Effort**: 75 min
  - **Dependencies**: T002 (types), T003 (CSS variables)
  - **Files**:
    - `src/components/ChatWidget/components/MessageBubble.tsx`
    - `src/components/ChatWidget/styles/MessageBubble.module.css`
  - **Acceptance**:
    - User messages: right-aligned, cyan background (opacity 0.2), max-width 70%
    - Assistant messages: left-aligned, 3px cyan border-left, max-width 80%
    - Timestamp displayed (relative format: "2 minutes ago")
    - Citations render below assistant messages (placeholder)
    - Proper border-radius (16px variants)

- [ ] T018 [P] [US1] Create CitationBadge component in src/components/ChatWidget/components/CitationBadge.tsx
  - **Effort**: 60 min
  - **Dependencies**: T002 (Citation type), T003 (CSS variables)
  - **Files**:
    - `src/components/ChatWidget/components/CitationBadge.tsx`
    - `src/components/ChatWidget/styles/CitationBadge.module.css`
  - **Acceptance**:
    - Pill-shaped badge (border-radius 20px)
    - Cyan border and background (opacity 0.15)
    - Content: "Chapter: {chapter} | Section: {section}"
    - Hover: scale(1.05) + brighter background
    - onClick navigates to citation URL
    - Cursor pointer

### Input Bar

- [ ] T019 [US1] Create InputBar component in src/components/ChatWidget/components/InputBar.tsx
  - **Effort**: 90 min
  - **Dependencies**: T009 (context for sendMessage)
  - **Files**:
    - `src/components/ChatWidget/components/InputBar.tsx`
    - `src/components/ChatWidget/styles/InputBar.module.css`
  - **Acceptance**:
    - Flexbox layout: row, align center
    - TextInput: flex 1, placeholder "Ask a question..."
    - SendButton: fixed width 50px, gradient background
    - Enter key triggers send (not Shift+Enter)
    - SendButton disabled when input empty or isStreaming
    - Input clears after send
    - Hover effects on SendButton: scale(1.05) + glow

### Streaming Implementation

- [ ] T020 [US1] Create useStreamingChat hook in src/components/ChatWidget/hooks/useStreamingChat.ts
  - **Effort**: 120 min
  - **Dependencies**: T012 (API client), T009 (context)
  - **Files**: `src/components/ChatWidget/hooks/useStreamingChat.ts`
  - **Acceptance**:
    - Hook manages streaming state (isStreaming, currentMessage)
    - Calls streamChat() from API client
    - Handles token events: appends to assistant message
    - Handles citations events: stores in message
    - Handles metadata events: stores in message
    - Handles done event: finalizes message, enables input
    - Returns sendMessage function
    - Properly cleans up stream on unmount

- [ ] T021 [P] [US1] Create TypingIndicator component in src/components/ChatWidget/components/TypingIndicator.tsx
  - **Effort**: 30 min
  - **Dependencies**: T003 (CSS variables for animation)
  - **Files**:
    - `src/components/ChatWidget/components/TypingIndicator.tsx`
    - `src/components/ChatWidget/styles/TypingIndicator.module.css`
  - **Acceptance**:
    - Three animated dots
    - Cyan color matching theme
    - Animation: typing (opacity + scale)
    - Stagger animation delays (0s, 0.2s, 0.4s)
    - Renders when isStreaming=true

- [ ] T022 [US1] Integrate streaming into sendMessage action in ChatWidgetContext
  - **Effort**: 60 min
  - **Dependencies**: T020 (streaming hook), T009 (context)
  - **Files**: `src/components/ChatWidget/ChatWidgetContext.tsx`
  - **Acceptance**:
    - sendMessage() adds user message immediately (optimistic UI)
    - Calls streaming hook with question
    - Updates assistant message as tokens arrive
    - Stores citations when received
    - Handles errors from streaming
    - Re-enables input after completion

### Session Management

- [ ] T023 [US1] Implement session initialization in ChatWidget.tsx useEffect
  - **Effort**: 75 min
  - **Dependencies**: T011 (localStorage utils), T012 (API client)
  - **Files**: `src/components/ChatWidget/ChatWidget.tsx`
  - **Acceptance**:
    - On mount, checks localStorage for session_id
    - If found and valid, fetches history via API
    - If not found or expired, creates new session via API
    - Stores session_id in localStorage
    - Loads messages into context state
    - Updates sessionId in context

### Citation Navigation

- [ ] T024 [US1] Implement citation click handler in CitationBadge.tsx
  - **Effort**: 30 min
  - **Dependencies**: T018 (CitationBadge component)
  - **Files**: `src/components/ChatWidget/components/CitationBadge.tsx`
  - **Acceptance**:
    - onClick extracts URL from citation prop
    - Uses window.location.href to navigate
    - Browser automatically scrolls to anchor
    - On mobile (<768px), closes widget after navigation

### Phase 3 Integration & Testing

- [ ] T025 [US1] Wire all US1 components together in ChatWidget.tsx
  - **Effort**: 45 min
  - **Dependencies**: T013-T024 (all US1 components)
  - **Files**: `src/components/ChatWidget/ChatWidget.tsx`
  - **Acceptance**:
    - ChatToggleButton always visible
    - ChatPanel renders when isOpen=true
    - ChatHeader, MessageList, InputBar inside ChatPanel
    - All context state flows correctly
    - No TypeScript errors

- [ ] T026 [US1] Manual end-to-end test of general Q&A flow
  - **Effort**: 30 min
  - **Dependencies**: T025 (integration complete)
  - **Acceptance**:
    - Click toggle button → widget opens with animation
    - Type question → send button enabled
    - Click send → typing indicator appears
    - Answer streams progressively
    - Citations displayed below answer
    - Click citation → navigates to correct page/anchor
    - Ask follow-up → conversation context maintained
    - Close widget → state persists
    - Navigate to different page → widget still works

---

## Phase 4: User Story 2 - Selected Text Mode

**Goal**: Add ability to ask questions about selected text on the page.

**Duration**: ~12 hours (1.5 days)

**Independent Test Criteria**:
- Student highlights text on page (>10 chars)
- "Ask about this" tooltip appears near selection
- Clicking tooltip opens widget with selected text context
- Question sent includes selected_text parameter
- Answer references selected passage

### Tasks

- [ ] T027 [P] [US2] Create SelectedTextDetector component in src/components/ChatWidget/components/SelectedTextDetector.tsx
  - **Effort**: 90 min
  - **Dependencies**: T009 (context for setSelectedText)
  - **Files**:
    - `src/components/ChatWidget/components/SelectedTextDetector.tsx`
    - `src/components/ChatWidget/styles/SelectedTextDetector.module.css`
  - **Acceptance**:
    - Listens to mouseup and touchend events
    - Throttled to 200ms
    - Calls window.getSelection()
    - Shows tooltip if text.length > 10
    - Positions tooltip near selection rect
    - Hides tooltip on click outside or selection clear
    - Cleanup removes listeners on unmount

- [ ] T028 [US2] Create "Ask about this" tooltip UI in SelectedTextDetector.tsx
  - **Effort**: 45 min
  - **Dependencies**: T027 (detector component)
  - **Files**: `src/components/ChatWidget/components/SelectedTextDetector.tsx`
  - **Acceptance**:
    - Position: absolute, calculated from selection.getBoundingClientRect()
    - Background: cyan gradient
    - Text: "Ask about this"
    - Border-radius: 8px
    - Hover: scale(1.02)
    - Z-index: 10000 (above widget)

- [ ] T029 [US2] Implement tooltip click handler to open widget with context
  - **Effort**: 45 min
  - **Dependencies**: T028 (tooltip UI)
  - **Files**: `src/components/ChatWidget/components/SelectedTextDetector.tsx`
  - **Acceptance**:
    - onClick calls openWidget() from context
    - Sets selectedText in context state
    - Hides tooltip
    - Widget opens with selected text indicator

- [ ] T030 [US2] Add selectedText parameter to streamChat API call
  - **Effort**: 30 min
  - **Dependencies**: T012 (API client), T029 (selected text context)
  - **Files**: `src/components/ChatWidget/api/chatApi.ts`
  - **Acceptance**:
    - streamChat() includes selected_text in request body
    - Backend receives selected text context
    - API call succeeds with selected_text parameter

- [ ] T031 [US2] Add visual indicator for selected text mode in MessageBubble
  - **Effort**: 30 min
  - **Dependencies**: T017 (MessageBubble), T029 (selected text state)
  - **Files**: `src/components/ChatWidget/components/MessageBubble.tsx`
  - **Acceptance**:
    - User message shows "📄 Selected text mode" label
    - Label styled with cyan color
    - Clear visual distinction from general messages

- [ ] T032 [US2] Integrate SelectedTextDetector into ChatWidget.tsx
  - **Effort**: 20 min
  - **Dependencies**: T027-T031 (all US2 tasks)
  - **Files**: `src/components/ChatWidget/ChatWidget.tsx`
  - **Acceptance**:
    - SelectedTextDetector rendered in ChatWidget
    - Component receives context props
    - No conflicts with widget interactions

- [ ] T033 [US2] Manual test of selected text flow
  - **Effort**: 20 min
  - **Dependencies**: T032 (integration complete)
  - **Acceptance**:
    - Highlight text on page → tooltip appears
    - Click tooltip → widget opens
    - Send question → selected_text included in request
    - Answer references selected passage
    - Citations prioritize selected section

---

## Phase 5: User Story 4 - Session Continuity

**Goal**: Ensure session persists across browser sessions and page navigation.

**Duration**: ~8 hours (1 day)

**Independent Test Criteria**:
- Student closes browser after conversation
- Returns later → session_id still valid
- Opens widget → previous messages loaded
- Conversation context maintained
- Clear History button creates new session

### Tasks

- [ ] T034 [P] [US4] Implement isOpen state persistence in localStorage
  - **Effort**: 30 min
  - **Dependencies**: T011 (localStorage utils), T009 (context)
  - **Files**: `src/components/ChatWidget/ChatWidgetContext.tsx`
  - **Acceptance**:
    - useEffect saves isOpen to localStorage on change (key: 'robobook_chat_open')
    - useEffect restores isOpen on mount
    - Widget state persists across page navigation

- [ ] T035 [P] [US4] Add session expiration check (24hr TTL) in localStorage utils
  - **Effort**: 30 min
  - **Dependencies**: T011 (localStorage utils)
  - **Files**: `src/components/ChatWidget/utils/localStorage.ts`
  - **Acceptance**:
    - getStoredSessionId() calculates hours since lastActivity
    - Returns null if >24 hours
    - Removes expired session from localStorage

- [ ] T036 [US4] Implement automatic session reconnection on widget open
  - **Effort**: 60 min
  - **Dependencies**: T023 (session init), T035 (expiration check)
  - **Files**: `src/components/ChatWidget/ChatWidget.tsx`
  - **Acceptance**:
    - On widget open, checks localStorage for session
    - If valid, fetches history and reconnects
    - If expired, creates new session
    - No user action required

- [ ] T037 [P] [US4] Create ClearHistoryButton component in src/components/ChatWidget/components/ClearHistoryButton.tsx
  - **Effort**: 45 min
  - **Dependencies**: T009 (context for clearHistory)
  - **Files**: `src/components/ChatWidget/components/ClearHistoryButton.tsx`
  - **Acceptance**:
    - Button in ChatHeader (left side)
    - Icon: trash or reset
    - onClick triggers confirmation dialog
    - Confirms before clearing
    - Styled with hover effects

- [ ] T038 [US4] Implement clearHistory action in ChatWidgetContext
  - **Effort**: 45 min
  - **Dependencies**: T037 (clear button), T012 (API client)
  - **Files**: `src/components/ChatWidget/ChatWidgetContext.tsx`
  - **Acceptance**:
    - clearHistory() removes session from localStorage
    - Creates new session via API
    - Clears messages array in state
    - Updates sessionId in state
    - Widget remains open

- [ ] T039 [US4] Add updateSessionActivity call after each message
  - **Effort**: 20 min
  - **Dependencies**: T011 (localStorage utils), T022 (sendMessage)
  - **Files**: `src/components/ChatWidget/ChatWidgetContext.tsx`
  - **Acceptance**:
    - sendMessage() calls updateSessionActivity() after success
    - lastActivity timestamp updated in localStorage
    - Session TTL reset on activity

- [ ] T040 [US4] Manual test of session persistence
  - **Effort**: 30 min
  - **Dependencies**: T034-T039 (all US4 tasks)
  - **Acceptance**:
    - Send 3 messages → close browser → reopen
    - Widget shows previous conversation
    - Send new message → context maintained
    - Navigate to different page → session persists
    - Wait >24 hours → session expired, new session created
    - Click Clear History → new session, messages cleared

---

## Phase 6: User Story 3 (Mobile) + User Story 5 (Error Handling)

**Goal**: Add mobile responsiveness and comprehensive error handling.

**Duration**: ~16 hours (2 days)

**Independent Test Criteria**:
- **US3**: Mobile device (<768px) shows full-width widget, touch targets ≥44px, smooth interactions
- **US5**: Network errors show retry UI, 3 auto-retry attempts with backoff, manual retry available

### Mobile Responsiveness (US3)

- [ ] T041 [P] [US3] Add mobile styles to ChatPanel.module.css
  - **Effort**: 45 min
  - **Dependencies**: T014 (ChatPanel component)
  - **Files**: `src/components/ChatWidget/styles/ChatPanel.module.css`
  - **Acceptance**:
    - @media (max-width: 768px) rule
    - Width: 100vw, Height: 80vh
    - Position: bottom 0, right 0
    - Border-radius: 16px 16px 0 0

- [ ] T042 [P] [US3] Add mobile styles to ChatToggleButton.module.css
  - **Effort**: 20 min
  - **Dependencies**: T013 (toggle button)
  - **Files**: `src/components/ChatWidget/styles/ChatToggleButton.module.css`
  - **Acceptance**:
    - @media (max-width: 768px) rule
    - Size: 48x48px (reduced from 56px)
    - Position: bottom 16px, right 16px

- [ ] T043 [US3] Add mobile-specific citation close behavior
  - **Effort**: 30 min
  - **Dependencies**: T024 (citation click handler)
  - **Files**: `src/components/ChatWidget/components/CitationBadge.tsx`
  - **Acceptance**:
    - onClick checks window.innerWidth < 768
    - If mobile, closes widget after navigation
    - Calls closeWidget() from context

- [ ] T044 [US3] Implement touch target size enforcement (≥44px)
  - **Effort**: 45 min
  - **Dependencies**: T013, T015, T018, T019 (all interactive components)
  - **Files**: Multiple CSS Module files
  - **Acceptance**:
    - Toggle button: min 48px
    - Close button: min 44px
    - Send button: min 44px
    - Citation badges: min 44px height
    - Test with Chrome DevTools mobile emulation

- [ ] T045 [US3] Add scrollIntoView for input on mobile keyboard focus
  - **Effort**: 30 min
  - **Dependencies**: T019 (InputBar)
  - **Files**: `src/components/ChatWidget/components/InputBar.tsx`
  - **Acceptance**:
    - inputRef.current?.scrollIntoView() on focus
    - Delay 300ms to wait for keyboard animation
    - behavior: 'smooth', block: 'center'

- [ ] T046 [US3] Test mobile experience on real devices (iOS + Android)
  - **Effort**: 60 min
  - **Dependencies**: T041-T045 (all mobile tasks)
  - **Acceptance**:
    - Test on iOS Safari (iPhone)
    - Test on Chrome Android
    - All touch targets tappable
    - Keyboard doesn't obscure input
    - Animations smooth (no jank)
    - Widget closes on citation tap

### Error Handling (US5)

- [ ] T047 [P] [US5] Create useErrorHandler hook in src/components/ChatWidget/hooks/useErrorHandler.ts
  - **Effort**: 60 min
  - **Dependencies**: T002 (types)
  - **Files**: `src/components/ChatWidget/hooks/useErrorHandler.ts`
  - **Acceptance**:
    - ErrorState interface (message, type, retryable)
    - handleError() categorizes errors (network, server, timeout, unknown)
    - clearError() resets error state
    - retry() implements exponential backoff (1s, 2s, 4s)
    - Max 3 retry attempts

- [ ] T048 [P] [US5] Create ErrorMessage component in src/components/ChatWidget/components/ErrorMessage.tsx
  - **Effort**: 45 min
  - **Dependencies**: T047 (error handler hook)
  - **Files**:
    - `src/components/ChatWidget/components/ErrorMessage.tsx`
    - `src/components/ChatWidget/styles/ErrorMessage.module.css`
  - **Acceptance**:
    - Display error message from error state
    - Show retry button if retryable
    - Styled with error-red color
    - Retry button has hover effects
    - Renders in MessageList

- [ ] T049 [US5] Integrate error handler into streaming hook
  - **Effort**: 45 min
  - **Dependencies**: T020 (streaming hook), T047 (error handler)
  - **Files**: `src/components/ChatWidget/hooks/useStreamingChat.ts`
  - **Acceptance**:
    - Catches errors from streamChat()
    - Calls handleError() with error
    - Sets error state in context
    - Displays ErrorMessage in UI

- [ ] T050 [US5] Implement automatic retry logic with visible feedback
  - **Effort**: 60 min
  - **Dependencies**: T047 (error handler), T049 (error integration)
  - **Files**: `src/components/ChatWidget/hooks/useErrorHandler.ts`
  - **Acceptance**:
    - retry() called automatically on error
    - User sees "Retrying... (attempt 1/3)" message
    - Exponential backoff delays visible
    - After 3 attempts, shows "Service unavailable"
    - Manual retry button always available

- [ ] T051 [US5] Add timeout handling for long-running streams (30s)
  - **Effort**: 45 min
  - **Dependencies**: T020 (streaming hook)
  - **Files**: `src/components/ChatWidget/hooks/useStreamingChat.ts`
  - **Acceptance**:
    - setTimeout(30000) starts when stream begins
    - If timeout reached, shows "Taking longer than usual..."
    - Stream continues, timeout doesn't abort
    - Timeout cleared on stream completion

- [ ] T052 [US5] Preserve conversation history during errors
  - **Effort**: 30 min
  - **Dependencies**: T049 (error integration), T009 (context)
  - **Files**: `src/components/ChatWidget/ChatWidgetContext.tsx`
  - **Acceptance**:
    - Error doesn't clear messages array
    - Previous messages remain visible
    - User can scroll and read history during error
    - Retry sends new message, doesn't affect history

- [ ] T053 [US5] Manual test of error scenarios
  - **Effort**: 45 min
  - **Dependencies**: T047-T052 (all US5 tasks)
  - **Acceptance**:
    - Disconnect network → "Unable to connect. Retrying..." appears
    - 3 auto-retry attempts with delays
    - "Service unavailable" after failed retries
    - Click Retry button → manual retry works
    - Backend returns 500 → error message shown
    - Long response (>30s) → timeout message shown
    - All errors preserve conversation history

---

## Phase 7: Polish, Optimization & Final Testing

**Goal**: Performance optimization, accessibility, bundle size checks, and comprehensive QA.

**Duration**: ~24 hours (3 days)

### Performance Optimization

- [ ] T054 [P] Implement code splitting with React.lazy() in src/theme/Root.tsx
  - **Effort**: 45 min
  - **Dependencies**: T006 (BrowserOnly setup)
  - **Files**: `src/theme/Root.tsx`
  - **Acceptance**:
    - React.lazy() wraps ChatWidget import
    - Suspense fallback provides loading state
    - Widget bundle loaded only when first opened
    - `npm run build` shows separate chunk for ChatWidget

- [ ] T055 [P] Optimize re-renders with React.memo for message components
  - **Effort**: 60 min
  - **Dependencies**: T017 (MessageBubble), T018 (CitationBadge)
  - **Files**: `src/components/ChatWidget/components/`
  - **Acceptance**:
    - MessageBubble wrapped in React.memo
    - CitationBadge wrapped in React.memo
    - useMemo for expensive calculations
    - useCallback for event handlers
    - DevTools Profiler shows reduced re-renders

- [ ] T056 [P] Run webpack-bundle-analyzer and optimize imports
  - **Effort**: 90 min
  - **Files**: Multiple component files
  - **Acceptance**:
    - Install webpack-bundle-analyzer
    - Generate bundle report
    - Identify large dependencies
    - Replace or tree-shake heavy imports
    - Total bundle size <100KB gzipped

- [ ] T057 [P] Audit and optimize CSS animations for 60fps
  - **Effort**: 60 min
  - **Dependencies**: All CSS Module files
  - **Files**: `src/components/ChatWidget/styles/`
  - **Acceptance**:
    - All animations use transform/opacity only
    - No box-shadow animations (use filter instead)
    - will-change applied sparingly
    - Chrome DevTools Performance shows 60fps
    - No jank during slide-in/out

### Accessibility (WCAG AA)

- [ ] T058 [P] Add ARIA labels to all interactive elements
  - **Effort**: 60 min
  - **Dependencies**: All interactive components
  - **Files**: Multiple component files
  - **Acceptance**:
    - Toggle button: aria-label="Open chat assistant"
    - Close button: aria-label="Close chat"
    - Send button: aria-label="Send message"
    - Input: aria-label="Ask a question"
    - Citation badges: aria-label with chapter/section

- [ ] T059 [P] Implement keyboard navigation (Tab, Enter, Esc)
  - **Effort**: 90 min
  - **Dependencies**: T013-T019 (all interactive components)
  - **Files**: Multiple component files
  - **Acceptance**:
    - Tab navigates through: toggle → input → send → citations → close
    - Enter sends message in input
    - Escape closes widget
    - Focus indicators visible (outline style)
    - No focus traps

- [ ] T060 [P] Add screen reader support with semantic HTML
  - **Effort**: 60 min
  - **Dependencies**: All components
  - **Files**: Multiple component files
  - **Acceptance**:
    - Proper heading hierarchy (h1, h2, h3)
    - role="dialog" on ChatPanel
    - aria-live="polite" on MessageList
    - role="status" on TypingIndicator
    - Screen reader announces new messages

- [ ] T061 [P] Audit color contrast ratios (WCAG AA: ≥4.5:1)
  - **Effort**: 45 min
  - **Dependencies**: All CSS Module files
  - **Files**: `src/components/ChatWidget/styles/`
  - **Acceptance**:
    - Run axe DevTools or Lighthouse
    - All text meets 4.5:1 contrast ratio
    - Cyan text on dark backgrounds legible
    - Error messages high contrast
    - Fix any contrast issues found

### Cross-Browser & Cross-Device Testing

- [ ] T062 Test on Chrome 90+ (Windows + Mac)
  - **Effort**: 30 min
  - **Acceptance**: All features work, no console errors

- [ ] T063 Test on Firefox 88+ (Windows + Mac)
  - **Effort**: 30 min
  - **Acceptance**: All features work, animations smooth

- [ ] T064 Test on Safari 14+ (Mac + iOS)
  - **Effort**: 30 min
  - **Acceptance**: Backdrop-filter works, no iOS-specific bugs

- [ ] T065 Test on Edge 90+ (Windows)
  - **Effort**: 30 min
  - **Acceptance**: All features work, consistent behavior

### Final QA & Documentation

- [ ] T066 Run Lighthouse audit and achieve Performance >90
  - **Effort**: 60 min
  - **Acceptance**:
    - Performance score >90
    - Accessibility score 100
    - Best Practices score >90
    - First Interaction <1s
    - Bundle size <100KB

- [ ] T067 Create integration guide in docs/INTEGRATION_GUIDE.md
  - **Effort**: 90 min
  - **Files**: `docs/INTEGRATION_GUIDE.md`
  - **Acceptance**:
    - Step-by-step Docusaurus integration
    - Environment variable setup
    - Build and deployment instructions
    - Troubleshooting section

- [ ] T068 Create configuration guide in docs/CONFIGURATION.md
  - **Effort**: 60 min
  - **Files**: `docs/CONFIGURATION.md`
  - **Acceptance**:
    - All config options documented
    - Default values listed
    - Examples for common customizations
    - API URL configuration

- [ ] T069 Update README.md with widget features and setup
  - **Effort**: 45 min
  - **Files**: `README.md`
  - **Acceptance**:
    - Feature list
    - Quick start guide
    - Link to integration guide
    - Screenshots or GIFs

- [ ] T070 Final end-to-end test of all user scenarios
  - **Effort**: 120 min
  - **Dependencies**: All implementation tasks
  - **Acceptance**:
    - US1: General Q&A works flawlessly
    - US2: Selected text mode works
    - US3: Mobile experience smooth
    - US4: Session persistence works
    - US5: Error handling graceful
    - All acceptance criteria from spec met

---

## Dependency Graph

### Phase Dependencies

```
Phase 1 (Setup)
  ↓
Phase 2 (SSR-Safe Integration)
  ↓
Phase 3 (US1 - MVP)
  ↓
├─→ Phase 4 (US2 - Selected Text) [Can run in parallel with Phase 5]
├─→ Phase 5 (US4 - Session Continuity) [Can run in parallel with Phase 4]
└─→ Phase 6 (US3 + US5 - Mobile + Errors)
  ↓
Phase 7 (Polish & Optimization)
```

### Task Dependencies Summary

**Blocking Prerequisites** (must complete before user stories):
- T001-T004: Setup
- T005-T008: SSR-Safe integration

**User Story 1 (MVP)** - Core dependencies:
- T009-T010: Context (blocks all US1 tasks)
- T013-T014: Toggle + Panel (blocks UI tasks)
- T016-T017: Message display (blocks streaming)
- T020: Streaming hook (blocks message flow)

**User Story 2** - Depends on US1 completion (T009, T012)

**User Story 4** - Depends on US1 completion (T011, T023)

**User Story 3 + 5** - Depends on US1 completion

**Polish** - Depends on all user stories

---

## Execution Strategy

### MVP First Approach

**MVP Milestone** (Phases 1-3): ~50 hours (6-7 days)
- Tasks T001-T026: Setup + SSR + General Q&A + Streaming + Citations
- Delivers: Working chat widget with core functionality
- **Stop here for hackathon base deliverable**

**Post-MVP Increments**:
1. **Selected Text Mode** (Phase 4): +12 hours
   - Tasks T027-T033
   - Adds: Highlight text → "Ask about this" → contextual answers

2. **Session Persistence** (Phase 5): +8 hours
   - Tasks T034-T040
   - Adds: Conversation history across browser sessions

3. **Mobile + Errors** (Phase 6): +16 hours
   - Tasks T041-T053
   - Adds: Mobile responsiveness + error handling

4. **Polish** (Phase 7): +24 hours
   - Tasks T054-T070
   - Adds: Performance optimization + accessibility + testing

### Parallel Execution Opportunities

**Phase 3 (US1) Parallel Tasks**:
- T011 (localStorage utils) || T012 (API client)
- T015 (ChatHeader) || T018 (CitationBadge) || T021 (TypingIndicator)

**Phase 4-5 Parallel Execution**:
- US2 tasks (T027-T033) can run in parallel with US4 tasks (T034-T040)
- Different components, no shared dependencies

**Phase 7 Parallel Tasks**:
- T054-T057 (Performance) || T058-T061 (Accessibility)
- T062-T065 (Browser testing) can run concurrently

### Suggested Task Order

**Week 1** (MVP):
- Day 1: T001-T012 (Setup, SSR, API client)
- Day 2: T013-T019 (UI components)
- Day 3: T020-T024 (Streaming, citations)
- Day 4: T025-T026 (Integration, testing)

**Week 2** (Features):
- Day 1: T027-T033 (Selected text mode)
- Day 2: T034-T040 (Session persistence)
- Day 3: T041-T046 (Mobile responsiveness)
- Day 4: T047-T053 (Error handling)

**Week 3** (Polish):
- Day 1: T054-T057 (Performance optimization)
- Day 2: T058-T061 (Accessibility)
- Day 3: T062-T070 (Testing, docs, QA)

---

## Effort Summary

**Total Tasks**: 70
**Total Estimated Effort**: ~120 hours (15 working days)

**By Phase**:
- Phase 1 (Setup): 4 tasks, 2 hours
- Phase 2 (SSR-Safe): 4 tasks, 3 hours
- Phase 3 (US1 - MVP): 18 tasks, 40 hours
- Phase 4 (US2): 7 tasks, 12 hours
- Phase 5 (US4): 7 tasks, 8 hours
- Phase 6 (US3 + US5): 13 tasks, 16 hours
- Phase 7 (Polish): 17 tasks, 24 hours

**By Priority**:
- **MVP (P1)**: Phases 1-3, ~50 hours (35 tasks)
- **High Value (P2)**: Phases 4-6, ~36 hours (27 tasks)
- **Polish (P3)**: Phase 7, ~24 hours (17 tasks)

**Parallelizable Tasks**: 25 tasks marked with [P]

---

## Next Steps

1. **For MVP Development**:
   ```bash
   # Start with Phase 1-2 setup
   # Then implement Phase 3 tasks T009-T026
   # Stop at T026 for hackathon base deliverable
   ```

2. **For Full Feature**:
   ```bash
   # After MVP, continue with Phase 4-7
   # Prioritize based on user feedback
   ```

3. **Recommended Command**:
   ```bash
   # Begin implementation:
   /sp.implement T001-T026  # MVP scope

   # Or bootstrap entire project:
   /sp.bootstrap 004-chatbot-widget
   ```

---

**Tasks Document Version**: 1.0
**Last Updated**: 2025-12-17
**Status**: Ready for Implementation
