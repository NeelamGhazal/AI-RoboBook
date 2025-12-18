# Implementation Plan: RAG Chatbot Frontend Widget

## Metadata

- **Feature ID**: 004-chatbot-widget
- **Plan Version**: 1.0
- **Created**: 2025-12-17
- **Last Updated**: 2025-12-17
- **Status**: Draft
- **Architect**: AI Planning Agent
- **Related Documents**:
  - Specification: `specs/004-chatbot-widget/spec.md`
  - Research: `specs/004-chatbot-widget/research.md` (to be created)
  - Data Model: `specs/004-chatbot-widget/data-model.md` (to be created)

---

## Executive Summary

### Architectural Overview

This plan details the technical architecture for integrating an interactive floating chat widget into the RoboBook Docusaurus site. The widget provides AI-powered Q&A with streaming responses, source citations, and selected-text querying.

**Core Technical Challenges**:
1. **SSR/SSG Compatibility**: Docusaurus static generation requires careful client-side-only rendering
2. **ChatKit.js Integration**: Balancing SDK capabilities with custom Tech Cyber theme requirements
3. **Performance**: Lazy loading, code splitting, and bundle size optimization (<100KB target)
4. **Cross-Page Persistence**: Maintaining widget state during Docusaurus page navigation
5. **Selected Text Detection**: Global event listener without impacting page performance

**Key Architectural Decisions**:
- **Custom UI over ChatKit.js SDK**: Build lightweight custom React components for full theme control
- **React Context + useState**: Simple state management (no Redux/Zustand overhead)
- **CSS Modules**: Scoped styling with CSS variable integration for theme consistency
- **EventSource API**: Native Server-Sent Events for streaming (no library needed)
- **Docusaurus Root Swizzle**: Cleanest global injection method

### Success Criteria

**Technical**:
- Zero SSR/SSG build errors
- Bundle size <100KB gzipped (widget + dependencies)
- First interaction <1s (lazy loading)
- 60fps animations (slide-in, hover effects)
- WCAG AA compliance (automated + manual testing)

**Functional**:
- All 14 functional requirements from spec implemented
- All 5 user scenarios pass acceptance criteria
- <3s backend response time maintained
- Cross-browser compatibility (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)

---

## Technical Context

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    RoboBook Docusaurus Site                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Docusaurus Root (src/theme/Root.tsx)                 │  │
│  │  ├── BrowserOnly Wrapper                              │  │
│  │  │   └── ChatWidget (Lazy Loaded)                     │  │
│  │  │       ├── ChatToggleButton (always visible)        │  │
│  │  │       └── ChatPanel (conditional render)           │  │
│  │  │           ├── ChatHeader                           │  │
│  │  │           ├── MessageList                          │  │
│  │  │           │   └── MessageBubble[]                  │  │
│  │  │           │       └── CitationBadge[]              │  │
│  │  │           └── InputBar                             │  │
│  │  │               ├── TextInput                        │  │
│  │  │               └── SendButton                       │  │
│  │  ├── SelectedTextDetector (global listener)          │  │
│  │  └── Docusaurus Page Content                         │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS (EventSource + Fetch)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              RAG Backend API (FastAPI)                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  POST /api/v1/sessions                                │  │
│  │  POST /api/v1/chat/stream (Server-Sent Events)        │  │
│  │  GET /api/v1/chat/history/{session_id}                │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Frontend Framework**:
- React 18+ (Docusaurus default)
- TypeScript (type safety, better DX)
- CSS Modules (scoped styling, no CSS-in-JS overhead)

**State Management**:
- React Context API for global widget state
- useState/useReducer for local component state
- localStorage for session persistence (native Web Storage API)

**HTTP Client**:
- Native Fetch API for REST calls
- Native EventSource API for Server-Sent Events streaming
- No axios/ky needed (reduce bundle size)

**Styling**:
- CSS Modules with `.module.css` files
- CSS Variables from robobook-docusaurus-ui theme
- CSS animations (transition, transform, keyframes)

**Build Integration**:
- Docusaurus v3.x plugin system
- Webpack (Docusaurus default bundler)
- Code splitting via React.lazy() and dynamic import()

### Integration Points

**1. Docusaurus Integration**:
- **Method**: Theme swizzling (`src/theme/Root.tsx`)
- **Reason**: Cleanest way to inject global component, persists across all pages
- **Alternative**: Custom plugin (more complex, overkill for this use case)

**2. Backend API Integration**:
```typescript
// API Endpoints
POST   /api/v1/sessions
       → { session_id, created_at, last_activity }

POST   /api/v1/chat/stream
       Body: { session_id, question, selected_text? }
       → Server-Sent Events:
         data: {"type":"token","content":"..."}
         data: {"type":"citations","citations":[...]}
         data: {"type":"metadata","metadata":{...}}
         data: {"type":"done"}

GET    /api/v1/chat/history/{session_id}
       → [ { role, content, sources, created_at }, ... ]
```

**3. Theme Integration**:
- CSS Variables from `src/css/custom.css` (robobook-docusaurus-ui)
- Primary: `--primary-cyan`, `--secondary-blue`
- Backgrounds: `--card-bg`, `--background-color`
- Text: `--text-primary`, `--text-secondary`

### Data Flow

```
User Action: Click Toggle Button
  ↓
Widget State: isOpen = true
  ↓
useEffect: Check localStorage for session_id
  ↓
  ├─ Found → Fetch /api/v1/chat/history/{session_id}
  │          ↓
  │          Load messages into state
  ↓
  └─ Not Found → POST /api/v1/sessions
                 ↓
                 Store session_id in localStorage

User Action: Type question + Send
  ↓
Add user message to state (optimistic UI)
  ↓
POST /api/v1/chat/stream with EventSource
  ↓
  ├─ Event: type="token" → Append to assistant message
  ├─ Event: type="citations" → Store citations array
  ├─ Event: type="metadata" → Store metadata
  └─ Event: type="done" → Finalize message, enable input

User Action: Click citation badge
  ↓
Extract URL from citation (e.g., "/docs/module-1#ros-2-nodes")
  ↓
Navigate to URL (window.location.href or router.push)
  ↓
Browser scrolls to anchor (#ros-2-nodes)

User Action: Select text on page
  ↓
SelectedTextDetector: window.getSelection()
  ↓
Selection length > 10 chars?
  ├─ Yes → Show "Ask about this" tooltip
  │        ↓
  │        User clicks → Open widget, set selectedText state
  ↓
  └─ No → Hide tooltip

Widget Close (user clicks X or mobile citation)
  ↓
Widget State: isOpen = false
  ↓
Play slide-out animation
  ↓
Unmount ChatPanel (cleanup listeners)
```

---

## Phase 0: Research & Technical Decisions

### Research Tasks

#### R1: Docusaurus SSR/SSG Best Practices

**Question**: What is the safest pattern for injecting client-only components in Docusaurus v3.x?

**Research Findings**:
- **BrowserOnly Component**: Official Docusaurus component that only renders on client
- **Theme Swizzling**: `src/theme/Root.tsx` is the recommended injection point for global components
- **Dynamic Import**: Use React.lazy() with Suspense for code splitting
- **useEffect Hook**: All browser APIs (window, document, localStorage) must be inside useEffect

**Decision**: Use BrowserOnly + theme swizzling with dynamic import

**Implementation Pattern**:
```tsx
// src/theme/Root.tsx
import React from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';

export default function Root({ children }) {
  return (
    <>
      {children}
      <BrowserOnly fallback={<div />}>
        {() => {
          const ChatWidget = require('@site/src/components/ChatWidget').default;
          return <ChatWidget />;
        }}
      </BrowserOnly>
    </>
  );
}
```

#### R2: OpenAI ChatKit.js SDK Evaluation

**Question**: Can ChatKit.js be customized to match Tech Cyber theme requirements?

**Research Findings**:
- ChatKit.js is designed for OpenAI-styled interfaces (white/gray theme)
- Limited customization options (CSS overrides only)
- Does not support Server-Sent Events streaming format (expects OpenAI's format)
- Heavy bundle size (~150KB) for limited benefit

**Decision**: Build custom lightweight React UI instead of using ChatKit.js

**Rationale**:
1. **Theme Control**: Full control over glassmorphism, gradients, shimmer effects
2. **Bundle Size**: Custom implementation ~40KB vs ChatKit.js ~150KB
3. **Streaming Format**: Backend uses custom SSE format, not OpenAI's format
4. **Simplicity**: Fewer abstractions, easier to debug and maintain

**Alternative Considered**: Fork ChatKit.js and heavily customize (rejected due to maintenance burden)

#### R3: Server-Sent Events Streaming Implementation

**Question**: What is the most reliable way to handle SSE streaming in React?

**Research Findings**:
- Native EventSource API supported in all modern browsers
- EventSource automatically reconnects on connection loss
- Simple API: `new EventSource(url)`, `.onmessage`, `.onerror`
- No external library needed (fetch-event-source not required)

**Decision**: Use native EventSource API

**Implementation Pattern**:
```typescript
const eventSource = new EventSource(
  `${API_URL}/api/v1/chat/stream?session_id=${sessionId}&question=${encodeURIComponent(question)}`
);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);

  switch (data.type) {
    case 'token':
      appendToken(data.content);
      break;
    case 'citations':
      setCitations(data.citations);
      break;
    case 'done':
      eventSource.close();
      break;
  }
};

eventSource.onerror = () => {
  eventSource.close();
  handleError();
};
```

**Note**: Backend expects POST request, so we'll need to use fetch + readableStream instead:

```typescript
const response = await fetch(`${API_URL}/api/v1/chat/stream`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ session_id, question, selected_text }),
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value);
  const lines = chunk.split('\n');

  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));
      handleEvent(data);
    }
  }
}
```

#### R4: Selected Text Detection Performance

**Question**: How to detect text selection without impacting page performance?

**Research Findings**:
- `window.getSelection()` is fast (< 1ms)
- `selectionchange` event fires frequently (every selection change)
- Throttling required to avoid performance issues
- Best to use `mouseup` event instead of `selectionchange`

**Decision**: Listen to `mouseup` + `touchend` events, throttled to 200ms

**Implementation Pattern**:
```typescript
useEffect(() => {
  let timeoutId: NodeJS.Timeout;

  const handleSelectionChange = () => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => {
      const selection = window.getSelection();
      const text = selection?.toString().trim();

      if (text && text.length > 10) {
        // Show "Ask about this" tooltip
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();
        setTooltipPosition({ x: rect.right, y: rect.bottom });
        setSelectedText(text);
      } else {
        setSelectedText(null);
      }
    }, 200);
  };

  document.addEventListener('mouseup', handleSelectionChange);
  document.addEventListener('touchend', handleSelectionChange);

  return () => {
    document.removeEventListener('mouseup', handleSelectionChange);
    document.removeEventListener('touchend', handleSelectionChange);
    clearTimeout(timeoutId);
  };
}, []);
```

#### R5: Animation Performance Optimization

**Question**: How to achieve 60fps animations for slide-in/out and hover effects?

**Research Findings**:
- CSS transforms (translate, scale) trigger GPU acceleration
- Opacity changes are cheaper than width/height changes
- Use `will-change` CSS property sparingly (only on interactive elements)
- Avoid animating box-shadow (use filter: drop-shadow or pseudo-elements)

**Decision**: Use CSS transforms + transitions for all animations

**Implementation Patterns**:
```css
/* Slide-in animation */
.chatPanel {
  transform: translateX(0);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.chatPanel.closed {
  transform: translateX(120%);
}

/* Hover effects */
.button {
  transform: scale(1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.button:hover {
  transform: scale(1.05);
  box-shadow: 0 0 20px var(--primary-cyan);
}

/* Shimmer effect (loading indicator) */
@keyframes shimmer {
  0% { background-position: -200% center; }
  100% { background-position: 200% center; }
}

.loading {
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(0, 255, 255, 0.3) 50%,
    transparent 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
```

### Technical Decisions Summary

| Decision | Chosen Approach | Rationale |
|----------|----------------|-----------|
| ChatKit.js SDK | **Don't use** - Build custom UI | Theme control, bundle size, streaming format mismatch |
| State Management | **React Context + useState** | Simple, no Redux overhead, sufficient for widget scope |
| Styling | **CSS Modules** | Scoped, no runtime cost, easy CSS variable integration |
| HTTP Client | **Native Fetch API** | No external dependency, standard browser API |
| Streaming | **Fetch + ReadableStream** | POST support, manual SSE parsing, reconnection control |
| Docusaurus Integration | **Theme swizzling (Root.tsx)** | Official pattern, persists across pages, clean |
| Code Splitting | **React.lazy() + dynamic import** | Bundle size optimization, load on demand |
| Text Selection | **mouseup/touchend + throttle** | Performance, avoids selectionchange overhead |
| Animations | **CSS transforms + transitions** | GPU accelerated, 60fps, declarative |
| Session Storage | **localStorage** | Native API, persistent, synchronous |

---

## Component Architecture

### Component Hierarchy

```
ChatWidget (Container)
  ├── ChatWidgetContext (State Provider)
  │     └── value: { isOpen, toggleWidget, session, messages, ... }
  │
  ├── ChatToggleButton
  │     ├── Props: onClick, isOpen
  │     └── Renders: Floating button (always visible)
  │
  ├── ChatPanel (Conditional: when isOpen)
  │     ├── ChatHeader
  │     │     ├── Title: "RoboBook Assistant"
  │     │     └── CloseButton
  │     │
  │     ├── MessageList
  │     │     ├── Props: messages[]
  │     │     ├── Ref: messagesEndRef (auto-scroll)
  │     │     └── Children:
  │     │         └── MessageBubble (foreach message)
  │     │               ├── Props: role, content, sources, timestamp
  │     │               ├── Renders: User message (right) OR Assistant message (left)
  │     │               └── Children (if assistant):
  │     │                   └── CitationBadge[] (foreach source)
  │     │                         ├── Props: chapter, section, url, score
  │     │                         └── onClick: Navigate to url
  │     │
  │     ├── TypingIndicator (Conditional: when isStreaming)
  │     │     └── Renders: Shimmer animation
  │     │
  │     └── InputBar
  │           ├── TextInput
  │           │     ├── Placeholder: "Ask a question..."
  │           │     ├── onKeyPress: Send on Enter
  │           │     └── value: inputText
  │           │
  │           └── SendButton
  │                 ├── disabled: !inputText || isStreaming
  │                 └── onClick: handleSend()
  │
  └── SelectedTextDetector (Separate, global)
        ├── useEffect: Listen to mouseup/touchend
        ├── State: selectedText, tooltipPosition
        └── Renders: "Ask about this" tooltip (conditional)
              └── onClick: Open widget, set context
```

### Component Specifications

#### ChatWidget.tsx

**Purpose**: Root container, provides context, manages global state

**State**:
```typescript
interface WidgetState {
  isOpen: boolean;
  sessionId: string | null;
  messages: Message[];
  isStreaming: boolean;
  error: string | null;
  selectedText: string | null;
}
```

**Responsibilities**:
- Initialize session on mount (fetch from localStorage or create new)
- Provide ChatWidgetContext to all children
- Handle widget open/close logic
- Persist isOpen state across page navigation (useEffect + history API)

**Key Hooks**:
- `useState` for local state
- `useEffect` for session initialization
- `useCallback` for memoized handlers

#### ChatToggleButton.tsx

**Purpose**: Always-visible floating button in bottom-right corner

**Props**:
```typescript
interface ChatToggleButtonProps {
  isOpen: boolean;
  onClick: () => void;
  unreadCount?: number; // Future: Badge for unread messages
}
```

**Styling**:
- Position: fixed, bottom: 24px, right: 24px
- Size: 56px x 56px (desktop), 48px x 48px (mobile)
- Background: Gradient (cyan → blue)
- Icon: Chat bubble SVG
- Hover: scale(1.05) + cyan glow (box-shadow: 0 0 20px cyan)
- Active: scale(0.95)
- Z-index: 9999

#### ChatPanel.tsx

**Purpose**: Collapsible panel containing chat interface

**Props**:
```typescript
interface ChatPanelProps {
  isOpen: boolean;
  onClose: () => void;
}
```

**Styling**:
- Position: fixed, bottom: 90px, right: 24px
- Size: 400px x 600px (desktop), 100vw x 80vh (mobile)
- Background: var(--card-bg) with backdrop-filter: blur(10px) (glassmorphism)
- Border-radius: 16px (desktop), 16px 16px 0 0 (mobile)
- Box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3)
- Animation: translateX(0) when open, translateX(120%) when closed (300ms cubic-bezier)

**Layout**:
```
┌────────────────────────────────┐
│ Header (gradient)       [X]    │ ← 60px height
├────────────────────────────────┤
│                                │
│ Message List (scrollable)      │ ← flex: 1 (fills space)
│                                │
│                                │
├────────────────────────────────┤
│ Input Bar                      │ ← 70px height
└────────────────────────────────┘
```

#### MessageList.tsx

**Purpose**: Scrollable container for messages with auto-scroll

**Props**:
```typescript
interface MessageListProps {
  messages: Message[];
  isStreaming: boolean;
}
```

**Responsibilities**:
- Render MessageBubble for each message
- Auto-scroll to bottom on new message (useEffect + messagesEndRef)
- Show TypingIndicator when isStreaming
- Handle empty state (welcome message)

**Auto-scroll Logic**:
```typescript
const messagesEndRef = useRef<HTMLDivElement>(null);

useEffect(() => {
  messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
}, [messages]);
```

#### MessageBubble.tsx

**Purpose**: Individual message display (user or assistant)

**Props**:
```typescript
interface MessageBubbleProps {
  role: 'user' | 'assistant';
  content: string;
  sources?: Citation[];
  timestamp: string;
}
```

**Styling**:
- **User Message**:
  - Align: right
  - Background: var(--primary-cyan) with opacity 0.2
  - Text color: var(--text-primary)
  - Border-radius: 16px 16px 4px 16px
  - Max-width: 70%

- **Assistant Message**:
  - Align: left
  - Background: var(--card-bg)
  - Border-left: 3px solid var(--primary-cyan)
  - Text color: var(--text-primary)
  - Border-radius: 16px 16px 16px 4px
  - Max-width: 80%

**Citation Rendering**:
- If sources exist, render CitationBadge[] below message
- Layout: Flexbox, wrap, gap: 8px

#### CitationBadge.tsx

**Purpose**: Clickable badge linking to textbook section

**Props**:
```typescript
interface CitationBadgeProps {
  chapter: string;
  section: string;
  url: string;
  confidenceScore: number;
}
```

**Styling**:
- Background: var(--primary-cyan) with opacity 0.15
- Border: 1px solid var(--primary-cyan)
- Border-radius: 20px (pill shape)
- Padding: 6px 12px
- Font-size: 12px
- Hover: scale(1.05) + brighter background (opacity 0.25)
- Cursor: pointer

**Content**:
```
Chapter: Module 1 | Section: ROS 2 Nodes
```

**onClick Handler**:
```typescript
const handleClick = () => {
  // Navigate to URL (e.g., "/docs/module-1#ros-2-nodes")
  window.location.href = url;

  // On mobile, close widget after navigation
  if (window.innerWidth < 768) {
    onClose();
  }
};
```

#### InputBar.tsx

**Purpose**: Text input and send button

**Props**:
```typescript
interface InputBarProps {
  onSend: (message: string) => void;
  disabled: boolean;
}
```

**State**:
```typescript
const [inputText, setInputText] = useState('');
```

**Layout**:
- Flexbox: row, align: center
- TextInput: flex: 1
- SendButton: fixed width 50px

**Keyboard Handling**:
```typescript
const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
  if (e.key === 'Enter' && !e.shiftKey && !disabled) {
    e.preventDefault();
    handleSend();
  }
};
```

#### SelectedTextDetector.tsx

**Purpose**: Global listener for text selection, shows "Ask about this" tooltip

**State**:
```typescript
interface SelectedTextState {
  text: string | null;
  position: { x: number; y: number } | null;
}
```

**Responsibilities**:
- Listen to mouseup/touchend events (throttled 200ms)
- Get selection via window.getSelection()
- Show tooltip if text.length > 10
- Position tooltip near selection
- Hide tooltip on click outside or selection clear

**Tooltip Styling**:
- Position: absolute (calculated from selection rect)
- Background: var(--primary-cyan)
- Color: white
- Border-radius: 8px
- Padding: 8px 16px
- Box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2)
- Hover: scale(1.02)
- Z-index: 10000 (above widget)

**onClick Handler**:
```typescript
const handleAskAboutThis = () => {
  // Open widget
  openWidget();

  // Set selected text context
  setSelectedTextContext(text);

  // Hide tooltip
  setSelectedText(null);
};
```

---

## State Management Design

### Context Structure

```typescript
// src/components/ChatWidget/ChatWidgetContext.tsx

interface ChatWidgetContextValue {
  // Widget State
  isOpen: boolean;
  toggleWidget: () => void;
  closeWidget: () => void;

  // Session
  sessionId: string | null;
  isLoadingSession: boolean;

  // Messages
  messages: Message[];
  addMessage: (message: Message) => void;
  updateLastMessage: (content: string) => void;

  // Streaming
  isStreaming: boolean;
  startStreaming: () => void;
  stopStreaming: () => void;

  // Selected Text
  selectedText: string | null;
  setSelectedText: (text: string | null) => void;

  // Error
  error: string | null;
  setError: (error: string | null) => void;

  // Actions
  sendMessage: (content: string) => Promise<void>;
  loadHistory: () => Promise<void>;
  clearHistory: () => Promise<void>;
}

const ChatWidgetContext = createContext<ChatWidgetContextValue | null>(null);

export const useChatWidget = () => {
  const context = useContext(ChatWidgetContext);
  if (!context) {
    throw new Error('useChatWidget must be used within ChatWidgetProvider');
  }
  return context;
};
```

### localStorage Schema

```typescript
// Key: 'robobook_chat_session_id'
// Value: string (UUID)
interface StoredSession {
  sessionId: string;
  createdAt: string; // ISO timestamp
  lastActivity: string; // ISO timestamp
}

// Helpers
const SESSION_KEY = 'robobook_chat_session_id';

const getStoredSessionId = (): string | null => {
  try {
    const stored = localStorage.getItem(SESSION_KEY);
    if (!stored) return null;

    const session: StoredSession = JSON.parse(stored);

    // Check if session expired (>24 hours)
    const lastActivity = new Date(session.lastActivity);
    const now = new Date();
    const hoursSince = (now.getTime() - lastActivity.getTime()) / (1000 * 60 * 60);

    if (hoursSince > 24) {
      localStorage.removeItem(SESSION_KEY);
      return null;
    }

    return session.sessionId;
  } catch {
    return null;
  }
};

const storeSessionId = (sessionId: string) => {
  const session: StoredSession = {
    sessionId,
    createdAt: new Date().toISOString(),
    lastActivity: new Date().toISOString(),
  };
  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
};

const updateSessionActivity = () => {
  try {
    const stored = localStorage.getItem(SESSION_KEY);
    if (!stored) return;

    const session: StoredSession = JSON.parse(stored);
    session.lastActivity = new Date().toISOString();
    localStorage.setItem(SESSION_KEY, JSON.stringify(session));
  } catch {
    // Ignore errors
  }
};
```

---

## API Integration Design

### API Client Module

```typescript
// src/components/ChatWidget/api/chatApi.ts

const API_BASE_URL = process.env.CHAT_API_URL || 'http://localhost:8000';

// Types
export interface CreateSessionResponse {
  session_id: string;
  created_at: string;
  last_activity: string;
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Citation[];
  created_at: string;
}

export interface Citation {
  chunk_id: string;
  chapter: string;
  section: string;
  url: string;
  confidence_score: number;
  text_snippet: string;
}

export interface StreamEvent {
  type: 'token' | 'citations' | 'metadata' | 'done' | 'error';
  content?: string;
  citations?: Citation[];
  metadata?: Record<string, any>;
  error?: string;
}

// API Functions

export const createSession = async (): Promise<CreateSessionResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/v1/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({}),
  });

  if (!response.ok) {
    throw new Error('Failed to create session');
  }

  return response.json();
};

export const fetchHistory = async (sessionId: string): Promise<Message[]> => {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/chat/history/${sessionId}`,
    {
      headers: { 'Content-Type': 'application/json' },
    }
  );

  if (!response.ok) {
    throw new Error('Failed to fetch history');
  }

  return response.json();
};

export const streamChat = async (
  sessionId: string,
  question: string,
  selectedText: string | null,
  onEvent: (event: StreamEvent) => void,
  onError: (error: Error) => void
): Promise<void> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        question,
        selected_text: selectedText,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('Response body is not readable');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();

      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');

      // Keep last incomplete line in buffer
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const event: StreamEvent = JSON.parse(line.slice(6));
            onEvent(event);
          } catch (e) {
            console.error('Failed to parse event:', e);
          }
        }
      }
    }
  } catch (error) {
    onError(error as Error);
  }
};
```

### Error Handling Strategy

```typescript
// src/components/ChatWidget/hooks/useErrorHandler.ts

interface ErrorState {
  message: string;
  type: 'network' | 'server' | 'timeout' | 'unknown';
  retryable: boolean;
}

export const useErrorHandler = () => {
  const [error, setError] = useState<ErrorState | null>(null);

  const handleError = (err: Error | unknown) => {
    if (err instanceof TypeError && err.message.includes('fetch')) {
      setError({
        message: 'Unable to connect. Retrying...',
        type: 'network',
        retryable: true,
      });
    } else if (err instanceof Error && err.message.includes('HTTP error')) {
      setError({
        message: 'Service temporarily unavailable. Please try again.',
        type: 'server',
        retryable: true,
      });
    } else {
      setError({
        message: 'Something went wrong. Please try again.',
        type: 'unknown',
        retryable: true,
      });
    }
  };

  const clearError = () => setError(null);

  const retry = async (fn: () => Promise<void>, maxAttempts = 3) => {
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        await fn();
        clearError();
        return;
      } catch (err) {
        if (attempt === maxAttempts) {
          handleError(err);
          return;
        }

        // Exponential backoff
        await new Promise((resolve) => setTimeout(resolve, 1000 * attempt));
      }
    }
  };

  return { error, handleError, clearError, retry };
};
```

---

## Styling & Theme Integration

### CSS Variables Integration

```css
/* src/components/ChatWidget/styles/variables.module.css */

:root {
  /* Inherit from robobook-docusaurus-ui theme */
  --chat-primary-cyan: var(--primary-cyan, #00f0ff);
  --chat-secondary-blue: var(--secondary-blue, #0066ff);
  --chat-card-bg: var(--card-bg, rgba(255, 255, 255, 0.1));
  --chat-text-primary: var(--text-primary, #ffffff);
  --chat-text-secondary: var(--text-secondary, #b0b0b0);
  --chat-error-red: var(--error-red, #ff4444);

  /* Chat-specific variables */
  --chat-panel-width: 400px;
  --chat-panel-height: 600px;
  --chat-panel-border-radius: 16px;
  --chat-animation-duration: 0.3s;
  --chat-animation-timing: cubic-bezier(0.4, 0, 0.2, 1);
}

/* Mobile overrides */
@media (max-width: 768px) {
  :root {
    --chat-panel-width: 100vw;
    --chat-panel-height: 80vh;
    --chat-panel-border-radius: 16px 16px 0 0;
  }
}
```

### Component Styles

**ChatToggleButton.module.css**:
```css
.toggleButton {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--chat-primary-cyan), var(--chat-secondary-blue));
  border: none;
  cursor: pointer;
  z-index: 9999;

  display: flex;
  align-items: center;
  justify-content: center;

  box-shadow: 0 4px 12px rgba(0, 240, 255, 0.3);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.toggleButton:hover {
  transform: scale(1.05);
  box-shadow: 0 0 20px rgba(0, 240, 255, 0.6);
}

.toggleButton:active {
  transform: scale(0.95);
}

.toggleButton svg {
  width: 24px;
  height: 24px;
  fill: white;
}

@media (max-width: 768px) {
  .toggleButton {
    width: 48px;
    height: 48px;
    bottom: 16px;
    right: 16px;
  }
}
```

**ChatPanel.module.css**:
```css
.chatPanel {
  position: fixed;
  bottom: 90px;
  right: 24px;
  width: var(--chat-panel-width);
  height: var(--chat-panel-height);

  background: var(--chat-card-bg);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);

  border-radius: var(--chat-panel-border-radius);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);

  display: flex;
  flex-direction: column;

  transform: translateX(0);
  transition: transform var(--chat-animation-duration) var(--chat-animation-timing);

  z-index: 9998;
}

.chatPanel.closed {
  transform: translateX(120%);
}

@media (max-width: 768px) {
  .chatPanel {
    bottom: 0;
    right: 0;
    border-radius: var(--chat-panel-border-radius);
  }
}
```

**ChatHeader.module.css**:
```css
.chatHeader {
  height: 60px;
  padding: 0 20px;

  background: linear-gradient(135deg, var(--chat-primary-cyan), var(--chat-secondary-blue));
  border-radius: var(--chat-panel-border-radius) var(--chat-panel-border-radius) 0 0;

  display: flex;
  align-items: center;
  justify-content: space-between;
}

.chatHeader h3 {
  margin: 0;
  color: white;
  font-size: 18px;
  font-weight: 600;
}

.closeButton {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  cursor: pointer;

  display: flex;
  align-items: center;
  justify-content: center;

  transition: background 0.2s ease, transform 0.2s ease;
}

.closeButton:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

.closeButton svg {
  width: 16px;
  height: 16px;
  fill: white;
}
```

**MessageBubble.module.css**:
```css
.messageBubble {
  max-width: 80%;
  padding: 12px 16px;
  margin-bottom: 12px;
  border-radius: 16px;
  word-wrap: break-word;
}

.messageBubble.user {
  align-self: flex-end;
  background: rgba(0, 240, 255, 0.2);
  color: var(--chat-text-primary);
  border-radius: 16px 16px 4px 16px;
  max-width: 70%;
}

.messageBubble.assistant {
  align-self: flex-start;
  background: var(--chat-card-bg);
  border-left: 3px solid var(--chat-primary-cyan);
  color: var(--chat-text-primary);
  border-radius: 16px 16px 16px 4px;
}

.timestamp {
  font-size: 11px;
  color: var(--chat-text-secondary);
  margin-top: 4px;
}

.citations {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}
```

**CitationBadge.module.css**:
```css
.citationBadge {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 20px;

  background: rgba(0, 240, 255, 0.15);
  border: 1px solid var(--chat-primary-cyan);

  font-size: 12px;
  color: var(--chat-primary-cyan);
  cursor: pointer;

  transition: transform 0.2s ease, background 0.2s ease;
}

.citationBadge:hover {
  transform: scale(1.05);
  background: rgba(0, 240, 255, 0.25);
  box-shadow: 0 0 12px rgba(0, 240, 255, 0.4);
}

.citationBadge:active {
  transform: scale(0.98);
}
```

**TypingIndicator.module.css**:
```css
.typingIndicator {
  align-self: flex-start;
  padding: 12px 16px;
  border-radius: 16px;
  background: var(--chat-card-bg);
  border-left: 3px solid var(--chat-primary-cyan);

  display: flex;
  gap: 6px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--chat-primary-cyan);
  animation: typing 1.4s infinite;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}

.dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    opacity: 0.3;
    transform: scale(0.8);
  }
  30% {
    opacity: 1;
    transform: scale(1);
  }
}
```

**Shimmer Effect (Loading)**:
```css
.shimmerEffect {
  position: relative;
  overflow: hidden;
}

.shimmerEffect::before {
  content: '';
  position: absolute;
  top: 0;
  left: -200%;
  width: 200%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(0, 240, 255, 0.3) 50%,
    transparent 100%
  );
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% {
    left: -200%;
  }
  100% {
    left: 200%;
  }
}
```

---

## Implementation Phases

### Phase 1: Project Setup & SSR-Safe Integration (Priority: Critical)

**Duration**: 1 day

**Tasks**:
1. Create component directory structure
2. Set up TypeScript configuration
3. Create Docusaurus Root swizzle
4. Implement BrowserOnly wrapper
5. Test build process (ensure no SSR errors)
6. Set up CSS Modules configuration

**Acceptance Criteria**:
- ✅ `npm run build` succeeds without errors
- ✅ `npm run serve` shows empty page (no widget yet)
- ✅ No console errors related to window/document access

**Deliverables**:
- `src/theme/Root.tsx`
- `src/components/ChatWidget/` (empty structure)
- TypeScript types file (`types.ts`)

---

### Phase 2: Core UI Components (Priority: High)

**Duration**: 2 days

**Tasks**:
1. Implement ChatToggleButton with styling
2. Implement ChatPanel with slide animation
3. Implement ChatHeader with close button
4. Implement MessageList with auto-scroll
5. Implement MessageBubble (user and assistant variants)
6. Implement InputBar with send button
7. Test component rendering and interactions

**Acceptance Criteria**:
- ✅ Toggle button visible and clickable
- ✅ Panel opens/closes with smooth animation
- ✅ Messages render correctly (mock data)
- ✅ Input sends message on Enter key
- ✅ All hover effects working (scale, glow)

**Deliverables**:
- All UI components with CSS Modules
- Mock data for testing
- Component Storybook stories (optional)

---

### Phase 3: State Management & Context (Priority: High)

**Duration**: 1 day

**Tasks**:
1. Create ChatWidgetContext
2. Implement useChatWidget hook
3. Implement session management (localStorage)
4. Wire up context to components
5. Test state persistence across page navigation

**Acceptance Criteria**:
- ✅ Context provides all required state and actions
- ✅ localStorage stores session_id correctly
- ✅ Widget state persists across page changes
- ✅ No memory leaks (cleanup in useEffect)

**Deliverables**:
- `ChatWidgetContext.tsx`
- `useChatWidget.ts` hook
- localStorage utilities

---

### Phase 4: Backend Integration & Streaming (Priority: Critical)

**Duration**: 2 days

**Tasks**:
1. Implement API client (`chatApi.ts`)
2. Implement session creation on first open
3. Implement history fetching
4. Implement streaming with Fetch + ReadableStream
5. Handle streaming events (token, citations, metadata, done)
6. Implement error handling and retry logic
7. Test with real backend

**Acceptance Criteria**:
- ✅ Session created on first widget open
- ✅ History loaded correctly
- ✅ Streaming displays tokens progressively
- ✅ Citations parsed and stored correctly
- ✅ Network errors handled gracefully
- ✅ Retry logic works (3 attempts with backoff)

**Deliverables**:
- `api/chatApi.ts`
- `hooks/useErrorHandler.ts`
- `hooks/useStreamingChat.ts`

---

### Phase 5: Citation Badges & Navigation (Priority: Medium)

**Duration**: 1 day

**Tasks**:
1. Implement CitationBadge component
2. Implement click handler (navigate to URL)
3. Implement scroll-to-anchor logic
4. Test citation navigation on real docs pages
5. Handle mobile behavior (close widget on citation click)

**Acceptance Criteria**:
- ✅ Citations displayed as styled badges
- ✅ Clicking citation navigates to correct page + anchor
- ✅ Browser scrolls to anchor automatically
- ✅ Widget closes on mobile after navigation

**Deliverables**:
- `CitationBadge.tsx`
- Navigation utilities

---

### Phase 6: Selected Text Detection & Mode (Priority: Medium)

**Duration**: 2 days

**Tasks**:
1. Implement SelectedTextDetector component
2. Listen to mouseup/touchend events (throttled)
3. Implement "Ask about this" tooltip
4. Position tooltip near selection
5. Implement click handler (open widget + set context)
6. Test on various page layouts
7. Ensure no performance impact

**Acceptance Criteria**:
- ✅ Text selection shows tooltip (>10 chars)
- ✅ Tooltip positioned near selection
- ✅ Clicking tooltip opens widget with context
- ✅ Selected text included in API request
- ✅ No lag when selecting text

**Deliverables**:
- `SelectedTextDetector.tsx`
- Tooltip component
- Selected text utilities

---

### Phase 7: Mobile Responsiveness (Priority: High)

**Duration**: 1 day

**Tasks**:
1. Implement mobile-specific styles (full-width panel)
2. Adjust touch target sizes (min 44px)
3. Test on real mobile devices (iOS + Android)
4. Fix any layout issues
5. Optimize animations for mobile performance

**Acceptance Criteria**:
- ✅ Widget full-width on mobile (<768px)
- ✅ All interactive elements touch-friendly
- ✅ Animations smooth on mobile (no jank)
- ✅ Keyboard pushes input into view
- ✅ Citations close widget on mobile

**Deliverables**:
- Mobile-specific CSS
- Touch interaction improvements

---

### Phase 8: Accessibility (Priority: High)

**Duration**: 1 day

**Tasks**:
1. Add ARIA labels to all interactive elements
2. Implement keyboard navigation (Tab, Enter, Esc)
3. Ensure focus indicators visible
4. Test with screen reader (NVDA/JAWS)
5. Fix color contrast issues (WCAG AA)
6. Test keyboard-only navigation

**Acceptance Criteria**:
- ✅ All buttons have ARIA labels
- ✅ Escape key closes widget
- ✅ Enter key sends message
- ✅ Tab navigates through interactive elements
- ✅ Focus indicators visible
- ✅ Color contrast ≥4.5:1 (WCAG AA)
- ✅ Screen reader announces messages

**Deliverables**:
- ARIA attributes added
- Keyboard handlers implemented
- Accessibility audit report

---

### Phase 9: Performance Optimization (Priority: Medium)

**Duration**: 1 day

**Tasks**:
1. Implement code splitting (React.lazy)
2. Optimize bundle size (analyze with webpack-bundle-analyzer)
3. Implement memoization (React.memo, useMemo, useCallback)
4. Optimize re-renders (avoid unnecessary updates)
5. Test performance with Lighthouse
6. Measure First Interaction Time

**Acceptance Criteria**:
- ✅ Bundle size <100KB gzipped
- ✅ First interaction <1s
- ✅ Lighthouse Performance score >90
- ✅ No unnecessary re-renders
- ✅ Animations 60fps (DevTools profiling)

**Deliverables**:
- Code splitting implementation
- Performance audit report
- Bundle size report

---

### Phase 10: Error States & Edge Cases (Priority: Medium)

**Duration**: 1 day

**Tasks**:
1. Implement error message display
2. Handle empty state (no messages yet)
3. Handle network offline state
4. Handle session expiration
5. Implement "Clear History" button
6. Test all error scenarios

**Acceptance Criteria**:
- ✅ Network errors show friendly message
- ✅ Empty state shows welcome message
- ✅ Offline state detected and communicated
- ✅ Expired sessions recreated automatically
- ✅ Clear History works correctly

**Deliverables**:
- Error components
- Empty state component
- Edge case handling

---

### Phase 11: Testing & QA (Priority: Critical)

**Duration**: 2 days

**Tasks**:
1. Write unit tests (Jest + React Testing Library)
2. Write integration tests (user flows)
3. Test on all browsers (Chrome, Firefox, Safari, Edge)
4. Test on all devices (desktop, tablet, mobile)
5. Test all user scenarios from spec
6. Fix bugs found during QA

**Acceptance Criteria**:
- ✅ All unit tests pass
- ✅ All integration tests pass
- ✅ All user scenarios work
- ✅ No console errors or warnings
- ✅ Cross-browser compatibility verified
- ✅ Cross-device compatibility verified

**Deliverables**:
- Test suite (Jest + RTL)
- Test coverage report (>80%)
- QA sign-off document

---

### Phase 12: Documentation & Deployment (Priority: High)

**Duration**: 1 day

**Tasks**:
1. Write integration guide for Docusaurus
2. Document configuration options
3. Create troubleshooting guide
4. Update README with setup instructions
5. Deploy to staging environment
6. Smoke test on staging
7. Deploy to production

**Acceptance Criteria**:
- ✅ Integration guide complete
- ✅ Configuration documented
- ✅ README updated
- ✅ Staging deployment successful
- ✅ Production deployment successful

**Deliverables**:
- `docs/INTEGRATION_GUIDE.md`
- `docs/CONFIGURATION.md`
- `docs/TROUBLESHOOTING.md`
- Updated README.md

---

## Risk Assessment & Mitigation

### Risk 1: SSR/SSG Build Failures (Critical)

**Probability**: Medium
**Impact**: Critical (blocks deployment)

**Symptoms**:
- `ReferenceError: window is not defined`
- `ReferenceError: document is not defined`
- `ReferenceError: localStorage is not defined`

**Mitigation**:
1. **Prevention**:
   - Wrap all widget code in BrowserOnly
   - Use `typeof window !== 'undefined'` checks
   - Place all browser API calls inside useEffect
   - Never import browser-dependent code at top level

2. **Detection**:
   - Run `npm run build` frequently during development
   - Set up CI/CD to catch build errors early

3. **Fallback**:
   - If BrowserOnly fails, use dynamic import with `require()` in callback
   - Add null checks for all browser APIs

**Example Safe Pattern**:
```tsx
// ✅ GOOD
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

// ❌ BAD
import ChatWidget from '@site/src/components/ChatWidget';

export default function Root({ children }) {
  return (
    <>
      {children}
      <ChatWidget />
    </>
  );
}
```

### Risk 2: Bundle Size Exceeds Target (<100KB) (High)

**Probability**: Medium
**Impact**: High (performance degradation)

**Mitigation**:
1. **Monitor**:
   - Use webpack-bundle-analyzer during development
   - Set up bundle size budgets in CI/CD

2. **Optimize**:
   - Code splitting with React.lazy()
   - Tree shaking (avoid barrel imports)
   - No heavy dependencies (avoid moment.js, lodash, etc.)
   - Minification and compression (webpack production mode)

3. **Target Breakdown**:
   - React Context + components: ~30KB
   - CSS Modules: ~15KB
   - API client: ~10KB
   - Utilities: ~5KB
   - Total: ~60KB (40KB buffer)

**If Exceeds Target**:
- Remove unused code (dead code elimination)
- Lazy load non-critical components
- Use lighter alternatives (date-fns instead of moment)
- Consider CDN for shared libraries

### Risk 3: Cross-Page State Loss (Medium)

**Probability**: Medium
**Impact**: Medium (poor UX, confusion)

**Symptoms**:
- Widget resets when navigating between pages
- Messages disappear on page change
- isOpen state not preserved

**Mitigation**:
1. **Root-level Context**:
   - Place ChatWidgetProvider at Root level (above Docusaurus router)
   - Ensures context survives page navigation

2. **localStorage Backup**:
   - Persist isOpen state in localStorage
   - Restore on mount

3. **Testing**:
   - Test navigation scenarios thoroughly
   - Use Docusaurus Link component (client-side routing)

**Implementation**:
```tsx
// In ChatWidgetProvider
useEffect(() => {
  // Save isOpen state
  localStorage.setItem('robobook_chat_open', isOpen ? '1' : '0');
}, [isOpen]);

useEffect(() => {
  // Restore isOpen state on mount
  const wasOpen = localStorage.getItem('robobook_chat_open') === '1';
  if (wasOpen) {
    setIsOpen(true);
  }
}, []);
```

### Risk 4: Selected Text Detection Performance (Medium)

**Probability**: Low
**Impact**: Medium (laggy selection, poor UX)

**Mitigation**:
1. **Throttling**:
   - Use throttle (200ms) on mouseup/touchend
   - Avoid selectionchange event (fires too frequently)

2. **Efficient Check**:
   - Quick length check before processing
   - Bail early if selection too short (<10 chars)

3. **Cleanup**:
   - Remove listeners on widget close
   - Clear timeouts on unmount

4. **Testing**:
   - Profile with DevTools (Performance tab)
   - Test on low-end devices

### Risk 5: Streaming Failure Mid-Response (Medium)

**Probability**: Low
**Impact**: Medium (incomplete answer, confusion)

**Mitigation**:
1. **Timeout Detection**:
   - Set timeout (30s) for streaming
   - Show message: "Response is taking longer than usual..."

2. **Retry Logic**:
   - Auto-retry on connection loss (3 attempts)
   - Exponential backoff (1s, 2s, 4s)

3. **Partial Response Handling**:
   - Display partial response if stream disconnects
   - Show "Connection lost. Retry?" button

4. **EventSource Reconnection**:
   - EventSource auto-reconnects by default
   - For Fetch stream, implement manual reconnection

**Implementation**:
```typescript
const streamWithTimeout = (fn: () => Promise<void>, timeoutMs = 30000) => {
  return Promise.race([
    fn(),
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Timeout')), timeoutMs)
    ),
  ]);
};
```

### Risk 6: Mobile Keyboard Obscures Input (Low)

**Probability**: Low
**Impact**: Low (annoying UX on mobile)

**Mitigation**:
1. **Scroll Into View**:
   - Use `scrollIntoView({ behavior: 'smooth', block: 'center' })` on input focus

2. **Viewport Height Adjustment**:
   - Use `vh` units carefully (100vh doesn't account for mobile keyboard)
   - Use `calc(100vh - 300px)` to leave space

3. **Testing**:
   - Test on real mobile devices (iOS Safari, Chrome Android)
   - Test with hardware keyboard and on-screen keyboard

**Implementation**:
```typescript
const inputRef = useRef<HTMLInputElement>(null);

useEffect(() => {
  const input = inputRef.current;
  if (!input) return;

  const handleFocus = () => {
    setTimeout(() => {
      input.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 300); // Wait for keyboard animation
  };

  input.addEventListener('focus', handleFocus);
  return () => input.removeEventListener('focus', handleFocus);
}, []);
```

### Risk 7: Theme Variable Conflicts (Low)

**Probability**: Low
**Impact**: Low (visual inconsistencies)

**Mitigation**:
1. **Scoped Variables**:
   - Prefix all chat-specific variables with `--chat-`
   - Fallback to defaults if theme variables missing

2. **Testing**:
   - Test in light mode and dark mode
   - Test with different Docusaurus themes

3. **Fallback**:
   - Define fallback values for all CSS variables
   - Example: `var(--primary-cyan, #00f0ff)`

---

## Monitoring & Observability

### Performance Metrics

**Client-Side**:
- First Interaction Time (widget open latency)
- Streaming Latency (time to first token)
- Message Send Latency (click to API call)
- Animation Frame Rate (should be 60fps)

**Tools**:
- Lighthouse CI (automated audits)
- Web Vitals (LCP, FID, CLS)
- Chrome DevTools Performance profiler
- webpack-bundle-analyzer (bundle size)

### Error Tracking

**Client-Side Errors**:
- API errors (network, 4xx, 5xx)
- Streaming errors (connection loss, parsing)
- localStorage errors (quota exceeded, disabled)
- Component errors (boundary catches)

**Logging**:
- Console errors (development)
- Sentry or similar (production)
- Custom telemetry (optional)

### Usage Analytics (Optional)

**Events to Track**:
- Widget opened
- Message sent
- Citation clicked
- Selected text query
- Error occurred

**Privacy**:
- No message content logged
- Only aggregate metrics (counts, timings)
- Respect Do Not Track header

---

## Acceptance Criteria (Final)

### Functional Requirements (FR-1 to FR-14)

- ✅ FR-1: Widget visible on all pages
- ✅ FR-2: Open/close animations smooth (<300ms)
- ✅ FR-3: Tech Cyber theme styling applied
- ✅ FR-4: Chat functionality (send, stream, history)
- ✅ FR-5: Selected text mode functional
- ✅ FR-6: Citations clickable and navigable
- ✅ FR-7: Session management (localStorage)
- ✅ FR-8: Conversation history loaded
- ✅ FR-9: Error handling (network, retry)
- ✅ FR-10: Performance optimized (bundle size, lazy load)
- ✅ FR-11: Accessibility (WCAG AA)
- ✅ FR-12: Mobile responsive
- ✅ FR-13: SSR/SSG compatible (no build errors)
- ✅ FR-14: Configuration options available

### User Scenarios (1-5)

- ✅ Scenario 1: General Q&A works end-to-end
- ✅ Scenario 2: Selected text mode works
- ✅ Scenario 3: Mobile experience smooth
- ✅ Scenario 4: Session continuity across visits
- ✅ Scenario 5: Error handling graceful

### Technical Acceptance

- ✅ `npm run build` succeeds without errors
- ✅ `npm run serve` shows working widget
- ✅ Bundle size <100KB gzipped
- ✅ Lighthouse Performance score >90
- ✅ Test coverage >80%
- ✅ No console errors or warnings
- ✅ Cross-browser compatibility verified
- ✅ WCAG AA compliance verified

---

## Next Steps

### After Plan Approval

1. **Run `/sp.tasks`**: Generate granular task breakdown with estimates
2. **Set up project board**: Create tickets for each task
3. **Begin Phase 1**: Start with SSR-safe integration
4. **Daily standups**: Track progress, blockers
5. **Weekly demos**: Show progress to stakeholders

### Implementation Order

**Week 1**:
- Phase 1: Project setup (Day 1)
- Phase 2: Core UI components (Day 2-3)
- Phase 3: State management (Day 4)
- Phase 4: Backend integration (Day 5)

**Week 2**:
- Phase 5: Citation badges (Day 1)
- Phase 6: Selected text detection (Day 2-3)
- Phase 7: Mobile responsiveness (Day 4)
- Phase 8: Accessibility (Day 5)

**Week 3**:
- Phase 9: Performance optimization (Day 1)
- Phase 10: Error states (Day 2)
- Phase 11: Testing & QA (Day 3-4)
- Phase 12: Documentation & deployment (Day 5)

**Total Estimated Duration**: 15 working days (3 weeks)

---

## Appendices

### A. File Structure

```
src/
├── components/
│   └── ChatWidget/
│       ├── index.tsx                      # Main export
│       ├── ChatWidget.tsx                 # Container component
│       ├── ChatWidgetContext.tsx          # Context provider
│       ├── components/
│       │   ├── ChatToggleButton.tsx
│       │   ├── ChatPanel.tsx
│       │   ├── ChatHeader.tsx
│       │   ├── MessageList.tsx
│       │   ├── MessageBubble.tsx
│       │   ├── CitationBadge.tsx
│       │   ├── InputBar.tsx
│       │   ├── TypingIndicator.tsx
│       │   ├── ErrorMessage.tsx
│       │   └── SelectedTextDetector.tsx
│       ├── hooks/
│       │   ├── useChatWidget.ts
│       │   ├── useErrorHandler.ts
│       │   ├── useStreamingChat.ts
│       │   └── useSelectedText.ts
│       ├── api/
│       │   └── chatApi.ts
│       ├── utils/
│       │   ├── localStorage.ts
│       │   ├── streaming.ts
│       │   └── navigation.ts
│       ├── styles/
│       │   ├── variables.module.css
│       │   ├── ChatToggleButton.module.css
│       │   ├── ChatPanel.module.css
│       │   ├── ChatHeader.module.css
│       │   ├── MessageList.module.css
│       │   ├── MessageBubble.module.css
│       │   ├── CitationBadge.module.css
│       │   ├── InputBar.module.css
│       │   └── SelectedTextDetector.module.css
│       └── types.ts
│
└── theme/
    └── Root.tsx                           # Docusaurus swizzle

docs/
├── INTEGRATION_GUIDE.md
├── CONFIGURATION.md
└── TROUBLESHOOTING.md

tests/
└── ChatWidget/
    ├── ChatWidget.test.tsx
    ├── ChatToggleButton.test.tsx
    ├── ChatPanel.test.tsx
    ├── MessageList.test.tsx
    ├── MessageBubble.test.tsx
    ├── CitationBadge.test.tsx
    ├── InputBar.test.tsx
    ├── SelectedTextDetector.test.tsx
    ├── useChatWidget.test.ts
    ├── useStreamingChat.test.ts
    └── chatApi.test.ts
```

### B. Configuration Options

```typescript
// src/components/ChatWidget/config.ts

export interface ChatWidgetConfig {
  // API Configuration
  apiBaseUrl: string;

  // UI Configuration
  position: 'bottom-right' | 'bottom-left';
  enableSelectedTextMode: boolean;
  maxCitations: number;

  // Session Configuration
  sessionDurationHours: number;

  // Performance Configuration
  streamingTimeout: number;
  retryAttempts: number;
  retryDelay: number;
}

export const defaultConfig: ChatWidgetConfig = {
  apiBaseUrl: process.env.CHAT_API_URL || 'http://localhost:8000',
  position: 'bottom-right',
  enableSelectedTextMode: true,
  maxCitations: 5,
  sessionDurationHours: 24,
  streamingTimeout: 30000,
  retryAttempts: 3,
  retryDelay: 1000,
};
```

### C. TypeScript Types

```typescript
// src/components/ChatWidget/types.ts

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Citation[];
  timestamp: string;
  isStreaming?: boolean;
}

export interface Citation {
  chunk_id: string;
  chapter: string;
  section: string;
  url: string;
  confidence_score: number;
  text_snippet: string;
}

export interface Session {
  sessionId: string;
  createdAt: string;
  lastActivity: string;
}

export interface StreamEvent {
  type: 'token' | 'citations' | 'metadata' | 'done' | 'error';
  content?: string;
  citations?: Citation[];
  metadata?: Record<string, any>;
  error?: string;
}

export interface WidgetState {
  isOpen: boolean;
  sessionId: string | null;
  messages: Message[];
  isStreaming: boolean;
  error: string | null;
  selectedText: string | null;
}
```

---

**Plan Version**: 1.0
**Last Updated**: 2025-12-17
**Status**: Ready for Task Generation (`/sp.tasks`)
