# Windows Local Setup Guide

## Prerequisites

Make sure you have:
- Python 3.11 or higher installed
- Git installed (if cloning from repo)
- `.env` file with all required environment variables

## Step-by-Step Setup

### 1. Open PowerShell or Command Prompt

Navigate to the backend directory:
```powershell
cd E:\phyai-humanoid-textbook\backend\rag-chatbot
```

### 2. Create Virtual Environment (Recommended)

```powershell
# Create virtual environment
python -m venv venv

# Activate it (PowerShell)
.\venv\Scripts\Activate.ps1

# OR if using Command Prompt
.\venv\Scripts\activate.bat
```

If you get an execution policy error in PowerShell:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Upgrade pip

```powershell
python -m pip install --upgrade pip
```

### 4. Install All Dependencies

```powershell
pip install -r requirements.txt
```

This will install:
- ✅ `openai>=2.9.0` (OpenAI Python SDK)
- ✅ `openai-agents>=0.6.0` (OpenAI Agents SDK)
- ✅ `litellm==1.80.11` (LiteLLM for OpenRouter)
- ✅ `fastapi`, `uvicorn`, and all other dependencies

**Expected installation time**: 2-5 minutes depending on internet speed

### 5. Verify Installation

```powershell
# Check if openai is installed
python -c "import openai; print(f'OpenAI version: {openai.__version__}')"

# Check if litellm is installed
python -c "import litellm; print('LiteLLM installed successfully')"

# Check if agents SDK is installed
python -c "from agents import Agent, Runner; print('Agents SDK installed successfully')"
```

### 6. Kill Any Old Server Processes

**PowerShell**:
```powershell
# Kill all Python processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# OR kill specific uvicorn processes
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Stop-Process -Force
```

**Command Prompt**:
```cmd
taskkill /F /IM python.exe /T
```

### 7. Start the Backend Server

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
[Backend] Loading routers...
[Backend] ✓ Sessions router registered
[Backend] ✓ Chat router registered: /api/v1/chat
...
INFO:     Application startup complete.
```

**⚠️ IMPORTANT**: Wait for the message "Application startup complete" before testing!

The startup sequence includes:
1. Database connection (2-3 seconds)
2. Loading local embedding model (all-MiniLM-L6-v2) - **5-8 seconds**
3. Connecting to Qdrant vector database (2-3 seconds)
4. Verifying 913 chunks loaded

**Total startup time**: ~10-15 seconds

## Verification Tests

### 1. Health Check

Open a **new PowerShell/Command Prompt window** (keep server running in the first one):

```powershell
curl http://localhost:8000/health
```

**Expected response**:
```json
{"status":"healthy"}
```

### 2. Test RAG Query

```powershell
curl -X POST "http://localhost:8000/api/v1/chat/api/v1/chat/stream" `
  -H "Content-Type: application/json" `
  -d '{\"session_id\": \"test\", \"question\": \"What is ROS 2?\"}'
```

**Expected response** (streaming format):
```
data: {"type": "token", "content": "ROS 2 (Robot Operating System 2) is..."}
data: {"type": "citations", "citations": [...]}
data: {"type": "metadata", "metadata": {...}}
data: {"type": "done"}
```

### 3. Test Another Query

```powershell
curl -X POST "http://localhost:8000/api/v1/chat/api/v1/chat/stream" `
  -H "Content-Type: application/json" `
  -d '{\"session_id\": \"test2\", \"question\": \"Explain physics simulation\"}'
```

## Frontend Testing Flow

Once the backend is verified working:

### 1. Start Frontend (Separate Terminal)

```powershell
# Navigate to frontend directory
cd E:\phyai-humanoid-textbook\frontend\chatbot-widget

# Install dependencies (if not done already)
npm install

# Start development server
npm run dev
```

### 2. Open Browser

Navigate to: `http://localhost:3000` (or whatever port the frontend uses)

### 3. Test Normal Queries

Type in the chat:
- "What is Physical AI?"
- "What is ROS 2?"
- "Explain physics simulation for robotics"

**Expected behavior**:
- ✅ Responses stream in smoothly (word by word)
- ✅ Answers are accurate and grounded in textbook
- ✅ Citations appear at the bottom
- ✅ No errors in browser console

### 4. Test Selected Text Feature

1. Navigate to a textbook page (if available in your frontend)
2. **Highlight a paragraph** with your mouse
3. Click **"Ask about this"** button
4. The chatbot should:
   - ✅ Receive the selected text as context
   - ✅ Provide an explanation grounded in that specific text
   - ✅ Show relevant citations

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'openai'"

**Solution**:
```powershell
pip install openai litellm openai-agents
```

### Issue: "ModuleNotFoundError: No module named 'litellm'"

**Solution**:
```powershell
pip install litellm==1.80.11
```

### Issue: "Port 8000 is already in use"

**Solution**:
```powershell
# Kill all Python processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# OR use a different port
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Issue: Server starts but crashes immediately

**Check**:
1. `.env` file exists with all required variables:
   ```
   OPENROUTER_API_KEY="sk-or-v1-..."
   QDRANT_URL="https://..."
   QDRANT_API_KEY="..."
   NEON_DATABASE_URL="postgresql://..."
   ```

2. View server logs for specific error messages

### Issue: "Embedding model download taking too long"

**First time only**: The `all-MiniLM-L6-v2` model (~80MB) will download from Hugging Face.
- Expected download time: 1-3 minutes on good internet
- Model is cached locally after first download

### Issue: Responses are empty (token_count: 0)

**This should NOT happen** - we fixed this issue!

If it does:
1. Check server logs for errors
2. Verify `litellm==1.80.11` is installed
3. Confirm `.env` has `OPENROUTER_API_KEY`
4. Restart the server

## Performance Expectations

- **Startup time**: 10-15 seconds
- **Query response time**: 2.8-4.1 seconds
  - Retrieval: ~1 second
  - Generation: ~2-3 seconds
- **Streaming**: Should see tokens appearing smoothly, not all at once
- **Accuracy**: Responses grounded in textbook content

## Demo Checklist

Before the hackathon demo, verify:

- [ ] Backend starts without errors
- [ ] Health endpoint returns `{"status":"healthy"}`
- [ ] Test query "What is ROS 2?" returns accurate answer
- [ ] Streaming works (tokens appear progressively)
- [ ] Citations show up correctly
- [ ] Frontend connects to backend successfully
- [ ] Selected text feature works
- [ ] No errors in browser console or server logs

## Quick Command Reference

**Start backend**:
```powershell
cd E:\phyai-humanoid-textbook\backend\rag-chatbot
.\venv\Scripts\Activate.ps1  # If using venv
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Test health**:
```powershell
curl http://localhost:8000/health
```

**Test query**:
```powershell
curl -X POST "http://localhost:8000/api/v1/chat/api/v1/chat/stream" `
  -H "Content-Type: application/json" `
  -d '{\"session_id\": \"demo\", \"question\": \"What is ROS 2?\"}'
```

**Stop server**: `Ctrl+C` in the terminal running uvicorn

---

**You're ready for the demo! 🚀**

If you encounter any issues, check the server logs for specific error messages and refer to the troubleshooting section above.
