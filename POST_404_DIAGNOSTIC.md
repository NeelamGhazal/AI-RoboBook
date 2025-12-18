# POST /api/v1/chat/stream Returns 404 - Root Cause Analysis

**Date**: 2025-12-18
**Status**: 🔍 DIAGNOSED - Session Validation Failure

---

## Symptom

- ✅ **GET `/api/v1/chat/health`** → 200 OK (router is registered correctly)
- ❌ **POST `/api/v1/chat/stream`** → 404 Not Found
- Frontend console: "Failed to load resource: the server responded with a status of 404"
- Empty message bubbles appearing (no response content)

---

## Root Cause

**The 404 is coming FROM the endpoint itself, not because the route doesn't exist.**

### Code Analysis

In `backend/rag-chatbot/app/api/v1/chat.py` lines 186-192:

```python
@router.post("/stream")
async def chat_stream(request: ChatRequest):
    print(f"[Backend] POST /api/v1/chat/stream called")

    # Validate session exists
    session_exists = await validate_session(request.session_id)
    if not session_exists:
        print(f"[Backend] ✗ Session validation failed: {request.session_id}")
        raise HTTPException(
            status_code=404,  # ← THIS IS THE 404!
            detail=f"Session {request.session_id} not found"
        )
```

**The endpoint IS registered and accessible, but it's returning 404 because the session validation is failing.**

---

## Why Session Validation Fails

### Session Storage Architecture

Sessions are stored in TWO places:

1. **Database** (Neon Postgres) - persistent
2. **In-memory dictionary** (Python module-level) - ephemeral

From `backend/rag-chatbot/app/api/v1/sessions.py` line 18:

```python
# In-memory session store (fallback if database fails)
_in_memory_sessions = {}  # ← MODULE-LEVEL DICT
```

### The Problem

**In-memory sessions are LOST on backend restart!**

1. Frontend creates session → `POST /api/v1/sessions`
   - Tries database first (may fail if DB unavailable)
   - Falls back to in-memory storage
   - Returns session_id to frontend

2. Frontend saves session_id to localStorage

3. **Backend restarts** (crash, code change, manual restart)
   - `_in_memory_sessions` dict is cleared (new Python process)
   - Database sessions persist
   - **In-memory sessions are GONE**

4. Frontend sends message with old session_id
   - `validate_session()` checks database (session not there if it was in-memory)
   - `validate_session()` checks `_in_memory_sessions` (empty after restart)
   - **Session not found** → 404

---

## Evidence to Verify This Hypothesis

### Check 1: Backend Console Logs

**What to look for**:

```bash
# When chat message is sent, you should see:
[Backend] POST /api/v1/chat/stream called
[Backend] Payload received: session_id=abc-123, question_length=25, has_selected_text=False
[Backend] ✗ Session validation failed: abc-123  # ← KEY LOG
```

**If you see "Session validation failed"**, this confirms the issue.

**If you DON'T see "POST /api/v1/chat/stream called"**, then the route truly isn't registered (different issue).

### Check 2: In-Memory Sessions Count

Add this to your backend startup logs (already exists in sessions.py line 88):

```python
print(f"[Backend] In-memory sessions count: {len(_in_memory_sessions)}")
```

After backend restart, this should be `0`. If frontend has a session ID from before restart, validation will fail.

### Check 3: Database Connectivity

Check if sessions are being created in the database:

```bash
# In backend logs, look for:
[Backend] ✓ Session created in database: <session_id>
# vs
[Backend] ⚠ Database session creation failed: <error>
[Backend] Falling back to in-memory session storage...
```

If database is down/unavailable, ALL sessions are in-memory only → lost on restart.

---

## Solutions

### Solution 1: Force Session Recreation on 404 (Frontend Fix)

**File**: `frontend/src/components/ChatWidget/hooks/useChatMessages.ts` (or wherever message sending is handled)

**Change**: When POST returns 404, automatically create new session and retry:

```typescript
try {
  await sendMessageStream(request, onEvent);
} catch (error) {
  if (error.statusCode === 404 && error.message.includes('Session')) {
    console.log('[ChatWidget] Session not found, creating new session...');

    // Clear old session from localStorage
    localStorage.removeItem('robobook_chat_session_id');

    // Create new session
    await initializeSession();

    // Retry with new session ID
    // (Note: This will lose conversation history)
    const newRequest = { ...request, session_id: sessionId };
    await sendMessageStream(newRequest, onEvent);
  } else {
    throw error;
  }
}
```

**Pros**: Automatic recovery, user doesn't need to refresh
**Cons**: Loses conversation history (in-memory messages are gone)

### Solution 2: Persistent Session Storage (Backend Fix)

**File**: `backend/rag-chatbot/app/api/v1/sessions.py`

**Change**: Use Redis or persistent cache instead of in-memory dict:

```python
# Replace module-level dict with Redis
import redis
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Session creation
redis_client.setex(
    f"session:{session_id}",
    86400,  # 24 hour TTL
    json.dumps(session_data)
)

# Session validation
session_data = redis_client.get(f"session:{session_id}")
```

**Pros**: Sessions survive backend restarts
**Cons**: Requires Redis dependency

### Solution 3: Fix Database Connection (Backend Fix)

**File**: `backend/rag-chatbot/.env` and database configuration

**Check**:
1. Is `NEON_DATABASE_URL` correctly set?
2. Is the Neon database accessible from backend?
3. Are there connection pool issues?

**Test**:
```bash
cd backend/rag-chatbot
python3 -c "
import asyncio
from app.clients.db_client import db_client
asyncio.run(db_client.connect())
result = asyncio.run(db_client.fetchval('SELECT 1'))
print('Database connection OK:', result)
"
```

If this fails, sessions aren't being persisted to database → lost on restart.

### Solution 4: Session Health Check (Frontend Enhancement)

**File**: `frontend/src/components/ChatWidget/context/ChatWidgetContext.tsx`

**Add**: Periodic session validation:

```typescript
useEffect(() => {
  const validateSession = async () => {
    if (!sessionId) return;

    try {
      // Check if session still exists
      const response = await fetch(`${apiUrl}/api/v1/sessions/${sessionId}`);
      if (!response.ok) {
        console.log('[ChatWidget] Session expired, creating new one...');
        await initializeSession();
      }
    } catch (err) {
      console.error('[ChatWidget] Session validation failed:', err);
    }
  };

  // Validate session every 5 minutes
  const interval = setInterval(validateSession, 5 * 60 * 1000);
  return () => clearInterval(interval);
}, [sessionId]);
```

**Pros**: Proactively detects stale sessions
**Cons**: Extra API calls

---

## Recommended Fix (Quickest Solution)

### Immediate Action: Frontend Auto-Recovery

**File**: `frontend/src/components/ChatWidget/hooks/useChatMessages.ts` (find the message sending logic)

**Add error handling**:

```typescript
const handleSessionNotFound = useCallback(async () => {
  console.log('[ChatWidget] Session not found (404), recreating session...');

  // Clear old session
  localStorage.removeItem('robobook_chat_session_id');

  // Create new session
  await initializeSession();

  // Clear messages (conversation history lost)
  setMessages([]);

  // Show info message to user
  setError('Your session expired. Starting a new conversation.');
  setTimeout(() => setError(null), 3000);
}, [initializeSession]);

// In sendMessage function:
try {
  await sendMessageStream(request, onEvent);
} catch (error) {
  if (error.statusCode === 404 && error.userMessage?.includes('Session')) {
    await handleSessionNotFound();
    // Don't throw - let user retry manually
    return;
  }
  throw error;
}
```

**This will**:
- Detect session 404 errors
- Automatically create new session
- Clear old conversation
- Let user send new message

**User experience**:
- First message after backend restart: "Your session expired. Starting a new conversation."
- User clicks send again → works with new session

---

## Long-Term Solution

**Fix database connectivity** so sessions are always persisted to Neon Postgres, not just in-memory.

**Check**:
1. Backend logs show: `[Backend] ✓ Session created in database`
2. NOT showing: `[Backend] ⚠ Database session creation failed`

**Test**:
```bash
# In backend console
[Backend] POST /api/v1/sessions called
[Backend] Session data: user_id=None, metadata=None
[Backend] Attempting database session creation...
[Backend] ✓ Session created in database: <session_id>  # ← MUST SEE THIS
```

If database creation works, sessions survive restarts → no 404s.

---

## Testing Verification

### Test Scenario: Backend Restart

1. **Start backend**: `cd backend/rag-chatbot && uvicorn app.main:app --reload`
2. **Open frontend**: Navigate to docs page
3. **Send first message**: Should work (new session created)
4. **Check backend console**: Note session ID
5. **Restart backend**: Ctrl+C and restart uvicorn
6. **Send second message** (same browser tab, same localStorage session):
   - **Expected behavior**: 404 (session not found)
   - **After fix**: Auto-creates new session, works

### Test Scenario: Database Connectivity

1. Check backend logs during session creation
2. Should see: `[Backend] ✓ Session created in database`
3. If you see: `[Backend] ⚠ Database session creation failed`
   - Fix database connection
   - Sessions are being stored in-memory only

---

## Summary

| Symptom | Root Cause | Solution |
|---------|------------|----------|
| POST `/api/v1/chat/stream` → 404 | Session validation failing | Frontend auto-recovery + database fix |
| GET `/api/v1/chat/health` → 200 OK | Router is registered correctly | No action needed |
| Empty message bubbles | No response content (404 error) | Fix session issue |

**The route exists. The 404 comes from session validation failure inside the endpoint.**

**Quick fix**: Frontend auto-recovery on 404
**Proper fix**: Ensure database session persistence works

---

## Files to Modify

### Quick Fix (Frontend):
- `frontend/src/components/ChatWidget/hooks/useChatMessages.ts` (add error handling)
- `frontend/src/components/ChatWidget/context/ChatWidgetContext.tsx` (add session validation)

### Proper Fix (Backend):
- Fix database connectivity (check `.env` and Neon connection)
- OR use Redis for session storage instead of in-memory dict
- OR implement session persistence layer

---

## Next Steps

1. **Check backend console** when sending message - look for "Session validation failed" log
2. **Verify database connection** - are sessions being created in DB or in-memory?
3. **Implement frontend auto-recovery** - handle 404 by recreating session
4. **Test backend restart** scenario - verify fix works

**Most likely**: Database is unavailable, sessions are in-memory only, lost on restart → 404.
