# Connecting Windows Frontend to WSL Backend

## Problem
Windows `localhost` and WSL `localhost` are on different networks. When your Windows frontend tries to connect to `http://localhost:8000`, it's NOT reaching the WSL backend.

## Solution: Use WSL IP Address

### Step 1: Get WSL IP Address (Run in WSL/Ubuntu)

```bash
hostname -I | awk '{print $1}'
```

**Example output**: `172.18.240.123`

### Step 2: Update Frontend Config

**Option A: Set environment variable (Windows PowerShell)**

```powershell
# Navigate to frontend
cd E:\phyai-humanoid-textbook\frontend

# Set the WSL IP (replace with YOUR WSL IP from Step 1)
$env:VITE_API_URL = "http://172.18.240.123:8000"

# Start frontend
npm run dev
```

**Option B: Update config.ts (permanent fix)**

Edit `frontend/src/components/ChatWidget/config.ts` line 20:

```typescript
function getApiUrl(): string {
  // Check for browser runtime config
  if (typeof window !== 'undefined' && (window as any).CHAT_API_URL) {
    return (window as any).CHAT_API_URL;
  }

  // WSL backend IP (replace with your WSL IP)
  return 'http://172.18.240.123:8000';  // ← CHANGE THIS
}
```

### Step 3: Verify Backend is Accessible

**From Windows PowerShell**, test the WSL backend:

```powershell
# Replace with YOUR WSL IP
curl http://172.18.240.123:8000/health
```

**Expected**: `{"status":"healthy",...}`

### Step 4: Test Chat Endpoint

```powershell
curl -X POST "http://172.18.240.123:8000/api/v1/chat/stream" `
  -H "Content-Type: application/json" `
  -d '{\"session_id\": \"test-wsl\", \"question\": \"What is ROS 2?\"}'
```

**Expected**: Streaming response with textbook content

---

## Alternative: Run Backend Natively on Windows

If you prefer to avoid WSL networking, run the backend directly in Windows PowerShell:

```powershell
# Navigate to backend
cd E:\phyai-humanoid-textbook\backend\rag-chatbot

# Activate virtual environment (if using venv)
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start backend on Windows
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Then frontend can use `http://localhost:8000` normally.

---

## Quick Test: Which Backend Are You Connected To?

**From Windows browser console (F12)**:

```javascript
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(d => console.log('Connected to:', d))
```

If this returns `{"status":"healthy"}`, you're connected to a backend. But which one?

**Check if it's the WSL backend**:
```javascript
fetch('http://172.18.240.123:8000/health')  // Use YOUR WSL IP
  .then(r => r.json())
  .then(d => console.log('WSL backend:', d))
```

---

## Summary

- ✅ WSL backend is running and WORKING (tested successfully)
- ✅ Qdrant has 913 chunks loaded
- ✅ Retrieval returns proper citations
- ❌ Windows frontend can't reach WSL backend via `localhost:8000`

**Solution**: Use WSL IP address in frontend config or run backend natively on Windows.
