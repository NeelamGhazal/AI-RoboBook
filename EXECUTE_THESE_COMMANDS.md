# 🚀 EXECUTE THESE COMMANDS NOW

## ✅ FIXES ALREADY APPLIED

1. **Frontend config updated**: Changed API URL from `localhost:8000` to `http://172.25.218.26:8000`
2. **Frontend caches cleared**: Removed `.docusaurus`, `build`, `node_modules/.cache`
3. **Frontend rebuild started**: Running in background

---

## 📋 NEXT STEPS - RUN THESE COMMANDS

### **Option 1: From WSL Terminal (Recommended)**

```bash
# Navigate to frontend
cd /mnt/e/phyai-humanoid-textbook/frontend

# Wait for current build to complete (check with):
ps aux | grep "npm run build"

# If build is still running, wait ~2-3 minutes
# Once complete, start dev server:
npm run start
```

**Expected Output**:
```
[SUCCESS] Serving "build" directory at: http://localhost:3000/
[INFO] Docs website: http://localhost:3000/
```

### **Option 2: From Windows PowerShell**

```powershell
# Navigate to frontend
cd E:\phyai-humanoid-textbook\frontend

# Check if build is complete (should see 'build' folder)
ls build

# If build folder exists, start server:
npm run start

# If build folder doesn't exist yet:
npm run build
# Then:
npm run start
```

---

## 🧪 TESTING - Run These Tests

### **Test 1: Verify WSL Backend is Accessible from Windows**

**From Windows PowerShell**:
```powershell
# Test health endpoint
curl http://172.25.218.26:8000/health
```

**Expected**:
```json
{"status":"healthy","timestamp":"2025-12-26T...","dependencies":{"postgres":"up","qdrant":"up",...}}
```

If you get **"Connection refused"** or **timeout**, your Windows firewall is blocking WSL. Try:
```powershell
# Allow WSL through firewall (run as Administrator)
New-NetFirewallRule -DisplayName "WSL Backend" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

### **Test 2: Test Chat Stream Endpoint**

```powershell
curl -X POST "http://172.25.218.26:8000/api/v1/chat/stream" `
  -H "Content-Type: application/json" `
  -d '{\"session_id\": \"test-final\", \"question\": \"What is ROS 2?\"}'
```

**Expected** (streaming response):
```
data: {"type": "token", "content": "ROS 2 (Robot Operating System 2)..."}
data: {"type": "citations", "citations": [{"chunk_id": "ba1f0484-...", "confidence_score": 0.71,...}]}
data: {"type": "metadata", "metadata": {"chunks_retrieved": 3,...}}
data: {"type": "done"}
```

---

## 🌐 BROWSER TESTING

### **Step 1: Open Browser**
```
http://localhost:3000
```

### **Step 2: Open Developer Console**
- Press **F12** (Windows)
- Go to **Console** tab

### **Step 3: Test Chat Widget**

1. Click chat widget button (bottom-right corner)
2. Type: **"What is ROS 2?"**
3. Press Enter

**Watch the console - Expected logs**:
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

**Watch the chat panel - Expected response**:
```
ROS 2 (Robot Operating System 2) is a next-generation robotics framework
designed for production robotics applications...

📚 Sources:
• Module1 - Chapter 1: ROS 2 Architecture (Confidence: 0.71)
• Module3 - Chapter 1: Isaac Sim Introduction (Confidence: 0.62)
```

---

## ❌ IF YOU STILL GET "couldn't find relevant information"

### **Diagnostic 1: Check What URL Frontend is Using**

**In browser console (F12)**:
```javascript
// Check current API URL
fetch('http://172.25.218.26:8000/health')
  .then(r => r.json())
  .then(d => console.log('WSL Backend:', d))
  .catch(e => console.error('Cannot reach WSL backend:', e))
```

If this **fails**, Windows can't reach WSL backend. Solutions:

1. **Add firewall rule** (see Test 1 above)
2. **OR run backend natively on Windows** (see below)

### **Diagnostic 2: Verify Frontend Built with Correct Config**

```bash
# Check if config file has WSL IP
grep -n "172.25.218.26" /mnt/e/phyai-humanoid-textbook/frontend/src/components/ChatWidget/config.ts
```

**Expected**: `20:  return 'http://172.25.218.26:8000';`

If it shows `localhost:8000`, the file wasn't updated. Run:
```bash
cd /mnt/e/phyai-humanoid-textbook/frontend
# Edit config.ts line 20 manually to use: http://172.25.218.26:8000
# Then rebuild:
rm -rf .docusaurus build
npm run build
npm run start
```

---

## 🔄 ALTERNATIVE: Run Backend on Windows (Avoid WSL Networking Issues)

If WSL networking is problematic, run backend directly in Windows:

### **Step 1: Stop WSL Backend**

**In WSL terminal**:
```bash
pkill -f "uvicorn app.main:app"
```

### **Step 2: Start Backend in Windows**

**Open NEW Windows PowerShell window**:
```powershell
cd E:\phyai-humanoid-textbook\backend\rag-chatbot

# Clear cache
Get-ChildItem -Path . -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force

# Install dependencies
pip install -r requirements.txt

# Start backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Wait for**:
```
[Backend] qdrant_collection_verified    points_count=913
[Backend] POST                 /api/v1/chat/stream
INFO:     Application startup complete.
```

### **Step 3: Update Frontend Config Back to localhost**

**Edit**: `E:\phyai-humanoid-textbook\frontend\src\components\ChatWidget\config.ts` line 20:

**Change FROM**:
```typescript
return 'http://172.25.218.26:8000';  // WSL backend IP
```

**Change TO**:
```typescript
return 'http://localhost:8000';  // Windows backend
```

### **Step 4: Rebuild Frontend**

```bash
cd /mnt/e/phyai-humanoid-textbook/frontend
rm -rf .docusaurus build
npm run build
npm run start
```

---

## ✅ SUCCESS CHECKLIST

After running commands, verify:

- [ ] Frontend builds successfully (no errors)
- [ ] Frontend server starts on `http://localhost:3000`
- [ ] Backend health endpoint responds: `curl http://172.25.218.26:8000/health`
- [ ] Browser opens `localhost:3000` with chat widget visible
- [ ] Chat query "What is ROS 2?" returns textbook content
- [ ] Citations appear: Module1 Chapter 1, Module3 Chapter 1
- [ ] No console errors (F12 → Console)
- [ ] Selected text feature works (highlight → "Ask about this")

---

## 🆘 STILL NOT WORKING?

**Check these**:

1. **WSL backend running?**
   ```bash
   curl http://localhost:8000/health  # From WSL
   ```

2. **Windows can reach WSL backend?**
   ```powershell
   curl http://172.25.218.26:8000/health  # From Windows
   ```

3. **Frontend built with new config?**
   ```bash
   grep "172.25.218.26" /mnt/e/phyai-humanoid-textbook/frontend/build/assets/*.js
   ```

4. **Browser cache cleared?**
   - Windows: `Ctrl + Shift + R`
   - Or: Clear browser cache manually

---

**You're almost there! Execute the commands above and test in browser.** 🚀
