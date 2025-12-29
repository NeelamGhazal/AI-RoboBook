# Quickstart: RAG Chatbot with OpenAI Agents SDK + Gemini

**Feature**: 001-openai-agents-migration
**Phase**: Phase 1 - Quickstart
**Date**: 2025-12-25
**Audience**: New developers joining the project post-migration

## Overview

This guide walks you through setting up and running the RAG chatbot backend after the OpenAI Agents SDK migration. The chatbot uses the Agents SDK with Google Gemini 1.5 Flash (free tier) as the underlying LLM.

**Tech Stack**:
- OpenAI Agents SDK (orchestration)
- Google Gemini 1.5 Flash (LLM - free tier)
- FastAPI (backend API)
- Qdrant Cloud (vector search)
- Neon Serverless Postgres (session storage)
- Sentence-Transformers (local embeddings)

---

## Prerequisites

- **Python**: 3.11+ (check with `python --version`)
- **Git**: For cloning the repository
- **API Keys**:
  - Google Gemini API key ([Get one free](https://aistudio.google.com/apikey))
  - Qdrant Cloud API key ([Free tier](https://cloud.qdrant.io/))
  - Neon Postgres connection string ([Free tier](https://neon.tech/))

---

## Step 1: Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd phyai-humanoid-textbook/backend/rag-chatbot

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Expected dependencies** (from `requirements.txt`):
```
fastapi==0.115.0
uvicorn[standard]==0.30.6
openai==1.51.0
openai-agents>=0.1.0  # ← NEW (Agents SDK)
google-generativeai==0.8.3
qdrant-client==1.16.2
asyncpg==0.29.0
sentence-transformers==2.2.2
pydantic==2.9.2
structlog==24.4.0
```

---

## Step 2: Configure Environment

Create `.env` file in `backend/rag-chatbot/`:

```bash
# Copy example
cp .env.example .env

# Edit with your API keys
nano .env  # or use your preferred editor
```

**Required environment variables**:

```env
# ========== Google Gemini (Free Tier) ==========
GOOGLE_API_KEY=your_gemini_api_key_here

# Model names (default: gemini-1.5-flash)
GEMINI_MODEL=gemini-1.5-flash
GEMINI_EMBEDDING_MODEL=models/embedding-001

# ========== Qdrant Cloud (Free Tier) ==========
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION_NAME=textbook_chunks

# ========== Neon Serverless Postgres ==========
NEON_DATABASE_URL=postgresql://user:password@host/dbname

# ========== API Configuration ==========
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,https://your-frontend-url.com

# ========== Logging ==========
LOG_LEVEL=INFO
LOG_JSON=false
```

**Important**:
- `GOOGLE_API_KEY` is used by both Gemini API AND the Agents SDK (via OpenAI-compatible endpoint)
- No `OPENAI_API_KEY` needed (zero OpenAI costs!)

---

## Step 3: Verify Database and Vector Store

### 3.1 Check Neon Postgres Connection

```bash
# Test database connection
python -c "import asyncio; from app.clients.db_client import db_client; asyncio.run(db_client.connect()); print('DB connected!')"
```

**Expected output**: `DB connected!`

### 3.2 Check Qdrant Collection

```bash
# Test Qdrant connection
python -c "import asyncio; from app.clients.qdrant_client import qdrant_client; asyncio.run(qdrant_client.initialize()); print(f'Collection exists: {await qdrant_client.collection_exists()}')"
```

**Expected output**: `Collection exists: True`

---

## Step 4: Run the Backend

```bash
# Development mode (auto-reload)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Expected startup logs**:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     application_starting
INFO:     database_connected
INFO:     local_embedding_client_ready
INFO:     agents_sdk_configured model=gemini-1.5-flash base_url=https://generativelanguage.googleapis.com/v1beta/openai/
INFO:     qdrant_client_ready
INFO:     application_started environment=production
[Backend] ✓ Sessions router registered
[Backend] ✓ RAG chat router registered: /api/v1/chat
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Key indicator**: Look for `agents_sdk_configured` log entry. This confirms the Agents SDK is using Gemini via the OpenAI-compatible endpoint.

---

## Step 5: Test the API

### 5.1 Health Check

```bash
curl http://localhost:8000/health
```

**Expected response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-25T12:00:00Z",
  "dependencies": {
    "postgres": "up",
    "qdrant": "up",
    "openai": "assumed_up"
  },
  "version": "1.0.0"
}
```

### 5.2 Create Session

```bash
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json"
```

**Expected response**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-12-25T12:00:00Z"
}
```

### 5.3 Test Chat (Non-Streaming)

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is ROS 2?",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

**Expected response**:
```json
{
  "response": "ROS 2 (Robot Operating System 2) is...",
  "citations": [
    {
      "source": "Chapter 1",
      "chapter": "Introduction to ROS 2",
      "section": "1.1 Overview",
      "page": 15,
      "text": "ROS 2 is the next generation...",
      "confidence_score": 0.92
    }
  ],
  "metadata": {
    "total_time_ms": 1840,
    "retrieval_time_ms": 320,
    "generation_time_ms": 1520,
    "chunks_retrieved": 5,
    "token_count": 124
  }
}
```

### 5.4 Test Streaming

```bash
curl -N -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is ROS 2?",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

**Expected output** (Server-Sent Events):
```
data: {"type":"token","content":"ROS"}

data: {"type":"token","content":" 2"}

data: {"type":"token","content":" is"}

...

data: {"type":"citations","citations":[{"source":"Chapter 1",...}]}

data: {"type":"metadata","metadata":{"total_time_ms":1840,...}}

data: {"type":"done"}
```

---

## Step 6: Verify Agents SDK Integration

### 6.1 Check Logs for Agents SDK Usage

Look for these log entries in the uvicorn console:

```
INFO:     agents_sdk_configured model=gemini-1.5-flash base_url=https://generativelanguage.googleapis.com/v1beta/openai/ agent_name=TextbookRAGAgent
INFO:     agent_request_started question_length=13 context_length=450 stream=True
INFO:     agent_response_complete response_length=124 estimated_tokens=31 duration_ms=1520
```

**Key indicator**: `agents_sdk_configured` confirms the SDK is initialized with Gemini.

### 6.2 Inspect Code

Verify the migration in `app/services/llm.py`:

```bash
# Should see Agents SDK imports
grep -n "from agents import" app/services/llm.py

# Should NOT see direct gemini_client usage
grep -n "gemini_client.generate" app/services/llm.py  # Should return empty
```

**Expected**:
- `from agents import Agent, Runner` present
- `gemini_client.generate_chat_completion` removed

### 6.3 Verify OpenAI Client Configuration

Check `app/main.py` lifespan:

```bash
grep -A 10 "set_default_openai_client" app/main.py
```

**Expected**:
```python
from openai import AsyncOpenAI
from agents import set_default_openai_client

gemini_client = AsyncOpenAI(
    api_key=settings.GOOGLE_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
set_default_openai_client(gemini_client)
```

---

## Step 7: Run Tests

```bash
# Run unit tests
pytest tests/unit/ -v

# Run integration tests (requires valid API keys)
pytest tests/integration/ -v -m integration

# Run full test suite
pytest -v
```

**Key tests to verify**:
- `test_agents_adapter.py` - Agents SDK configuration
- `test_rag_with_agents.py` - Full RAG pipeline with Agents SDK
- `test_streaming_contract.py` - Frontend compatibility

---

## Troubleshooting

### Issue: "agents module not found"

**Cause**: `openai-agents` package not installed

**Fix**:
```bash
pip install openai-agents>=0.1.0
```

### Issue: "RateLimitError: Quota exceeded"

**Cause**: Gemini free tier limits exceeded (15 RPM, 1500 RPD)

**Fix**:
- Wait 1 minute if you hit per-minute limit
- Wait 24 hours if you hit daily limit
- For production, upgrade to Gemini paid tier

### Issue: "Streaming responses not working"

**Cause**: Frontend expecting old event format

**Check**: Event mapping in `app/services/llm.py:generate_response_stream()`
```python
# Must map Agents SDK events to frontend format
if event.type == "content_delta":
    yield {"type": "token", "content": event.content}
```

### Issue: "agents_sdk_configured log missing"

**Cause**: `set_default_openai_client()` not called during startup

**Fix**: Verify `app/main.py` lifespan includes client setup before any Agent usage

---

## Development Workflow

### Making Changes

1. **Modify code** in `app/services/llm.py` or other files
2. **Test locally**: Uvicorn auto-reloads with `--reload` flag
3. **Run tests**: `pytest tests/`
4. **Check logs**: Look for `agent_request_started`, `agent_response_complete`
5. **Verify metrics**: `curl http://localhost:8000/metrics` (Prometheus)

### Debugging Agent Behavior

Enable debug logging in `.env`:
```env
LOG_LEVEL=DEBUG
```

Restart server to see detailed Agents SDK execution logs:
```
DEBUG:    agent_input input="**Textbook Excerpts:** ..."
DEBUG:    content_delta content="The"
DEBUG:    content_delta content=" answer"
DEBUG:    agent_response_complete response_length=124
```

---

## Next Steps

After verifying the setup works:

1. **Deploy to Railway**: Push to branch `001-openai-agents-migration`
2. **Test with Frontend**: Connect frontend chatbot widget to deployed backend
3. **Monitor Performance**: Check `REQUEST_DURATION` metrics (<3 sec requirement)
4. **Hackathon Demo**: Verify judges can see Agents SDK imports in code (`app/services/llm.py`)

---

## Key Files Reference

| File | Purpose | Post-Migration Changes |
|------|---------|------------------------|
| `app/main.py` | FastAPI app + lifespan | ✅ Added `set_default_openai_client()` setup |
| `app/services/llm.py` | LLM service layer | ✅ Refactored to use `Runner.run()` / `Runner.run_stream()` |
| `app/clients/gemini_client.py` | Direct Gemini client | ⚠️ DEPRECATED (kept for reference, not imported) |
| `app/api/v1/chat.py` | Real RAG endpoint | ✅ ACTIVATED (was inactive, now registered in main.py) |
| `app/api/v1/chat_minimal.py` | Mock endpoint | ⚠️ DEACTIVATED (was active, now unused) |
| `requirements.txt` | Python dependencies | ✅ Added `openai-agents>=0.1.0` |
| `.env` | Environment variables | ✅ No new vars needed (reuses GOOGLE_API_KEY) |

---

## Support

- **Documentation**: See `specs/001-openai-agents-migration/` directory
- **Agents SDK Docs**: https://openai.github.io/openai-agents-python/
- **Gemini OpenAI Compatibility**: https://ai.google.dev/gemini-api/docs/openai
- **Issues**: Create GitHub issue with logs and error messages

---

**Migration Status**: ✅ Complete
**Next Command**: `/sp.tasks` to generate implementation task breakdown
