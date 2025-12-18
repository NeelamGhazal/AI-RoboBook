# Quick Test Commands - ChatWidget Visibility

## Frontend Test

```bash
# Start development server
cd frontend
npm start

# Expected: http://localhost:3000
# Check browser console for:
# - "[ChatWidget] Rendering in browser - widget should be visible"
# - "[ChatToggleButton] Rendering button - isOpen: false"

# Look for cyan circular button in bottom-right corner (24px from edges)
```

## Backend Test

```bash
# Start backend server
cd backend/rag-chatbot
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Expected: http://localhost:8000/docs shows all endpoints
# - POST /api/v1/chat
# - POST /api/v1/chat/stream
# - POST /api/v1/sessions
# - GET /api/v1/sessions/{session_id}
# - GET /health
```

## Production Build Test

```bash
cd frontend
npm run build
# Expected: [SUCCESS] Generated static files in "build"

npm run serve
# Expected: http://localhost:3000 with widget visible
```

## Troubleshooting

**If widget not visible**:
1. Check console logs (widget rendering?)
2. Use Element Inspector (Ctrl+Shift+C)
3. Search for "toggleButton" in HTML
4. Verify CSS loaded in Network tab

**If backend /docs blank**:
1. Check router includes before metrics mounting
2. Verify routers have tags and prefixes
3. Restart server

---

**Status**: Both fixes applied, ready for testing
**Date**: 2025-12-18
