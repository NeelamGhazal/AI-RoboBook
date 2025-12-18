# Feature Specification: RAG Chatbot Frontend Widget

## Metadata

- **Feature ID**: 004-chatbot-widget
- **Feature Name**: Interactive Floating Chat Widget with Tech Cyber Theme
- **Status**: Draft
- **Created**: 2025-12-17
- **Last Updated**: 2025-12-17
- **Owner**: Product Team
- **Stakeholders**: Content Authors, Students, Educators

---

## Executive Summary

### Problem Statement

The Physical AI & Humanoid Robotics textbook (RoboBook) currently lacks an interactive way for readers to ask questions and get instant, contextual answers while studying. Readers must navigate away from their current page to search for information, breaking their learning flow and reducing engagement.

### Proposed Solution

A floating chat widget embedded on all RoboBook pages that connects readers to an AI-powered question-answering system. The widget provides instant answers with source citations, supports asking questions about selected text, and maintains conversation history across sessions.

### Business Value

- **Improved Learning Outcomes**: Students get instant clarification without leaving their reading context
- **Increased Engagement**: Seamless interaction encourages deeper exploration of textbook content
- **Reduced Support Load**: Self-service Q&A reduces instructor/TA questions
- **Enhanced Accessibility**: Conversational interface supports diverse learning styles

### Success Metrics

- 70% of active readers open the widget at least once per session
- Average conversation contains 3+ question-answer exchanges
- 85% of questions receive answers with relevant citations within 3 seconds
- Widget remains accessible and functional on all supported devices and screen sizes

---

## User Scenarios & Testing

### Primary User: Student Reading Textbook

**Scenario 1: General Question While Reading**

1. Student is reading "Module 2: Sensing & Perception" on desktop
2. Encounters unfamiliar term "point cloud processing"
3. Clicks cyan-glowing chat button in bottom-right corner
4. Widget slides open with smooth animation
5. Types question: "What is point cloud processing?"
6. Sees typing indicator with cyan shimmer
7. Receives answer within 3 seconds with 2-3 source citations
8. Clicks citation badge to jump to relevant textbook section
9. Returns to chat to ask follow-up question
10. Widget remembers conversation context

**Acceptance Criteria**:
- Toggle button visible and accessible on all pages
- Widget opens/closes with smooth slide animation (<300ms)
- Typing indicator appears immediately when question submitted
- Answer streams progressively (tokens appear in real-time)
- Citations displayed as clickable cyan badges below answer
- Clicking citation navigates to exact textbook anchor
- Conversation history persists within session
- Widget state (open/closed) persists across page navigation

**Scenario 2: Question About Selected Text**

1. Student reading complex paragraph about "SLAM algorithms"
2. Highlights specific paragraph text
3. Sees "Ask about this" prompt appear near selection
4. Clicks prompt, widget opens with selected text pre-loaded
5. Types question: "Explain this in simpler terms"
6. Receives answer focused on the selected passage
7. Citations link to section containing selected text

**Acceptance Criteria**:
- Text selection triggers "Ask about this" UI element
- Selected text included in chat request context
- Answer demonstrates understanding of selected passage
- Citations prioritize sources from selected text section
- Selected text mode indicated visually in widget

**Scenario 3: Mobile Reading Experience**

1. Student reading on mobile device (portrait orientation)
2. Taps floating chat button
3. Widget expands to full-width panel
4. Types question using mobile keyboard
5. Scrolls through answer and citations
6. Taps citation to navigate (widget closes automatically)
7. Returns to reading, widget remains closed

**Acceptance Criteria**:
- Chat button accessible with thumb on mobile (right side, above navigation)
- Widget uses full screen width on mobile
- Touch-friendly interactive elements (min 44px tap targets)
- Citations close widget when clicked on mobile
- Widget doesn't obscure critical content
- Smooth transitions optimized for mobile performance

**Scenario 4: Session Continuity**

1. Student asks 3 questions, closes browser
2. Returns 2 hours later, opens same page
3. Opens widget, sees previous conversation
4. Asks new question, system maintains context
5. Closes tab, opens different chapter
6. Widget opens with same session, can reference earlier answers

**Acceptance Criteria**:
- Session ID persisted in localStorage
- Conversation history loaded on widget open
- Backend maintains session for minimum 24 hours
- Widget reconnects to existing session automatically
- Clear conversation history option available

**Scenario 5: Error Handling**

1. Student asks question, backend temporarily unavailable
2. Sees clear error message: "Unable to connect. Retrying..."
3. System automatically retries (3 attempts with exponential backoff)
4. If still failing, shows: "Service temporarily unavailable. Try again later."
5. Retry button available for manual attempt
6. Previous conversation history remains visible

**Acceptance Criteria**:
- Network errors handled gracefully without crashing
- Clear, non-technical error messages
- Automatic retry with visible feedback
- Manual retry option always available
- Conversation history preserved during errors
- Widget remains functional for viewing past messages

---

## Functional Requirements

### FR-1: Widget Presence and Visibility

- Widget toggle button must be visible and accessible on every page (documentation, blog, landing page)
- Toggle button fixed position: bottom-right corner, 24px from edges
- Toggle button styling: Circular, cyan icon, scale + glow effect on hover
- Widget persists across page navigation (no re-initialization)
- Widget z-index ensures it appears above all page content

### FR-2: Widget Interaction States

- **Closed State**: Only toggle button visible
- **Opening Animation**: Smooth slide-in from bottom-right (duration: 250-300ms)
- **Open State**: Panel visible with header, message area, input field
- **Closing Animation**: Smooth slide-out to bottom-right (duration: 250-300ms)
- State persists across page navigation within same session

### FR-3: Visual Design and Theming

- Header: Gradient background (primary-cyan → secondary-blue)
- Panel Background: Glassmorphism effect with card-bg variable
- Assistant Messages: Left-aligned, 3px cyan left border accent
- User Messages: Right-aligned, distinct background color
- All interactive elements: Scale transform + cyan glow + shimmer on hover
- Send Button: Gradient background, scale + strong glow on hover
- Typography: Follows RoboBook design system
- Dark Mode Support: Respects system/user theme preference

### FR-4: Chat Functionality

- Text input field with placeholder: "Ask a question about the textbook..."
- Send button (icon + text) enabled only when input has content
- Submit on Enter key (desktop), button tap (mobile)
- Streaming response: Tokens appear progressively as generated
- Typing indicator: Animated cyan shimmer while backend processes
- Message timestamps: Relative format ("2 minutes ago")
- Auto-scroll: Message area scrolls to show latest message

### FR-5: Selected Text Mode

- Text selection on page triggers "Ask about this" UI element
- Element appears near selection (positioned to avoid obscuring text)
- Clicking element opens widget with selected text included in context
- Selected text shown in widget with visual indicator
- Questions receive context-aware answers based on selection
- Citations prioritize sources from selected passage

### FR-6: Source Citations

- Citations displayed as badges below assistant messages
- Badge content: Chapter name + Section name
- Badge styling: Cyan background, clickable, hover effect
- Clicking citation navigates to exact textbook anchor
- Citation hover shows text snippet preview (first 100 characters)
- Maximum 5 citations per answer (backend deduplicates)
- Citations sorted by confidence score (descending)

### FR-7: Session Management

- Session ID generated on first widget open
- Session ID stored in localStorage with key: "robobook_chat_session_id"
- Session persists for 24 hours minimum
- Widget reconnects to existing session on page load
- New session created if stored session expired
- Clear History button creates new session

### FR-8: Conversation History

- Full conversation loaded when widget opens
- Messages displayed in chronological order (oldest first)
- Conversation scrollable (latest message visible by default)
- History includes: user messages, assistant responses, citations, timestamps
- Maximum history: 50 messages (backend pagination if exceeded)
- Clear History action: Deletes current session, starts new one

### FR-9: Error Handling

- Network errors: "Unable to connect. Retrying..."
- Automatic retry: 3 attempts with exponential backoff (1s, 2s, 4s)
- Persistent failure: "Service temporarily unavailable. Try again later."
- Retry button: Manual retry trigger
- Backend errors: "Something went wrong. Please try again."
- Invalid session: Automatically create new session
- Long response timeout (30s): "Response is taking longer than usual..."

### FR-10: Performance Optimization

- Widget loaded lazily (only when user first opens)
- Dynamic import for chat components (code splitting)
- Backend API calls only when widget open
- Throttled API calls: Minimum 500ms between requests
- Cached session data reduces backend calls
- Optimized re-renders (only update changed messages)

### FR-11: Accessibility

- Keyboard navigation: Tab through all interactive elements
- Focus indicators: Visible outline on all focusable elements
- Screen reader support: ARIA labels on all buttons and inputs
- Semantic HTML: Proper heading hierarchy, list structures
- Color contrast: Meets WCAG AA standards (4.5:1 for text)
- Text resize: Widget remains functional at 200% zoom

### FR-12: Mobile Responsiveness

- Toggle button: Touch-friendly size (minimum 48x48px)
- Open widget: Full-width panel on screens <768px
- Message bubbles: Legible font size (minimum 16px)
- Input field: Triggers mobile keyboard appropriately
- Citations: Stack vertically on narrow screens
- Scrolling: Touch-optimized momentum scrolling

### FR-13: SSR/SSG Compatibility

- Widget wrapped in BrowserOnly component (Docusaurus)
- No window/document access during static build
- Client-side only rendering
- Graceful degradation if JavaScript disabled (widget hidden)
- No build-time errors related to chat functionality

### FR-14: Configuration

- Backend API URL: Configurable constant in widget code
- Widget position: Configurable (default: bottom-right)
- Theme colors: Inherit from Docusaurus CSS variables
- Feature flags: Ability to disable selected-text mode, citations
- Session duration: Configurable (default: 24 hours)

---

## Non-Functional Requirements

### Performance

- Widget initial load: <1 second (lazy-loaded)
- Animation frame rate: 60fps for smooth transitions
- Message streaming: Tokens appear within 100ms of receipt
- Backend response time: <3 seconds (target: 1-2 seconds)
- Widget bundle size: <100KB (gzipped)

### Scalability

- Support 1000+ concurrent users without degradation
- Handle conversation histories with 50+ messages
- Graceful handling of slow network connections
- No memory leaks during extended sessions

### Reliability

- 99% uptime for widget rendering
- Graceful fallback when backend unavailable
- No data loss during session (localStorage resilience)
- Automatic reconnection after network disruption

### Security

- Session IDs: Cryptographically secure random UUIDs
- No sensitive data stored in localStorage
- Backend API calls over HTTPS only
- XSS prevention: Sanitize all user input and API responses
- CORS: Backend configured to accept requests from RoboBook domain only

### Compatibility

- Browsers: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- Devices: Desktop, tablet, mobile (iOS 14+, Android 10+)
- Screen sizes: 320px width minimum to 4K displays
- Network: Functional on 3G connections (degraded UX acceptable)

### Maintainability

- Modular component structure
- Clear separation: UI logic, API client, state management
- Comprehensive inline documentation
- Follows Docusaurus and React best practices
- Linting and formatting enforced

---

## Key Entities

### Session

**Purpose**: Represents a user's persistent chat session

**Attributes**:
- session_id: Unique identifier (UUID)
- created_at: Timestamp of session creation
- last_activity: Timestamp of last interaction
- user_id: Optional identifier for authenticated users

### Message

**Purpose**: Represents a single message in conversation

**Attributes**:
- message_id: Unique identifier
- session_id: Reference to parent session
- role: "user" or "assistant"
- content: Message text
- timestamp: When message was sent
- sources: Array of citation objects (assistant messages only)

### Citation

**Purpose**: Source reference for assistant answer

**Attributes**:
- chunk_id: Backend chunk identifier
- chapter: Chapter name/title
- section: Section name/title
- url: Relative URL path to textbook section (with anchor)
- confidence_score: Relevance score (0.0-1.0)
- text_snippet: Preview text (first 100-200 characters)

### WidgetState

**Purpose**: Manages widget UI state

**Attributes**:
- isOpen: Boolean (widget panel visibility)
- isLoading: Boolean (streaming in progress)
- selectedText: String or null (selected text mode)
- error: String or null (current error message)
- messages: Array of Message objects
- session_id: Current session identifier

---

## User Interface Requirements

### Widget Layout Structure

```
┌─────────────────────────────────────┐
│ Header (gradient cyan → blue)       │
│ "RoboBook Assistant"         [X]    │
├─────────────────────────────────────┤
│                                     │
│ [Scrollable Message Area]           │
│                                     │
│  ┌─ Assistant Message ─────────┐   │
│  │ Answer text here...         │   │
│  │ [Badge][Badge][Badge]       │   │
│  │ 2 minutes ago               │   │
│  └─────────────────────────────┘   │
│                                     │
│      ┌─ User Message ──────────┐   │
│      │ Question text here...   │   │
│      │ Just now                │   │
│      └─────────────────────────┘   │
│                                     │
├─────────────────────────────────────┤
│ [Input field placeholder text...]   │
│ [Send Button with icon]        →   │
└─────────────────────────────────────┘
```

### Color Palette (CSS Variables)

- Primary Cyan: `var(--primary-cyan)` (used for accents, borders, glows)
- Secondary Blue: `var(--secondary-blue)` (gradient partner)
- Card Background: `var(--card-bg)` (with transparency for glassmorphism)
- Text Primary: `var(--text-primary)`
- Text Secondary: `var(--text-secondary)`
- Error Red: `var(--error-red)`

### Hover Effects (Mandatory for All Interactive Elements)

1. **Scale Transform**: `transform: scale(1.05)` (button/badge hover)
2. **Cyan Glow**: `box-shadow: 0 0 20px rgba(0, 255, 255, 0.6)` (button/toggle)
3. **Shimmer Animation**: Animated gradient sweep for loading states

### Responsive Breakpoints

- **Desktop**: >1024px - Full widget panel (400px wide, 600px tall)
- **Tablet**: 768px-1024px - Slightly narrower panel (350px wide)
- **Mobile**: <768px - Full-width panel, positioned from bottom

---

## Technical Constraints

### Must Use

- OpenAI ChatKit.js SDK for chat UI components
- Docusaurus BrowserOnly wrapper for SSR/SSG safety
- React (Docusaurus default)
- Fetch API or Axios for backend requests
- localStorage for session persistence

### Must Avoid

- Server-side rendering of widget (client-only)
- Direct DOM manipulation (use React state)
- Inline styles (use CSS modules or styled-components)
- Hardcoded backend URLs (use configuration)
- Synchronous API calls (all async)

### Integration Points

- **Backend API**: `/api/v1/chat/stream` (POST) for streaming responses
- **Backend API**: `/api/v1/sessions` (POST) for session creation
- **Backend API**: `/api/v1/chat/history/{session_id}` (GET) for history
- **Docusaurus**: Global component injection via Root wrapper or theme swizzle
- **RoboBook Theme**: CSS variables from robobook-docusaurus-ui

---

## Dependencies

### External

- Backend RAG API (MVP-complete, documented endpoints)
- OpenAI ChatKit.js SDK (npm package)
- Docusaurus framework (current version)
- RoboBook theme system (CSS variables)

### Internal

- Access to Docusaurus site source code
- Ability to add npm dependencies
- Deployment pipeline for static site

---

## Assumptions

1. Backend API is stable and meets <3s response time target consistently
2. RoboBook uses standard Docusaurus project structure
3. CSS variables for Tech Cyber theme are already defined
4. localStorage is available and not blocked by browser settings
5. Users have JavaScript enabled (graceful degradation if not)
6. Backend handles authentication/authorization if needed (widget is unauthenticated)
7. Backend rate limiting allows reasonable chat usage per session
8. Citation URLs follow consistent anchor pattern (#section-name)
9. Selected text functionality doesn't conflict with other page interactions
10. Widget doesn't need real-time collaboration features (single-user sessions)

---

## Out of Scope

### Explicitly Excluded

- Multi-user chat or collaboration features
- Voice input/output capabilities
- File upload or image sharing
- User authentication within widget (unauthenticated access)
- Chat history export/download
- Custom bot personality configuration
- Integration with external chat platforms (Slack, Discord)
- Admin dashboard for monitoring chat usage
- A/B testing framework within widget
- Internationalization (English only for MVP)

### Future Considerations

- Multi-language support (i18n)
- Voice-to-text input
- Chat history export (PDF, Markdown)
- User feedback mechanism (thumbs up/down on answers)
- Analytics dashboard (usage metrics, popular questions)
- Custom themes per textbook
- Mobile app integration
- Offline mode with cached responses

---

## Risks and Mitigations

### Risk 1: ChatKit.js SDK Integration Complexity

**Impact**: High - Core widget UI depends on SDK
**Probability**: Medium
**Mitigation**:
- Review ChatKit.js documentation thoroughly before implementation
- Create proof-of-concept with basic streaming before full integration
- Have fallback plan: Custom chat UI if SDK incompatible
- Budget extra time for SDK customization to match theme

### Risk 2: Docusaurus SSR/SSG Build Errors

**Impact**: High - Broken builds block deployment
**Probability**: Medium
**Mitigation**:
- Strictly use BrowserOnly wrapper for all widget code
- Test builds frequently during development
- Follow robobook-docusaurus-architect patterns exactly
- Set up CI/CD to catch build errors early

### Risk 3: Mobile Performance Issues

**Impact**: Medium - Poor UX on mobile devices
**Probability**: Medium
**Mitigation**:
- Test on real mobile devices early (not just emulators)
- Use React.memo and useMemo to minimize re-renders
- Implement virtualization for long conversation histories
- Monitor bundle size continuously (<100KB target)

### Risk 4: Backend API Unreliability

**Impact**: High - Widget unusable if backend down
**Probability**: Low (backend is MVP-complete)
**Mitigation**:
- Comprehensive error handling with retry logic
- Clear error messages for users
- Graceful degradation (show cached conversation)
- Circuit breaker pattern for repeated failures

### Risk 5: Theme Style Conflicts

**Impact**: Medium - Widget looks broken or inconsistent
**Probability**: Medium
**Mitigation**:
- Use CSS modules or scoped styles to avoid conflicts
- Test widget on all RoboBook pages (docs, blog, landing)
- Collaborate with robobook-docusaurus-ui maintainer
- Fallback to inline styles if CSS variable issues

### Risk 6: Selected Text Feature Conflicts

**Impact**: Low - Feature fails or interferes with page
**Probability**: Medium
**Mitigation**:
- Detect and avoid conflicts with native browser selection features
- Make "Ask about this" UI dismissible/non-intrusive
- Test on pages with complex layouts and interactions
- Provide option to disable feature if issues arise

---

## Success Criteria

### Measurable Outcomes

1. **Adoption**: 70% of active readers open widget at least once per session
2. **Engagement**: Average conversation length of 3+ question-answer exchanges
3. **Performance**: 85% of questions receive answers within 3 seconds
4. **Reliability**: Widget loads successfully on 99.5% of page visits
5. **Responsiveness**: Widget functional on all screen sizes (320px+)
6. **Accessibility**: Passes WCAG AA automated tests (Lighthouse, axe)
7. **User Satisfaction**: Qualitative feedback indicates widget enhances learning experience

### Qualitative Outcomes

- Students report widget helps them learn faster
- Instructors observe fewer repetitive questions
- Widget feels like natural part of RoboBook experience
- Tech Cyber theme is visually cohesive with site
- Widget works seamlessly across page navigation

---

## Acceptance Criteria

### For Feature Completion

- [ ] Widget toggle button visible on all RoboBook pages
- [ ] Widget opens/closes with smooth animations
- [ ] General Q&A functional with streaming responses
- [ ] Selected text mode functional (highlight → ask → answer)
- [ ] Citations displayed and clickable (navigate to anchors)
- [ ] Session persistence works (localStorage + backend)
- [ ] Conversation history loads correctly
- [ ] Error handling covers all failure scenarios
- [ ] Mobile responsive (full-width panel, touch-friendly)
- [ ] Accessibility standards met (keyboard, screen reader, contrast)
- [ ] SSR/SSG builds succeed without errors
- [ ] Tech Cyber theme styling fully applied
- [ ] All hover effects (scale, glow, shimmer) implemented
- [ ] Performance targets met (bundle size, response time)
- [ ] Integration guide documented
- [ ] Sample code structure provided

---

## Glossary

- **ChatKit.js**: OpenAI's SDK for building chat interfaces with streaming support
- **Docusaurus**: Static site generator used for RoboBook
- **SSR/SSG**: Server-Side Rendering / Static Site Generation
- **BrowserOnly**: Docusaurus component that only renders on client-side
- **Tech Cyber Theme**: RoboBook's design system (cyan/blue, glassmorphism, shimmer effects)
- **RAG**: Retrieval-Augmented Generation (backend AI system)
- **Citation**: Source reference linking to textbook section
- **Session**: Persistent conversation context stored on backend
- **Glassmorphism**: UI design style with frosted glass effect
- **Shimmer**: Animated gradient effect for loading states

---

## Appendices

### A. Backend API Contract

**POST /api/v1/sessions**
- Creates new session
- Response: `{ session_id, created_at, last_activity }`

**POST /api/v1/chat/stream**
- Request: `{ session_id, question, selected_text? }`
- Response: Server-Sent Events stream
  - Event types: `token`, `citations`, `metadata`, `done`, `error`

**GET /api/v1/chat/history/{session_id}**
- Response: Array of messages with role, content, sources, timestamp

### B. Sample Code Structure

```
src/
├── components/
│   └── ChatWidget/
│       ├── index.tsx              # Main widget component
│       ├── ChatToggle.tsx         # Toggle button
│       ├── ChatPanel.tsx          # Collapsible panel
│       ├── MessageList.tsx        # Message display area
│       ├── MessageInput.tsx       # Input field + send button
│       ├── Citation.tsx           # Citation badge component
│       ├── TypingIndicator.tsx   # Loading shimmer
│       ├── ErrorMessage.tsx      # Error display
│       ├── useChat.ts            # Chat logic hook
│       ├── useChatSession.ts     # Session management hook
│       ├── useSelectedText.ts    # Text selection hook
│       ├── chatApi.ts            # Backend API client
│       ├── styles.module.css     # Component styles
│       └── constants.ts          # Configuration
└── theme/
    └── Root.tsx                   # Docusaurus Root wrapper
```

### C. Integration Guide

**Step 1**: Install dependencies
```bash
npm install @openai/chatkit
```

**Step 2**: Add ChatWidget to Docusaurus Root
```tsx
// src/theme/Root.tsx
import React from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';

export default function Root({ children }) {
  return (
    <>
      {children}
      <BrowserOnly>
        {() => {
          const ChatWidget = require('@site/src/components/ChatWidget').default;
          return <ChatWidget />;
        }}
      </BrowserOnly>
    </>
  );
}
```

**Step 3**: Configure backend URL
```ts
// src/components/ChatWidget/constants.ts
export const CHAT_API_URL = process.env.CHAT_API_URL || 'http://localhost:8000';
```

**Step 4**: Build and test
```bash
npm run build
npm run serve
```

---

**Specification Version**: 1.0
**Last Reviewed**: 2025-12-17
**Next Review**: Before implementation phase
