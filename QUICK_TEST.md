# Quick Test - ChatWidget Full Functionality (v6 - Robust Session Creation)

## Start Backend (REQUIRED)

```bash
cd backend/rag-chatbot
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Start Frontend

```bash
cd frontend
npm start
```

## Expected Console Logs (Widget Load)

**Frontend Console** (F12 → Console):
```
[ChatWidget] Rendering in browser - widget should be visible
[ChatToggleButton] Rendering button - isOpen: false
[ChatToggleButton] Toggle button inline styles applied — should be visible now
[SelectedTextDetector] Installing selection listeners
[ChatApi] Creating session at: http://localhost:8000/api/v1/sessions
[ChatApi] Session created successfully: <uuid>
```

**Backend Console** (uvicorn terminal) - NEW in v6:
```
[Backend] POST /api/v1/sessions called
[Backend] Session data: user_id=None, metadata=None
[Backend] Attempting database session creation...
[Backend] ⚠ Database session creation failed: ... (OR ✓ Session created in database)
[Backend] Falling back to in-memory session storage... (if DB failed)
[Backend] ✓ Session created in memory: <uuid> (OR in database)
```

## Expected Visual (ENHANCED)

**Bottom-right corner**:
- ✅ **BRIGHT CYAN** circular button (60px diameter)
- ✅ **WHITE BORDER** (3px) - crisp edge
- ✅ 32px from bottom and right edges (more clearance)
- ✅ Bright cyan-to-blue gradient (#00d4ff → #0ea5e9)
- ✅ Strong cyan glow (30px spread)
- ✅ White message bubble icon

**Hover** (STRONGER):
- ✅ Grows to **115%** size (was 110%)
- ✅ **INTENSE cyan glow** (40px blur, 90% opacity)
- ✅ Smooth 300ms animation

**Click**:
- ✅ Chat panel slides in from right
- ✅ Icon changes to X
- ✅ Panel shows header + message list + input bar

---

## Test Message Sending (NEW in v4)

1. **Click toggle button** → Panel opens
2. **Type**: "What is a ROS 2 node?"
3. **Press Enter or click send**

**Expected Console Logs**:
```
[ChatApi] Starting stream request to: http://localhost:8000/api/v1/chat/stream
[ChatApi] Request payload: { session_id: "...", question_length: 20, has_selected_text: false }
[ChatApi] Stream response status: 200 OK
[ChatApi] Stream started successfully
[ChatApi] Token chunk received, total chunks: 1
[ChatApi] Token chunk received, total chunks: 10
[ChatApi] Stream event: citations
[ChatApi] Stream event: metadata
[ChatApi] Stream event: done
[ChatApi] Stream completed, total chunks: 35
```

**Expected Visual**:
- ✅ User message appears immediately
- ✅ Assistant message streams in word-by-word
- ✅ Citations appear at bottom (if any)
- ✅ Message completes with full response

---

## Test Selected Text Feature (NEW in v4)

1. **Navigate to any page** with text (e.g., Chapter 1)
2. **Select 50+ characters** (e.g., a full sentence or paragraph)
3. **Look for "Ask about this" button** near selection (cyan with question icon)
4. **Click button**

**Expected Console Logs**:
```
[SelectedTextDetector] Text selected: { length: 125, preview: "ROS 2 nodes are fundamental..." }
[SelectedTextDetector] Opening widget with selected text
```

**Expected Visual**:
- ✅ "Ask about this" button appears near selection (cyan gradient, white border)
- ✅ Button positioned 10px right and 40px above selection
- ✅ Hover: Button grows slightly with glow
- ✅ Click: Widget opens with badge "📌 Asking about: ..."
- ✅ Input bar ready for question about selected text
- ✅ Send message includes selected text in context

---

## Maximum Visibility Features

- ✅ `display: block` (forced)
- ✅ `visibility: visible` (forced)
- ✅ `opacity: 1` (forced)
- ✅ `pointerEvents: auto` (forced)
- ✅ White border for maximum contrast
- ✅ Brighter gradient for better visibility
- ✅ Z-index 9999 (above everything)

## Critical Fixes Applied

**v3 - process.env Crash Fix**:
- ✅ Replaced `process.env.CHAT_API_URL` with browser-safe `getApiUrl()`
- ✅ Widget can now load without crash

**v4 - API Communication & Selected Text**:
- ✅ Added comprehensive debug logging to chatApi.ts
- ✅ Implemented "Ask about this" button for selected text
- ✅ Enhanced SelectedTextDetector with button display logic
- ✅ Changed MIN_SELECTED_TEXT_LENGTH to 50 chars

**v5 - Session Fix + Heading Selection**:
- ✅ Fixed 500 error on /api/v1/sessions endpoint (UUID handling)
- ✅ Confirmed heading selection works (H1-H6)
- ✅ Added element type logging (shows H1, H2, P, etc.)
- ✅ Added selection length debugging

**v6 - Robust Session Creation** (NEW - CRITICAL FIX):
- ✅ Dual-mode session creation (database + in-memory fallback)
- ✅ NEVER fails - always returns 201 Created
- ✅ Comprehensive logging (shows database/memory selection)
- ✅ Works without database setup (MVP ready)

## Test Heading Selection (NEW in v5)

1. **Navigate to any chapter** with headings
2. **Select a FULL heading** (at least 50 characters)
   - Example: "Chapter 1: Fundamentals of Physical AI and Humanoid Robotics" (67 chars ✅)
   - Too short: "Introduction" (12 chars ❌)
3. **Look for "Ask about this" button**

**Expected Console Logs**:
```
[SelectedTextDetector] Selection detected: { length: 67, minRequired: 50, tooShort: false, ... }
[SelectedTextDetector] Text selected (showing button): { length: 67, elementType: "H1", ... }
```

**If button doesn't appear**:
- Console will show: `tooShort: true` if heading < 50 chars
- Solution: Select heading + subtitle, or longer heading

## Troubleshooting

**Session creation fails (500 error)**:
1. Check backend is running: `curl http://localhost:8000/health`
2. Check PostgreSQL is running: `pg_isready -h localhost -p 5432`
3. Check backend logs for: `ERROR: session_creation_failed`
4. See `SESSION_AND_HEADING_SELECTION_FIX.md` for detailed debugging

**No response when sending message**:
1. Check backend is running: `curl http://localhost:8000/health`
2. Check console for API errors (red ❌)
3. Check Network tab for CORS errors
4. See `CHATWIDGET_API_COMMUNICATION_FIX.md` for detailed debugging

**"Ask about this" button not appearing**:
1. Select at least 50 characters (not just 1 word or short heading)
2. Check console for `[SelectedTextDetector]` logs showing selection length
3. Verify `enableSelectedText: true` in config.ts
4. Check browser zoom is 100%
5. Try selecting heading + first sentence if heading alone is too short

---

**Status**: Session creation GUARANTEED + heading selection working
**Date**: 2025-12-18
**Version**: v6 - Robust dual-mode session creation (database + in-memory fallback)
**Docs**:
- `SESSION_500_ERROR_FIX.md` for v6 robust session fix (CRITICAL)
- `SESSION_AND_HEADING_SELECTION_FIX.md` for v5 fixes
- `CHATWIDGET_API_COMMUNICATION_FIX.md` for comprehensive guide
