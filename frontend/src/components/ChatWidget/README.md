# RAG Chatbot Frontend Widget

An interactive floating chat widget for the RoboBook Docusaurus site that provides AI-powered Q&A with streaming responses, source citations, and selected-text querying.

## Features

- **Floating Toggle Button**: Always accessible cyan-glowing button in bottom-right corner
- **Streaming Responses**: Real-time token-by-token streaming from the backend
- **Source Citations**: Clickable citation badges that navigate to relevant textbook sections
- **Selected Text Mode**: Highlight text on the page to ask contextual questions
- **Session Persistence**: Conversation history maintained across page navigation
- **Mobile Responsive**: Full-width panel on mobile with touch-friendly controls
- **Tech Cyber Theme**: Glassmorphism, cyan gradients, mandatory shimmer/glow effects
- **SSR/SSG Safe**: Zero build errors with Docusaurus static generation

## Architecture

```
ChatWidget (Container)
  ├── ChatWidgetContext (State Provider)
  ├── ChatToggleButton (Always Visible)
  ├── ChatPanel (Conditional)
  │     ├── ChatHeader
  │     ├── MessageList
  │     │     ├── MessageBubble[]
  │     │     │     └── CitationBadge[]
  │     │     └── TypingIndicator
  │     └── InputBar
  └── SelectedTextDetector (Global Listener)
```

## Configuration

Edit `/src/components/ChatWidget/config.ts` to configure:

```typescript
export const defaultConfig: ChatWidgetConfig = {
  apiUrl: 'http://localhost:8000', // Backend API URL
  sessionTtlHours: 24,             // Session expiration
  maxMessages: 50,                 // Max history messages
  enableSelectedText: true,        // Enable text selection mode
  position: 'bottom-right',        // Widget position
  theme: 'cyber',                  // Theme variant
};
```

### Environment Variables

Set the backend API URL via environment variable:

```bash
# .env
CHAT_API_URL=https://your-backend-api.com
```

Or configure at runtime:

```html
<script>
  window.CHAT_API_URL = 'https://your-backend-api.com';
</script>
```

## Integration

The widget is globally integrated via Docusaurus Root swizzling (`src/theme/Root.tsx`):

```tsx
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

This ensures:
- Widget appears on all pages
- SSR/SSG safety (no build errors)
- Lazy loading (client-side only)
- State persists across page navigation

## Testing

### Manual Testing

1. **Start the backend**:
   ```bash
   cd backend/rag-chatbot
   uvicorn app.main:app --reload
   ```

2. **Start the frontend**:
   ```bash
   cd frontend
   npm start
   ```

3. **Test scenarios**:
   - Click the cyan toggle button → Panel should slide in
   - Type a question → Response should stream in real-time
   - Click citations → Should navigate to textbook section
   - Select text on page → Widget opens with selected text context
   - Navigate to different page → Widget state persists
   - Mobile view → Panel should be full-width

### Build Verification

Verify SSR/SSG safety:

```bash
npm run build
```

Build should complete without errors. Check for:
- No `window is not defined` errors
- No `document is not defined` errors
- Widget appears correctly after build

### Production Build

Build for production:

```bash
npm run build
npm run serve
```

Visit http://localhost:3000 and verify widget functionality.

## API Contract

The widget expects these backend endpoints:

### `POST /api/v1/sessions`

Create a new chat session.

**Response**:
```json
{
  "session_id": "uuid",
  "created_at": "2025-12-17T..."
}
```

### `POST /api/v1/chat/stream`

Send a message and receive streaming response.

**Request**:
```json
{
  "session_id": "uuid",
  "question": "What is SLAM?",
  "selected_text": "optional selected text context"
}
```

**Response** (Server-Sent Events):
```
data: {"type": "token", "content": "SLAM"}
data: {"type": "token", "content": " stands"}
data: {"type": "token", "content": " for..."}
data: {"type": "citations", "citations": [{...}]}
data: {"type": "metadata", "metadata": {...}}
data: {"type": "done"}
```

### `GET /api/v1/chat/history/{session_id}`

Fetch conversation history.

**Response**:
```json
{
  "session_id": "uuid",
  "messages": [
    {
      "role": "user",
      "content": "What is SLAM?",
      "timestamp": "2025-12-17T...",
      "sources": []
    },
    {
      "role": "assistant",
      "content": "SLAM stands for...",
      "timestamp": "2025-12-17T...",
      "sources": [{...}]
    }
  ]
}
```

## Customization

### Styling

All styles use CSS Modules with Tech Cyber theme variables defined in `styles/variables.module.css`.

Key variables:
```css
--chat-primary-cyan: #00ffff
--chat-secondary-blue: #0077ff
--chat-card-bg: rgba(15, 23, 42, 0.95)
--chat-glass-blur: blur(10px)
```

### Hover Effects

All interactive elements have **mandatory shimmer/glow** hover effects per the Tech Cyber theme:

```css
.button:hover {
  transform: scale(1.05);
  box-shadow: 0 0 30px rgba(0, 255, 255, 0.8);
  animation: shimmer 2s linear infinite;
}
```

## Troubleshooting

### Widget doesn't appear

- Check browser console for errors
- Verify `src/theme/Root.tsx` exists and imports ChatWidget
- Ensure build completed successfully

### SSR/Build errors

- Verify all browser APIs (`window`, `document`, `localStorage`) are inside `useEffect` or `typeof window !== 'undefined'` checks
- Ensure `BrowserOnly` wrapper is used in Root.tsx

### Streaming not working

- Verify backend API URL is correct
- Check Network tab for `/api/v1/chat/stream` request
- Ensure backend is returning Server-Sent Events format

### Citations not clickable

- Verify citation URLs are valid
- Check that `citation.url` is not empty
- Ensure Docusaurus routing matches citation URLs

## File Structure

```
src/components/ChatWidget/
├── index.tsx                    # Main entry point
├── types.ts                     # TypeScript interfaces
├── config.ts                    # Configuration
├── README.md                    # This file
├── context/
│   └── ChatWidgetContext.tsx    # React Context provider
├── components/
│   ├── ChatToggleButton.tsx/.module.css
│   ├── ChatPanel.tsx/.module.css
│   ├── ChatHeader.tsx/.module.css
│   ├── MessageList.tsx/.module.css
│   ├── MessageBubble.tsx/.module.css
│   ├── CitationBadge.tsx/.module.css
│   ├── InputBar.tsx/.module.css
│   ├── TypingIndicator.tsx/.module.css
│   └── SelectedTextDetector.tsx
├── hooks/
│   └── useChatStream.ts         # Streaming hook
├── api/
│   └── chatApi.ts               # API client
├── utils/
│   └── localStorage.ts          # Persistence utilities
└── styles/
    └── variables.module.css     # CSS variables
```

## License

Part of the Physical AI & Humanoid Robotics Textbook project.
