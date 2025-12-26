# 🚀 Quick Start - Windows

## Option 1: One-Click Start (Recommended)

### PowerShell
```powershell
cd E:\phyai-humanoid-textbook\backend\rag-chatbot
.\start-server.ps1
```

### Command Prompt
```cmd
cd E:\phyai-humanoid-textbook\backend\rag-chatbot
start-server.bat
```

Wait for: **"Application startup complete"** (~10-15 seconds)

## Option 2: Manual Start

```powershell
# 1. Navigate to backend directory
cd E:\phyai-humanoid-textbook\backend\rag-chatbot

# 2. Install dependencies (first time only)
pip install -r requirements.txt

# 3. Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Verify It's Working

**Open a NEW terminal** (keep server running in first one):

```powershell
# Run test suite
.\test-backend.ps1
```

Expected output:
```
✓ PASS: Server is healthy
✓ PASS: Received response
✓ PASS: Received response with X tokens
✓ PASS: Response time: X ms

🎉 All tests passed! Backend is ready for demo.
```

## Manual Tests (Alternative)

### Health Check
```powershell
curl http://localhost:8000/health
```
Expected: `{"status":"healthy"}`

### Test Query
```powershell
curl -X POST "http://localhost:8000/api/v1/chat/api/v1/chat/stream" `
  -H "Content-Type: application/json" `
  -d '{\"session_id\": \"test\", \"question\": \"What is ROS 2?\"}'
```

Expected: Streaming response with tokens, citations, metadata

## Common Issues

### ❌ "ModuleNotFoundError: No module named 'openai'"

**Fix**: Install dependencies
```powershell
pip install -r requirements.txt
```

### ❌ "Port 8000 is already in use"

**Fix**: Kill old processes
```powershell
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
```

### ❌ Server starts but no response

**Fix**: Check `.env` file exists with:
- `OPENROUTER_API_KEY`
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `NEON_DATABASE_URL`

## Frontend Connection

After backend is verified:

1. **Start frontend** (new terminal):
   ```powershell
   cd E:\phyai-humanoid-textbook\frontend\chatbot-widget
   npm run dev
   ```

2. **Open browser**: `http://localhost:3000`

3. **Test queries**:
   - "What is Physical AI?"
   - "What is ROS 2?"
   - "Explain physics simulation"

4. **Test selected text**:
   - Highlight text → Click "Ask about this"

## What's Working

✅ OpenAI Agents SDK integration
✅ LiteLLM with OpenRouter (free mistralai/devstral-2512 model)
✅ Streaming responses (word-by-word)
✅ RAG pipeline with Qdrant vector search
✅ Accurate grounded responses with citations
✅ 913 textbook chunks loaded
✅ Local embeddings (all-MiniLM-L6-v2)

## Performance

- **Startup**: 10-15 seconds
- **Query time**: 2.8-4.1 seconds
  - Retrieval: ~1s
  - Generation: ~2-3s
- **Token rate**: Smooth streaming

## Demo Checklist

Before presenting:

- [ ] Backend starts without errors
- [ ] All 4 tests pass
- [ ] Frontend connects successfully
- [ ] Test query returns accurate answer
- [ ] Selected text feature works
- [ ] No console errors

## Need Help?

1. Check `WINDOWS_SETUP.md` for detailed troubleshooting
2. View server logs for specific errors
3. Verify all environment variables are set

---

**You're ready! 🎉**

Run `.\start-server.ps1` → Wait for startup → Run `.\test-backend.ps1` → Start frontend → Demo!
