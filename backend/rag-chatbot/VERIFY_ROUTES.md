# Route Verification Guide

## ✅ The Code Is Correct

I've verified that the route configuration is correct in the codebase:

- ✅ `app/api/v1/chat.py` line 20: `router = APIRouter(tags=["chat"])` (NO prefix)
- ✅ `app/main.py` line 187: `app.include_router(chat.router, prefix="/api/v1/chat")`
- ✅ `app/api/v1/chat.py` line 169: `@router.post("/stream")`

**This should create**: `POST /api/v1/chat/stream` ✅

---

## 🔍 **Problem: The Server Might Not Be Using the New Code**

If you're still getting 404, it means **the running server hasn't loaded the updated code**.

---

## 🚀 **Solution: Force Complete Restart**

### **Method 1: Run Debug Script (Recommended)**

```powershell
cd E:\phyai-humanoid-textbook\backend\rag-chatbot
.\debug-routes.ps1
```

This will:
1. Kill ALL Python processes
2. Verify code changes
3. Start server fresh
4. Test all endpoints
5. Show you exactly what's working/broken

---

### **Method 2: Manual Complete Restart**

#### Step 1: Kill ALL Python Processes

```powershell
# Kill everything
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Verify nothing is running
Get-Process python -ErrorAction SilentlyContinue
```

**Expected**: No output (all processes killed)

#### Step 2: Check Port 8000

```powershell
netstat -ano | findstr ":8000"
```

**Expected**: No output (port is free)

If you see output, something is still using port 8000:
```powershell
# Find the PID and kill it
netstat -ano | findstr ":8000"
# Example output: TCP 0.0.0.0:8000 0.0.0.0:0 LISTENING 12345
# Kill process 12345
taskkill /F /PID 12345
```

#### Step 3: Start Server Fresh

```powershell
cd E:\phyai-humanoid-textbook\backend\rag-chatbot
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Step 4: **CRITICAL - Check Startup Logs**

Wait for startup to complete, then **look for these lines**:

**You MUST see**:
```
[Backend] ✓ Chat router registered: /api/v1/chat
[Backend] Available endpoints:
[Backend] - POST /api/v1/chat/stream        ← This line is KEY
[Backend] - GET /api/v1/chat/health
[Backend] - GET /api/v1/chat/test

[Backend] ===== Registered Routes =====
...
[Backend] POST                 /api/v1/chat/stream     ← This confirms it's registered
...
```

**If you see** (OLD/WRONG):
```
[Backend] POST /api/v1/chat/api/v1/chat/stream  ← WRONG (double prefix)
```

Then the old code is still running - repeat Steps 1-3.

#### Step 5: Test Endpoints

**Open a NEW PowerShell window** (keep server running):

```powershell
# Test 1: Main health
curl http://localhost:8000/health

# Test 2: Chat health
curl http://localhost:8000/api/v1/chat/health

# Test 3: Stream endpoint (THE CRITICAL ONE)
curl -X POST "http://localhost:8000/api/v1/chat/stream" `
  -H "Content-Type: application/json" `
  -d '{\"session_id\": \"test\", \"question\": \"test\"}'
```

**Expected for Test 3**:
- ✅ Status 200
- ✅ Streaming response starts
- ❌ NOT 404!

---

## 🐛 **If STILL Getting 404**

### Check 1: Verify File Changes

```powershell
# Check chat.py router definition
Select-String -Path "app\api\v1\chat.py" -Pattern "router = APIRouter"
```

**Expected**:
```
20:router = APIRouter(tags=["chat"])
```

**NOT**:
```
20:router = APIRouter(prefix="/api/v1/chat", tags=["chat"])
```

If it shows the prefix, the file wasn't saved. Open `app/api/v1/chat.py` and manually fix line 20:

**Change**:
```python
router = APIRouter(prefix="/api/v1/chat", tags=["chat"])
```

**To**:
```python
router = APIRouter(tags=["chat"])
```

Save the file and restart.

### Check 2: Verify main.py

```powershell
Select-String -Path "app\main.py" -Pattern "include_router\(chat.router"
```

**Expected**:
```
187:app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
```

### Check 3: Are You in the Right Directory?

```powershell
pwd
```

**Expected**:
```
Path
----
E:\phyai-humanoid-textbook\backend\rag-chatbot
```

If not, navigate there:
```powershell
cd E:\phyai-humanoid-textbook\backend\rag-chatbot
```

### Check 4: Python Cache Issue

```powershell
# Clear Python cache
Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force
Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force

# Restart server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 📋 **Expected Route List**

After server starts correctly, you should see:

```
[Backend] ===== Registered Routes =====
[Backend] GET, HEAD            /openapi.json
[Backend] GET, HEAD            /docs
[Backend] GET, HEAD            /redoc
[Backend] GET                  /
[Backend] GET                  /health
[Backend] POST                 /api/v1/sessions          ← Sessions
[Backend] GET                  /api/v1/sessions/{id}     ← Sessions
[Backend] GET                  /api/v1/chat/health       ← Chat router
[Backend] POST                 /api/v1/chat              ← Chat router
[Backend] POST                 /api/v1/chat/stream       ← THIS IS THE KEY ONE ✅
[Backend] GET                  /api/v1/chat/history/{id} ← Chat router
[Backend] ===================================
```

---

## ✅ **Success Checklist**

- [ ] Killed all Python processes
- [ ] Port 8000 is free
- [ ] Started server fresh
- [ ] Saw correct routes in startup logs
- [ ] `/api/v1/chat/stream` appears in route list
- [ ] `curl` to `/api/v1/chat/stream` returns 200 (not 404)
- [ ] Frontend can send messages without 404 errors

---

## 🎯 **Once Working**

After the stream endpoint works:

1. **Test Frontend**:
   ```powershell
   cd E:\phyai-humanoid-textbook\frontend
   npm run dev
   ```

2. **Open browser**: http://localhost:5173

3. **Test queries**:
   - "What is ROS 2?"
   - "Explain physics simulation"
   - Highlight text → "Ask about this"

4. **Verify**:
   - ✅ No 404 errors
   - ✅ Streaming responses
   - ✅ Citations appear
   - ✅ Selected text works

---

## 🆘 **Last Resort**

If nothing works, manually edit the files:

1. **Open**: `E:\phyai-humanoid-textbook\backend\rag-chatbot\app\api\v1\chat.py`

2. **Find line 20**: Should be:
   ```python
   router = APIRouter(tags=["chat"])
   ```

3. **If it has a prefix**, remove it and save

4. **Restart server** with ALL processes killed first

---

**The code in the repository IS correct. The issue is likely a caching or process issue on your machine.**

**Run `.\debug-routes.ps1` for automatic diagnosis!**
