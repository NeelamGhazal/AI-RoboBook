# Chat Endpoint 404 Fix

## ✅ Problem Fixed

**Issue**: Frontend getting 404 error when calling `/api/v1/chat/stream`

**Root Cause**: Prefix was being **doubled** in the router configuration

### Before (WRONG):
```python
# In chat.py
router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

# In main.py
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
```

**Result**: Routes became `/api/v1/chat/api/v1/chat/stream` ❌

### After (FIXED):
```python
# In chat.py
router = APIRouter(tags=["chat"])  # No prefix here

# In main.py
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
```

**Result**: Routes are correctly `/api/v1/chat/stream` ✅

---

## 🚀 How to Test

### Step 1: Restart Backend

**IMPORTANT**: Stop your current backend server (`Ctrl+C`) and restart:

```powershell
cd E:\phyai-humanoid-textbook\backend\rag-chatbot
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Wait for**: `"Application startup complete"` (~10-15 seconds)

### Step 2: Verify Routes Are Correct

Check the startup logs - you should see:

```
[Backend] ✓ Chat router registered: /api/v1/chat
[Backend] Available endpoints:
[Backend] - POST /api/v1/chat/stream
[Backend] - GET /api/v1/chat/health
[Backend] - GET /api/v1/chat/test

[Backend] ===== Registered Routes =====
...
[Backend] POST                 /api/v1/chat/stream       ✅ (not /api/v1/chat/api/v1/chat/stream)
...
```

### Step 3: Test Chat Health Endpoint

```powershell
curl http://localhost:8000/api/v1/chat/health
```

**Expected response**:
```json
{
  "status": "healthy",
  "message": "Chat router is loaded and accessible",
  "endpoints": {
    "stream": "POST /api/v1/chat/stream",
    "chat": "POST /api/v1/chat",
    "history": "GET /api/v1/chat/history/{session_id}",
    "health": "GET /api/v1/chat/health"
  }
}
```

### Step 4: Test Stream Endpoint Directly

```powershell
curl -X POST "http://localhost:8000/api/v1/chat/stream" `
  -H "Content-Type: application/json" `
  -d '{\"session_id\": \"test-direct\", \"question\": \"What is ROS 2?\"}'
```

**Expected**: Streaming response (not 404!)
```
data: {"type": "token", "content": "ROS 2..."}
data: {"type": "citations", "citations": [...]}
...
```

---

## ✅ Frontend Testing

### Step 1: Frontend Should Already Work

If your frontend is already running, just **refresh the page** (or restart frontend):

```powershell
# If needed, restart frontend
cd E:\phyai-humanoid-textbook\frontend
npm run dev
```

### Step 2: Open Browser

Navigate to: **http://localhost:5173**

### Step 3: Test Chat Widget

**Open chat widget** → Type message → Press Enter

**Expected behavior**:
- ✅ No 404 errors in console
- ✅ Response streams in word-by-word
- ✅ Accurate answer from textbook
- ✅ Citations appear at bottom

### Step 4: Check Console (Should Be Clean)

**Console should show**:
```
[ChatApi] Creating session at: http://localhost:8000/api/v1/sessions
[ChatApi] Session created: <session-id>
[ChatApi] Sending message...
[ChatApi] Stream started
[ChatApi] Received token: ...
[ChatApi] Stream complete
```

✅ **No 404 errors**
✅ **No "Failed to load resource" errors**

### Step 5: Test Queries

Try these in the chat:

1. **"What is ROS 2?"**
   - Should get detailed response about Robot Operating System
   - Citations from Module 1

2. **"Explain physics simulation"**
   - Should get explanation of simulation fundamentals
   - Citations from Module 2

3. **"What are the main components of ROS 2?"**
   - Should list nodes, topics, services, actions
   - Citations included

### Step 6: Test Selected Text Feature

1. Navigate to a page with textbook content
2. **Highlight a paragraph** (50+ characters)
3. Click **"Ask about this"** button
4. Should get explanation based on that specific text
5. Citations should reference relevant sections

---

## 🎯 Expected API Endpoints (Correct Paths)

After the fix, these are the correct endpoints:

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Main health check |
| POST | `/api/v1/sessions` | Create session |
| GET | `/api/v1/sessions/{id}` | Get session |
| GET | `/api/v1/chat/health` | Chat router health |
| POST | `/api/v1/chat` | Non-streaming chat |
| POST | `/api/v1/chat/stream` | **Streaming chat** ✅ |
| GET | `/api/v1/chat/history/{id}` | Get chat history |

---

## 🐛 Troubleshooting

### Still Getting 404 on /api/v1/chat/stream

**Check**:
1. Did you restart the backend? (`Ctrl+C` then start again)
2. Check startup logs for:
   ```
   [Backend] POST /api/v1/chat/stream
   ```
   (NOT `/api/v1/chat/api/v1/chat/stream`)

### Routes Show Double Path

**Old server still running**:
```powershell
# Kill all Python processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Start fresh
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Still Shows 404

**Clear browser cache**:
- Windows: `Ctrl + Shift + R`
- Or restart frontend:
  ```powershell
  # Stop frontend (Ctrl+C)
  cd E:\phyai-humanoid-textbook\frontend
  rm -rf node_modules/.vite
  npm run dev
  ```

---

## ✅ Success Indicators

You know it's working when:

- [x] Backend starts without errors
- [x] Startup logs show `/api/v1/chat/stream` (single prefix)
- [x] `/api/v1/chat/health` returns 200 OK
- [x] Frontend opens without console errors
- [x] Chat message sends successfully
- [x] Response streams in progressively
- [x] Citations appear
- [x] Selected text feature works

---

## 🎉 Next: Demo Practice

Once all tests pass:

1. Practice the full demo flow 2-3 times
2. Test both normal queries and selected text
3. Verify streaming is smooth
4. Check citations are accurate
5. Make sure there are no console errors

**You're ready for the hackathon!** 🚀
