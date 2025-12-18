# Frontend Streaming Debug Guide

**Date**: 2025-12-18
**Status**: ✅ Enhanced logging added for debugging

---

## Changes Made

### Files Modified with Enhanced Logging

1. **`frontend/src/components/ChatWidget/api/chatApi.ts`**
   - Added raw event data logging
   - Log first 3 tokens and every 10th token with actual content
   - Log non-data lines for debugging
   - Enhanced error logging with raw line data

2. **`frontend/src/components/ChatWidget/hooks/useChatStream.ts`**
   - Log every event type received
   - Log token content and running total
   - Show response preview as it builds
   - Warn if event missing expected fields
   - Log final response length on completion

3. **`frontend/src/components/ChatWidget/context/ChatWidgetContext.tsx`**
   - Log updateLastMessage calls with content length
   - Show content preview
   - Log message ID being updated
   - Show before/after content lengths
   - Warn if no messages exist to update

---

## Expected Console Logs Flow

### When Sending a Message

**Step 1: Request Initiation**
```
[ChatApi] Starting stream request to: http://localhost:8000/api/v1/chat/stream
[ChatApi] Request payload: {session_id: "abc-123", question_length: 15, has_selected_text: false}
```

**Step 2: Response Received**
```
[ChatApi] Stream response status: 200 OK
[ChatApi] Stream started successfully
```

**Step 3: First Token**
```
[ChatApi] First raw event data: {"type":"token","content":"Hello! "}
[ChatApi] Token #1: Hello!
[ChatStream] Received event: token
[ChatStream] Token added, full response length: 7
[ChatStream] Current response preview: Hello! ...
[ChatWidgetContext] updateLastMessage called with content length: 7
[ChatWidgetContext] Content preview: Hello!
[ChatWidgetContext] Updating message ID: assistant-1734567890123
[ChatWidgetContext] Old content length: 0
[ChatWidgetContext] New content length: 7
```

**Step 4: Subsequent Tokens**
```
[ChatApi] Token #2: You
[ChatStream] Received event: token
[ChatStream] Token added, full response length: 11
[ChatStream] Current response preview: Hello! You ...
[ChatWidgetContext] updateLastMessage called with content length: 11
...

[ChatApi] Token #3: asked:
[ChatStream] Received event: token
[ChatStream] Token added, full response length: 19
[ChatStream] Current response preview: Hello! You asked: ...
[ChatWidgetContext] updateLastMessage called with content length: 19
...
```

**Step 5: Citations**
```
[ChatApi] Stream event: citations {...}
[ChatStream] Received event: citations
[ChatStream] Citations received: 1 sources
[ChatWidgetContext] updateLastMessage called with content length: 150
[ChatWidgetContext] Content preview: Hello! You asked: "What is ROS 2?" This is a test response...
```

**Step 6: Done**
```
[ChatApi] Stream event: done {}
[ChatStream] Received event: done
[ChatStream] ✓ Stream done! Final response length: 150
[ChatApi] Stream ending, event type: done
[ChatApi] Stream completed, total chunks: 52
```

---

## Debugging Checklist

### ✅ If Streaming Works (Expected Behavior)

**Console logs show**:
- [ChatApi] Stream response status: 200 OK
- [ChatApi] Token #1: Hello!
- [ChatStream] Token added, full response length: X
- [ChatWidgetContext] updateLastMessage called with content length: X
- **Chat widget displays progressive text**

**UI shows**:
- User message appears immediately
- Assistant message box appears
- Text appears word-by-word (progressive)
- Citations appear at end
- No error messages

---

### ❌ Problem: Empty Message Box

**Symptom**: Message box appears but no text inside

**Check console for**:
1. Are tokens being received?
   ```
   [ChatApi] Token #1: ...
   ```
   - ✅ YES → Tokens received, continue to #2
   - ❌ NO → Backend not sending tokens, check backend

2. Is ChatStream receiving events?
   ```
   [ChatStream] Received event: token
   ```
   - ✅ YES → Events received, continue to #3
   - ❌ NO → Parser not working, check for parse errors

3. Is content being extracted?
   ```
   [ChatStream] Token added, full response length: X
   ```
   - ✅ YES → Content extracted, continue to #4
   - ❌ NO → Check for warning: "Token event missing content"

4. Is updateLastMessage being called?
   ```
   [ChatWidgetContext] updateLastMessage called with content length: X
   ```
   - ✅ YES → Context updated, continue to #5
   - ❌ NO → Event handler not calling updateLastMessage

5. Is message being updated?
   ```
   [ChatWidgetContext] Updating message ID: assistant-...
   [ChatWidgetContext] New content length: X
   ```
   - ✅ YES → Message updated, check UI rendering
   - ❌ NO → Check for warning: "No messages to update!"

---

### ❌ Problem: Parse Errors

**Symptom**: Console shows parse errors

**Look for**:
```
[ChatApi] Failed to parse SSE event: data: ...
[ChatApi] Raw line that failed: ...
```

**Common causes**:
1. Backend sending invalid JSON
2. Backend sending wrong format (not `{"type":"token","content":"..."}`)
3. Line breaks in JSON

**Solution**: Check backend logs to see what's actually being sent

---

### ❌ Problem: No Events Received

**Symptom**: No token logs at all

**Check**:
1. Backend logs show tokens being sent?
   ```bash
   # Backend should show:
   [Backend] ✓✓✓ POST /stream endpoint called!
   [Backend] Starting token generation...
   [Backend] Sent 1/50 tokens
   ```

2. Frontend gets 200 response?
   ```
   [ChatApi] Stream response status: 200 OK
   ```

3. Check for CORS errors in console
   ```
   Access to fetch at 'http://localhost:8000/api/v1/chat/stream'
   from origin 'http://localhost:3000' has been blocked by CORS policy
   ```

---

## Testing Steps

### Step 1: Start Backend

```bash
cd backend/rag-chatbot
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify startup logs**:
```
[Backend] ✓ Minimal chat router registered: /api/v1/chat
[Backend] POST                 /api/v1/chat/stream
```

### Step 2: Start Frontend

```bash
cd frontend
npm start
```

**Open**: http://localhost:3000

### Step 3: Open Browser DevTools

1. Press F12 or right-click → Inspect
2. Go to Console tab
3. Clear console (trash icon)

### Step 4: Send Test Message

1. Open chat widget (click chat icon)
2. Type: "What is ROS 2?"
3. Press send

### Step 5: Watch Console Logs

**Should see (in order)**:
1. [ChatApi] Starting stream request...
2. [ChatApi] Stream response status: 200 OK
3. [ChatApi] First raw event data: {"type":"token",...}
4. [ChatApi] Token #1: ...
5. [ChatStream] Received event: token
6. [ChatStream] Token added...
7. [ChatWidgetContext] updateLastMessage called...
8. (Repeat for each token)
9. [ChatStream] ✓ Stream done!

**UI should show**:
- Text appearing progressively (word by word)
- No empty box
- No errors

---

## Common Issues & Solutions

### Issue 1: Warning "Token event missing content"

**Console shows**:
```
[ChatStream] Token event missing content: {type: "token"}
```

**Cause**: Backend sending `{"type": "token"}` without `content` field

**Solution**: Check backend - should send `{"type": "token", "content": "text"}`

**Backend fix** (in `chat_minimal.py`):
```python
token_event = {
    "type": "token",
    "content": word + " "  # ← Must include content field
}
```

---

### Issue 2: Warning "No messages to update!"

**Console shows**:
```
[ChatWidgetContext] No messages to update!
```

**Cause**: updateLastMessage called before assistant message created

**Check**: useChatStream should create placeholder message BEFORE streaming:
```typescript
// Create placeholder for assistant message
const assistantMessage: Message = {
  id: `assistant-${Date.now()}`,
  role: 'assistant',
  content: '',  // ← Empty initially
  timestamp: new Date(),
  citations: [],
};
addMessage(assistantMessage);  // ← Add BEFORE streaming
```

---

### Issue 3: Parse Error "Unexpected token"

**Console shows**:
```
[ChatApi] Failed to parse SSE event: data: {"type":"token
SyntaxError: Unexpected end of JSON input
```

**Cause**: Line split in middle of JSON

**This is expected**: SSE parser buffers incomplete lines and waits for complete JSON

**If persistent**: Check backend is sending `\n\n` after each event:
```python
yield f'data: {json.dumps(event)}\n\n'  # ← Must have \n\n
```

---

### Issue 4: Stream Starts Then Stops

**Console shows**:
```
[ChatApi] Token #1: Hello
[ChatApi] Token #2: You
(no more logs)
```

**Causes**:
1. Backend stopped sending (check backend logs)
2. Stream timeout (default 30 seconds)
3. Network error

**Check backend**:
```bash
# Should see continuous logs:
[Backend] Sent 1/50 tokens
[Backend] Sent 2/50 tokens
...
```

---

## Manual Testing Commands

### Test 1: Backend Streaming Works

```bash
curl -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test","question":"Hello"}'
```

**Should see**:
```
data: {"type":"token","content":"Hello! "}

data: {"type":"token","content":"You "}

data: {"type":"citations","citations":[...]}

data: {"type":"done"}
```

**NOT**:
```
{"detail":"Not Found"}  ← Backend not running or route not registered
```

### Test 2: Frontend API Client

Open browser console and run:
```javascript
// Test API endpoint directly
fetch('http://localhost:8000/api/v1/chat/stream', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    session_id: 'test-123',
    question: 'What is ROS 2?'
  })
})
.then(res => res.body.getReader())
.then(reader => reader.read())
.then(({value}) => console.log(new TextDecoder().decode(value)))
```

**Should log**:
```
data: {"type":"token","content":"Hello! "}
```

---

## Summary

**Enhanced logging added to**:
- ✅ API client (chatApi.ts) - raw events, parsing, tokens
- ✅ Stream hook (useChatStream.ts) - event handling, content building
- ✅ Context (ChatWidgetContext.tsx) - message updates

**Expected flow**:
1. Request sent → Response 200 OK
2. Tokens received → Parsed correctly
3. Events handled → Content accumulated
4. Messages updated → UI renders

**If streaming doesn't work**:
1. Check console logs (follow this guide)
2. Identify which step fails
3. Apply corresponding solution

**Status**: Ready for testing with comprehensive logging!
