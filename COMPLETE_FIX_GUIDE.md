# 🚨 COMPLETE FIX GUIDE - RoboBook Chat Widget

## Problem Summary
- ✅ Backend (WSL): Working perfectly - retrieves chunks, generates responses
- ❌ Frontend (Windows): Can't reach WSL backend via `localhost:8000`
- **Root Cause**: Windows and WSL have separate `localhost` networks

## WSL Backend IP: `172.25.218.26`

---

## 🔧 FIX #1: Update Frontend to Use WSL IP (ALREADY DONE)

**File Updated**: `frontend/src/components/ChatWidget/config.ts` line 20

**Changed from**:
```typescript
return 'http://localhost:8000';
```

**Changed to**:
```typescript
return 'http://172.25.218.26:8000';  // WSL backend IP
```

---

## 🔧 FIX #2: Rebuild Frontend (EXECUTE THESE COMMANDS)

### **From Windows PowerShell OR WSL Terminal**:

```bash
# Navigate to frontend
cd /mnt/e/phyai-humanoid-textbook/frontend

# Clear Docusaurus cache and build artifacts
rm -rf .docusaurus
rm -rf build
rm -rf node_modules/.cache

# Rebuild fresh
npm run build

# Start Docusaurus development server
npm run start
```

**Expected Output**:
```
[SUCCESS] Serving "build" directory at: http://localhost:3000/
```

---

## 🔧 FIX #3: Verify Backend is Accessible from Windows

### **From Windows PowerShell**:

```powershell
# Test WSL backend health (use WSL IP)
curl http://172.25.218.26:8000/health

# Test chat stream endpoint
curl -X POST "http://172.25.218.26:8000/api/v1/chat/stream" `
  -H "Content-Type: application/json" `
  -d '{\"session_id\": \"test-windows\", \"question\": \"What is ROS 2?\"}'
```

**Expected for Health**:
```json
{"status":"healthy","timestamp":"...","dependencies":{"postgres":"up","qdrant":"up",...}}
```

**Expected for Stream**:
```
data: {"type": "token", "content": "ROS 2 (Robot Operating System 2)..."}
data: {"type": "citations", "citations": [{"chunk_id": "ba1f0484-...", "confidence_score": 0.71,...}]}
data: {"type": "metadata", "metadata": {"chunks_retrieved": 3,...}}
data: {"type": "done"}
```

If you get **connection errors**, the WSL backend isn't accessible from Windows. See Alternative Fix below.

---

## 🧪 VERIFICATION STEPS

### **1. Check Backend Logs (WSL Terminal)**

While backend is running in WSL, you should see:
```
[Backend] qdrant_collection_verified    points_count=913
[Backend] POST                 /api/v1/chat/stream
```

### **2. Test in Browser (Windows)**

1. Open: `http://localhost:3000`
2. Wait for page to load fully
3. Click chat widget button (bottom-right corner)
4. Ask: **"What is ROS 2?"**

**Expected**:
- ✅ Response streams in word-by-word
- ✅ Full answer about ROS 2 robotics framework
- ✅ Citations appear at bottom (Module1 Chapter 1, Module3 Chapter 1)
- ✅ No "couldn't find relevant information" message

### **3. Check Browser Console (F12)**

**Expected Logs**:
```
[ChatApi] Creating session at: http://172.25.218.26:8000/api/v1/sessions
[ChatApi] Session created: <uuid>
[ChatApi] Sending message...
[ChatApi] Stream started
[ChatApi] Received token: ROS
[ChatApi] Received token: 2
...
[ChatApi] Stream complete
```

**NO Errors Like**:
- ❌ `net::ERR_CONNECTION_REFUSED`
- ❌ `Failed to fetch`
- ❌ `WebSocket connection failed`

---

## 🛠️ ALTERNATIVE FIX: Run Backend Natively on Windows

If WSL networking doesn't work, run backend directly in Windows:

### **Step 1: Stop WSL Backend**

**In WSL terminal**:
```bash
pkill -f "uvicorn app.main:app"
```

### **Step 2: Start Backend in Windows PowerShell**

```powershell
cd E:\phyai-humanoid-textbook\backend\rag-chatbot

# Clear Python cache
Get-ChildItem -Path . -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force

# Install dependencies (if needed)
pip install -r requirements.txt

# Start backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### **Step 3: Update Frontend Config Back**

**Edit**: `frontend/src/components/ChatWidget/config.ts` line 20:
```typescript
return 'http://localhost:8000';  // Windows backend
```

### **Step 4: Rebuild Frontend**

```bash
cd /mnt/e/phyai-humanoid-textbook/frontend
rm -rf .docusaurus build node_modules/.cache
npm run build
npm run start
```

---

## 🎯 TESTING CHECKLIST

After fixes, test these scenarios:

### ✅ Test 1: Normal Query
- **Query**: "What is ROS 2?"
- **Expected**: Detailed response with citations from Module1 Chapter 1
- **Confidence**: ~0.71

### ✅ Test 2: Physics Simulation Query
- **Query**: "Explain physics simulation for robotics"
- **Expected**: Explanation from Module2, citations
- **Confidence**: ~0.60+

### ✅ Test 3: Selected Text Feature
1. Navigate to any docs page with text
2. Highlight a paragraph (50+ characters)
3. Click "Ask about this" button
4. **Expected**: Context-aware response referencing selected text

### ✅ Test 4: Session Persistence
1. Ask a question
2. Refresh page
3. Open chat widget
4. **Expected**: Previous conversation history loads

---

## 📊 BACKEND VERIFICATION

The backend is **confirmed working**. Test results from WSL:

```
Query: "What is ROS 2?"
✅ Retrieval: 3 chunks found (1.0s)
✅ Citations:
   - Module1 Chapter 1: ROS 2 Architecture (confidence: 0.71)
   - Module3 Chapter 1: Isaac Sim Introduction (confidence: 0.62)
✅ Generation: 4.4s
✅ Total time: 5.5s
✅ Response: Full detailed answer about ROS 2
```

**Qdrant Status**:
- ✅ 913 textbook chunks loaded
- ✅ 384-dimensional vectors (all-MiniLM-L6-v2 embeddings)
- ✅ Collection verified and accessible

---

## 🐛 TROUBLESHOOTING

### Issue: Still getting "couldn't find relevant information"

**Check**:
```bash
# In browser console (F12)
console.log('API URL:', window.localStorage.getItem('debug_api_url'))
```

If it shows `localhost:8000`, the old config is cached. Fix:
```bash
# Clear frontend cache completely
cd /mnt/e/phyai-humanoid-textbook/frontend
rm -rf .docusaurus build node_modules/.cache
npm run build
```

### Issue: WebSocket errors in console

**Cause**: Normal Docusaurus hot-reload behavior. Safe to ignore.

**To disable hot-reload**, use production build:
```bash
npm run build
npm run serve  # Production server (no hot-reload)
```

### Issue: ChunkLoadError for JS files

**Fix**:
```bash
# Clear browser cache: Ctrl+Shift+R (Windows)
# OR
# Clear all caches and rebuild:
cd /mnt/e/phyai-humanoid-textbook/frontend
rm -rf .docusaurus build node_modules/.cache
npm run build
npm run start
```

### Issue: Can't reach WSL backend from Windows

**Test WSL IP accessibility**:
```powershell
# From Windows PowerShell
curl http://172.25.218.26:8000/health
```

If this fails:
1. Check WSL firewall: `sudo ufw status`
2. Try running backend on Windows instead (see Alternative Fix above)
3. Or use `localhost:8000` and run backend in Windows

---

## 🎉 SUCCESS CRITERIA

You'll know everything is working when:

1. ✅ Browser opens `http://localhost:3000`
2. ✅ Chat widget appears (bottom-right)
3. ✅ Ask "What is ROS 2?"
4. ✅ Response streams in progressively
5. ✅ Accurate answer from textbook content
6. ✅ Citations display: Module1 Chapter 1 (0.71), Module3 Chapter 1 (0.62)
7. ✅ No console errors
8. ✅ Selected text feature works

---

## 📌 QUICK COMMANDS SUMMARY

```bash
# BACKEND (WSL) - Already running and working
cd /mnt/e/phyai-humanoid-textbook/backend/rag-chatbot
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# FRONTEND (Windows or WSL)
cd /mnt/e/phyai-humanoid-textbook/frontend
rm -rf .docusaurus build node_modules/.cache
npm run build
npm run start

# TEST from Windows PowerShell
curl http://172.25.218.26:8000/health
curl -X POST "http://172.25.218.26:8000/api/v1/chat/stream" `
  -H "Content-Type: application/json" `
  -d '{\"session_id\": \"test\", \"question\": \"What is ROS 2?\"}'

# BROWSER
# Open: http://localhost:3000
# Open chat widget → Ask: "What is ROS 2?"
```

---

**Your demo is ready! 🚀**
