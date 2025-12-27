# Start Commands - RAG Chatbot

**Post-Cleanup Verified Working** ✅

---

## Prerequisites

Ensure you have:
- Python 3.11+ installed
- Node.js 18+ installed (for frontend)
- PostgreSQL running (or configured in .env)
- `.env` file with required credentials

---

## Backend Startup

### Option 1: Standard Development Server (Recommended)

```bash
cd /mnt/e/phyai-humanoid-textbook/backend/rag-chatbot
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Features:**
- Auto-reload on code changes
- Runs on http://0.0.0.0:8000
- Accessible from localhost and WSL IP

**Expected Output:**
```
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
[Backend] Loading routers...
[Backend] ✓ Sessions router registered
[Backend] ✓ Chat router registered: /api/v1/chat
...
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Option 2: Production-Style (No Auto-Reload)

```bash
cd /mnt/e/phyai-humanoid-textbook/backend/rag-chatbot
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Option 3: Background Process

```bash
cd /mnt/e/phyai-humanoid-textbook/backend/rag-chatbot
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
echo "Backend started in background. Check logs: tail -f backend.log"
```

**To stop:**
```bash
pkill -f "uvicorn app.main:app"
```

---

## Frontend Startup

### Standard Development Server

```bash
cd /mnt/e/phyai-humanoid-textbook/frontend
npm run dev
```

**Expected Output:**
```
VITE v4.x.x  ready in XXX ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

**Access at:** http://localhost:3000

### Production Build

```bash
cd /mnt/e/phyai-humanoid-textbook/frontend
npm run build
npm run preview
```

---

## Quick Verification

### 1. Backend Health Check

```bash
curl http://localhost:8000/health
```

**Expected:**
```json
{
  "status": "healthy",
  "dependencies": {
    "postgres": "up",
    "qdrant": "up",
    "openai": "assumed_up"
  },
  "version": "1.0.0"
}
```

### 2. Test Chat Request

```bash
curl -X POST "http://localhost:8000/api/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "question": "What is ROS 2?"}'
```

**Expected:** Streaming SSE response with answer and citations

### 3. Open Frontend

Open browser to: http://localhost:3000

**Expected:** Chat widget loads, you can ask questions

---

## Common Issues & Solutions

### Backend Won't Start

**Issue:** `ModuleNotFoundError` or import errors

**Solution:**
```bash
cd /mnt/e/phyai-humanoid-textbook/backend/rag-chatbot
pip install -r requirements.txt
```

### Port Already in Use

**Issue:** `Address already in use: 0.0.0.0:8000`

**Solution:**
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9
# OR
pkill -f "uvicorn"
```

### Database Connection Failed

**Issue:** Backend starts but health check shows `postgres: down`

**Solution:** Check `.env` file has correct `DATABASE_URL`

### Frontend Can't Reach Backend

**Issue:** Frontend shows connection errors

**Solution:** Check `frontend/src/components/ChatWidget/config.ts`:
```typescript
// Should point to backend (adjust if needed)
return 'http://172.25.218.26:8000';  // WSL IP
// OR
return 'http://localhost:8000';      // Same machine
```

---

## Environment Variables Required

Create `.env` in `backend/rag-chatbot/`:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname

# Qdrant
QDRANT_URL=https://xxx.gcp.cloud.qdrant.io:6333
QDRANT_API_KEY=your-key-here
QDRANT_COLLECTION_NAME=textbook_chunks

# OpenRouter LLM
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=mistralai/devstral-2512:free

# CORS (optional, defaults to localhost:3000)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## API Documentation

Once backend is running, access:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Metrics:** http://localhost:8000/metrics

---

## Startup Checklist

- [ ] Backend `.env` file configured
- [ ] PostgreSQL accessible
- [ ] Qdrant collection created (913 vectors)
- [ ] Backend starts without errors
- [ ] Health check returns "healthy"
- [ ] Frontend starts without errors
- [ ] Can send chat message and get response

---

## Full Stack Startup (Both at Once)

### Terminal 1 - Backend
```bash
cd /mnt/e/phyai-humanoid-textbook/backend/rag-chatbot
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2 - Frontend
```bash
cd /mnt/e/phyai-humanoid-textbook/frontend
npm run dev
```

**Then:** Open http://localhost:3000 in browser

---

## Success Indicators

✅ Backend logs show:
```
[info] application_started - environment=production
[info] database_connected
[info] local_embedding_model_loaded - embedding_dim=384
[info] qdrant_collection_verified - points_count=913
[info] agents_sdk_configured
```

✅ Frontend loads chat widget

✅ Sending "What is ROS 2?" returns detailed answer with citations

✅ Health endpoint returns all dependencies "up"

---

**Everything is working correctly after cleanup! 🎉**
