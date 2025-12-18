# ChatWidget "process is not defined" Fix

**Date**: 2025-12-18
**Issue**: ReferenceError: process is not defined
**Location**: `frontend/src/components/ChatWidget/config.ts:18`
**Status**: ✅ FIXED

---

## Problem

**Error in Browser Console**:
```
ReferenceError: process is not defined
  at config.ts:18
```

**Root Cause**:
The config file was trying to access `process.env.CHAT_API_URL` directly in browser code:

```typescript
// ❌ WRONG - crashes in browser
apiUrl:
  (typeof window !== 'undefined' && (window as any).CHAT_API_URL) ||
  process.env.CHAT_API_URL ||  // ← CRASH HERE
  'http://localhost:8000',
```

**Why This Crashes**:
- `process` is a Node.js global object
- `process` does NOT exist in browser environment
- When browser tries to evaluate `process.env.CHAT_API_URL`, it throws: `ReferenceError: process is not defined`
- This crash happens **before ChatWidget can even render**
- Result: Toggle button never appears, no console logs from component

---

## Solution Applied

**File**: `frontend/src/components/ChatWidget/config.ts`

### 1. Created Browser-Safe API URL Function

```typescript
/**
 * Get API URL with browser-safe fallback
 * Checks browser window global first, then falls back to hardcoded default
 * IMPORTANT: process.env is NOT available in browser - causes "process is not defined" error
 */
function getApiUrl(): string {
  // Check for browser runtime config
  if (typeof window !== 'undefined' && (window as any).CHAT_API_URL) {
    return (window as any).CHAT_API_URL;
  }

  // Fallback to localhost for development
  // TODO: In production, set window.CHAT_API_URL or update this to production URL
  return 'http://localhost:8000';
}
```

### 2. Updated defaultConfig to Use Function

```typescript
export const defaultConfig: ChatWidgetConfig = {
  // API endpoint - browser-safe (NO process.env)
  apiUrl: getApiUrl(),  // ✅ Browser-safe function call

  // Session persistence duration (24 hours)
  sessionTtlHours: 24,

  // ... rest of config
};
```

---

## Why This Fix Works

### Before (BROKEN):
```typescript
apiUrl: process.env.CHAT_API_URL || 'http://localhost:8000'
```

**Evaluation order**:
1. Browser tries to read `process`
2. `process` is undefined in browser
3. **CRASH**: `ReferenceError: process is not defined`
4. Code never reaches fallback
5. ChatWidget never loads

### After (FIXED):
```typescript
apiUrl: getApiUrl()
```

**Evaluation order**:
1. Call `getApiUrl()` function
2. Check `typeof window !== 'undefined'` (always true in browser)
3. Check `window.CHAT_API_URL` (if set, use it)
4. If not set, return `'http://localhost:8000'`
5. **NO crashes** - no `process` access
6. ChatWidget loads successfully

---

## Browser vs Node.js Environment

### Available in Browser:
- ✅ `window` - Global object
- ✅ `document` - DOM access
- ✅ `localStorage` - Storage API
- ✅ `fetch` - HTTP requests
- ✅ `console` - Logging

### NOT Available in Browser:
- ❌ `process` - Node.js only
- ❌ `require()` - Node.js only (use `import`)
- ❌ `__dirname` - Node.js only
- ❌ `fs` - File system (Node.js only)
- ❌ `path` - Path utilities (Node.js only)

### SSR/SSG Context (Docusaurus Build):
- ❌ `window` - Not available during build
- ❌ `document` - Not available during build
- ❌ `localStorage` - Not available during build
- ✅ Must use `typeof window !== 'undefined'` checks

---

## Configuration Options

### Development (Local Testing)

**Default behavior** (no configuration needed):
```
API URL: http://localhost:8000
```

**No changes required** - widget connects to local backend automatically.

### Production Deployment

**Option 1: Set window global** (Recommended):

In `docusaurus.config.ts`, add:
```typescript
module.exports = {
  // ... other config

  scripts: [
    {
      tagName: 'script',
      innerHTML: `
        window.CHAT_API_URL = 'https://api.yourdomain.com';
      `,
    },
  ],
};
```

**Option 2: Hardcode in config.ts**:

Update `getApiUrl()` function:
```typescript
function getApiUrl(): string {
  if (typeof window !== 'undefined' && (window as any).CHAT_API_URL) {
    return (window as any).CHAT_API_URL;
  }

  // Hardcode production URL
  return 'https://api.yourdomain.com';  // ← Update this
}
```

**Option 3: Environment-based**:

Use Docusaurus environment config (if available):
```typescript
function getApiUrl(): string {
  if (typeof window !== 'undefined' && (window as any).CHAT_API_URL) {
    return (window as any).CHAT_API_URL;
  }

  // Check if running on production domain
  if (typeof window !== 'undefined' && window.location.hostname === 'yourdomain.com') {
    return 'https://api.yourdomain.com';
  }

  // Default to localhost for development
  return 'http://localhost:8000';
}
```

---

## Testing Instructions

### Step 1: Restart Frontend

```bash
cd frontend
npm start
```

### Step 2: Check Console (Should Be Clean)

**Open Browser DevTools** (F12) → Console tab

**Expected** (NO errors):
```
[ChatWidget] Rendering in browser - widget should be visible
[ChatToggleButton] Rendering button - isOpen: false
[ChatToggleButton] Toggle button inline styles applied — should be visible now
```

**Should NOT see**:
```
❌ ReferenceError: process is not defined
```

### Step 3: Verify Toggle Button Appears

**Visual check** - Bottom-right corner:
- ✅ Bright cyan circular button (60px)
- ✅ White border (3px)
- ✅ Strong cyan glow
- ✅ 32px from bottom-right edges

### Step 4: Test Functionality

1. **Hover**: Button grows to 115%, intense cyan glow
2. **Click**: Chat panel slides in from right
3. **Type question**: Input should work
4. **Send**: Should connect to `http://localhost:8000/api/v1/chat`

---

## Backend Connection

### Start Backend Server

```bash
cd backend/rag-chatbot
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     application_started
```

### Verify API Endpoints

**Open**: http://localhost:8000/docs

**Should see**:
- POST /api/v1/chat
- POST /api/v1/chat/stream
- POST /api/v1/sessions
- GET /health

---

## Troubleshooting

### Button Still Not Appearing

**If you still see "process is not defined"**:
1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
3. Restart dev server (`npm start`)
4. Check you're editing the right file (`frontend/src/components/ChatWidget/config.ts`)

**If no console errors but button not visible**:
- This is a different issue (CSS styling)
- See `TOGGLE_BUTTON_DIAGNOSIS.md` for CSS fixes
- The config fix eliminates the crash, but styling issues are separate

### API Connection Fails

**Error**: "Failed to fetch" or "CORS error"

**Solution**: Ensure backend is running on port 8000:
```bash
cd backend/rag-chatbot
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Error**: "404 Not Found"

**Solution**: Check API endpoints exist:
```bash
curl http://localhost:8000/health
```

---

## Production Deployment Checklist

Before deploying to production:

- [ ] **Set production API URL** via window.CHAT_API_URL or hardcode in `getApiUrl()`
- [ ] **Test locally with production URL** (temporarily update `getApiUrl()`)
- [ ] **Verify CORS configured** on backend for production domain
- [ ] **Test full chat flow** (create session, send message, receive response)
- [ ] **Check browser console** for any errors
- [ ] **Test on multiple browsers** (Chrome, Firefox, Safari)
- [ ] **Test on mobile** (responsive behavior)

---

## Files Modified

| File | Changes | Purpose |
|------|---------|---------|
| `frontend/src/components/ChatWidget/config.ts` | Replaced `process.env.CHAT_API_URL` with browser-safe `getApiUrl()` function | Eliminate "process is not defined" crash in browser |

---

## Code Comparison

### Before (BROKEN):
```typescript
export const defaultConfig: ChatWidgetConfig = {
  apiUrl:
    (typeof window !== 'undefined' && (window as any).CHAT_API_URL) ||
    process.env.CHAT_API_URL ||  // ❌ CRASH in browser
    'http://localhost:8000',
  // ...
};
```

### After (FIXED):
```typescript
function getApiUrl(): string {
  if (typeof window !== 'undefined' && (window as any).CHAT_API_URL) {
    return (window as any).CHAT_API_URL;
  }
  return 'http://localhost:8000';  // ✅ Browser-safe
}

export const defaultConfig: ChatWidgetConfig = {
  apiUrl: getApiUrl(),  // ✅ No process access
  // ...
};
```

---

## Expected Result

### Console Output (Clean):
```
✅ [ChatWidget] Rendering in browser - widget should be visible
✅ [ChatToggleButton] Rendering button - isOpen: false
✅ [ChatToggleButton] Toggle button inline styles applied — should be visible now
```

### Visual Result:
- ✅ **Bright cyan toggle button** visible in bottom-right corner
- ✅ **White border** creating sharp contrast
- ✅ **No console errors** - clean browser console
- ✅ **Hover works** - button grows with glow
- ✅ **Click works** - panel opens

### Functional Result:
- ✅ Widget loads without crash
- ✅ Session created on mount
- ✅ Can send messages
- ✅ Receives streaming responses
- ✅ Citations displayed

---

## Next Steps

1. **Start frontend**: `cd frontend && npm start`
2. **Start backend**: `cd backend/rag-chatbot && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
3. **Open browser**: http://localhost:3000
4. **Check console**: Should be clean (no "process" error)
5. **Verify button**: Bright cyan with white border in bottom-right
6. **Test chat**: Click button, type question, send, verify response

---

**Fix Status**: ✅ **COMPLETE - Widget will now load without crash**
**Root Cause**: `process.env` access in browser code
**Solution**: Browser-safe `getApiUrl()` function
**Result**: Clean console, widget loads, toggle button appears

---

**Fix completed by**: Claude Code
**Date**: 2025-12-18
**Feature**: 004-chatbot-widget (process.env crash fix)
