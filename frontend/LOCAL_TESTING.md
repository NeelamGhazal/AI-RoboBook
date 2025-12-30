# Local Frontend + Backend Testing Guide

## ✅ What Was Fixed

1. **API URL**: Changed from production Railway URL to `http://localhost:8000`
2. **Double slash bug**: Removed trailing slash from base URL

**File updated**: `src/components/ChatWidget/config.ts` (line 20)

---

## 🚀 Quick Start

### Step 1: Start Backend (If Not Running)

```powershell
cd E:\phyai-humanoid-textbook\backend\rag-chatbot
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Wait for: `"Application startup complete"`

### Step 2: Start Frontend

Open a **NEW terminal**:

```powershell
cd E:\phyai-humanoid-textbook\frontend
npm run dev
```

**Expected output**:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

### Step 3: Open Browser

Navigate to: **http://localhost:5173** (or whatever port Vite shows)

---

## ✅ Testing Checklist

### 1. Widget Appears
- [ ] Chat toggle button visible in bottom-right corner
- [ ] Click button → Chat panel opens
- [ ] No console errors about "process is not defined"
- [ ] No 404 errors for session creation

### 2. Normal Queries

Click the chat widget and test these queries:

**Query 1**: "What is ROS 2?"
- [ ] Response streams in (word by word)
- [ ] Accurate answer about ROS 2 robotics framework
- [ ] Citations appear at bottom
- [ ] No errors in console

**Query 2**: "Explain physics simulation"
- [ ] Detailed response about simulation fundamentals
- [ ] Citations from Module 2
- [ ] Clean formatting

**Query 3**: "What is Physical AI?"
- [ ] Grounded response from textbook
- [ ] Relevant citations

### 3. Selected Text Feature

**Test flow**:
1. Navigate to a page with textbook content (if available)
2. **Highlight a paragraph** (at least 50 characters)
3. Look for "Ask about this" button near selection
4. Click the button
5. Chatbot should:
   - [ ] Receive the selected text as context
   - [ ] Provide explanation based on that text
   - [ ] Show relevant citations

---

## 🔍 Expected Behavior

### Successful Response Format

When you ask a question, you should see:

1. **Streaming tokens** appearing progressively (not all at once)
2. **Response content** - accurate answer from textbook
3. **Citations** - Sources with chapter/section references
4. **Metadata** - Response time, chunks retrieved, etc.

### Console Logs (Normal)

```
[ChatWidget] Rendering in browser - widget should be visible
[ChatToggleButton] Rendering button - isOpen: false
[SelectedTextDetector] Installing selection listeners
[ChatApi] Creating session at: http://localhost:8000/api/v1/sessions
[ChatApi] Session created: <session-id>
[ChatApi] Sending message...
[ChatApi] Stream started
[ChatApi] Received token: ...
[ChatApi] Stream complete
```

### API Calls (Network Tab)

Check browser DevTools → Network tab:

✅ **Correct**:
```
POST http://localhost:8000/api/v1/sessions          → 200 OK
POST http://localhost:8000/api/v1/chat/stream       → 200 OK
```

❌ **Wrong** (if you see this, config wasn't updated):
```
POST https://proud-nourishment-production-7f99.up.railway.app//api/v1/sessions → 404
```

---

## 🐛 Troubleshooting

### Issue: Still seeing Railway URL in console

**Fix**: Clear browser cache and reload
```
Ctrl + Shift + R (Windows)
Cmd + Shift + R (Mac)
```

Or:
1. Stop frontend (`Ctrl+C`)
2. Clear Vite cache: `rm -rf node_modules/.vite`
3. Restart: `npm run dev`

### Issue: "Failed to create session: 404"

**Check**:
1. Backend is running: `curl http://localhost:8000/health`
2. URL in console shows `localhost:8000` (not Railway)
3. No double slash in URL

**Fix**:
```powershell
# Restart backend
cd E:\phyai-humanoid-textbook\backend\rag-chatbot
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Issue: "CORS error"

The backend should have CORS enabled for localhost. Check `.env`:
```
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8000
```

If Vite is using a different port (e.g., 5174), add it to CORS_ORIGINS and restart backend.

### Issue: Selected text feature not working

**Check**:
1. Text selection is at least 50 characters
2. Page has actual text content (not just UI elements)
3. Console shows: `[SelectedTextDetector] Installing selection listeners`

### Issue: Empty responses (token_count: 0)

This **should NOT happen** - we fixed this in backend!

If it does:
1. Check backend logs for errors
2. Verify `litellm==1.80.11` is installed: `pip show litellm`
3. Restart backend

---

## 📊 Performance Expectations

### Normal Query Response Time

- **Frontend → Backend**: < 100ms
- **Backend retrieval**: ~1 second
- **LLM generation**: ~2-3 seconds
- **Total**: 2.8-4.1 seconds

### Streaming Behavior

- Tokens should appear **progressively** (word by word)
- NOT all at once at the end
- Smooth animation effect

---

## 🎯 Demo Practice Flow

### Full Demo Sequence

1. **Open browser**: http://localhost:5173
2. **Click chatbot icon** (bottom-right)
3. **Ask**: "What is ROS 2?"
   - Watch streaming response
   - Point out citations
4. **Ask**: "Explain physics simulation for robotics"
   - Show detailed formatted response
5. **Navigate to textbook page** (if available)
6. **Highlight a paragraph**
7. **Click "Ask about this"**
   - Show context-aware explanation
8. **Close and reopen chat**
   - Verify session persistence (history loads)

### What to Highlight in Demo

✨ **Key Features**:
- ✅ Real-time streaming responses
- ✅ Grounded in textbook content (show citations)
- ✅ Context-aware with selected text
- ✅ Clean, modern UI (Tech Cyber theme)
- ✅ Session persistence (history maintained)

---

## 🔄 Quick Commands Reference

### Start Backend
```powershell
cd E:\phyai-humanoid-textbook\backend\rag-chatbot
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Start Frontend
```powershell
cd E:\phyai-humanoid-textbook\frontend
npm run dev
```

### Test Backend Health
```powershell
curl http://localhost:8000/health
```

### Test Backend Query
```powershell
curl -X POST "http://localhost:8000/api/v1/chat/stream" `
  -H "Content-Type: application/json" `
  -d '{\"session_id\": \"test\", \"question\": \"What is ROS 2?\"}'
```

### Restart Frontend (if needed)
```powershell
# Stop: Ctrl+C
# Clear cache
rm -rf node_modules/.vite
# Start
npm run dev
```

---

## ✅ Pre-Demo Checklist

Before the hackathon:

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Health check returns OK
- [ ] Test query works in backend
- [ ] Widget appears in browser
- [ ] Session created successfully (no 404)
- [ ] Normal query returns accurate response
- [ ] Streaming works smoothly
- [ ] Citations display correctly
- [ ] Selected text feature works
- [ ] No console errors
- [ ] Practiced full demo flow 2-3 times

---

## 🎉 You're Ready!

The frontend now connects to your local backend at `http://localhost:8000`.

**Next**: Practice the demo flow a few times to get comfortable with the timing and responses.

Good luck with your hackathon! 🚀
