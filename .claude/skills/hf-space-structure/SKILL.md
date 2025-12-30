# hf-space-structure

Create proper file structure for Hugging Face Spaces deployment.

## Purpose
Organize FastAPI application files according to HF Spaces requirements and best practices.

## Required File Structure
```
backend/
├── Dockerfile                # Required for Docker SDK
├── requirements.txt          # Python dependencies
├── README.md                 # Space documentation
├── .env.example              # Environment variables template
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI app entry point
│   ├── config.py             # Configuration management
│   ├── database.py           # Database connections
│   ├── models.py             # Pydantic models
│   └── routers/
│       ├── __init__.py
│       └── chat.py           # RAG chatbot endpoints
```

## Key Files Content

### main.py
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import chat

app = FastAPI(
    title="PhyAI RAG Chatbot API",
    description="Retrieval-Augmented Generation chatbot for PhyAI Humanoid Textbook",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

@app.get("/")
def read_root():
    return {
        "status": "API is running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "PhyAI RAG API"}
```

### config.py
```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: str
    
    # Database
    NEON_DATABASE_URL: str
    
    # Vector Database
    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION_NAME: str = "book_content"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### routers/chat.py
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    context: str = None

class ChatResponse(BaseModel):
    response: str
    sources: list = []

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # TODO: Implement RAG logic
    return ChatResponse(
        response="This is a placeholder response",
        sources=[]
    )
```

## HF Spaces README.md Template
```markdown
---
title: PhyAI RAG Chatbot API
emoji: 🤖
colorFrom: blue
colorTo: cyan
sdk: docker
pinned: false
---

# PhyAI RAG Chatbot API

Retrieval-Augmented Generation chatbot backend for PhyAI Humanoid Textbook.

## Features
- OpenAI-powered responses
- Vector search with Qdrant
- Chat history with Neon Postgres
- CORS-enabled for Vercel frontend

## API Endpoints
- `GET /` - API status
- `GET /health` - Health check
- `POST /api/chat` - Chat endpoint
- `GET /docs` - Interactive API docs

## Environment Variables
Set these in Space settings:
- `OPENAI_API_KEY`
- `NEON_DATABASE_URL`
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `CORS_ORIGINS`
```

## Deployment Checklist
- [ ] Dockerfile in root directory
- [ ] requirements.txt complete
- [ ] Port 7860 configured
- [ ] Environment variables documented
- [ ] CORS properly configured
- [ ] Health check endpoint working
- [ ] README.md with setup instructions

## Deployment Timing & Monitoring

### Expected Build Duration
- **Initial Build**: 8-10 minutes (includes dependency installation)
- **Rebuild After Code Change**: 8-10 minutes (full rebuild)
- **Cold Start**: 30-60 seconds (after being inactive)

### Build Progress Monitoring
Monitor HF Spaces Logs tab for these critical stages:

**Stage 1: Image Build (0-5 min)**
```bash
✓ "Step 1/10 : FROM python:3.11-slim"
✓ "Step 5/10 : RUN pip install -r requirements.txt"
✓ "Successfully built [image-id]"
```

**Stage 2: Dependency Installation (5-8 min)**
```bash
✓ "Collecting fastapi==0.115.0"
✓ "Collecting sentence-transformers==3.0.1"
✓ "Successfully installed [packages]"
```

**Stage 3: Application Startup (8-10 min)**
```bash
✓ "INFO:     Started server process"
✓ "INFO:     Waiting for application startup"
✓ "INFO:     Application startup complete"
✓ "INFO:     Uvicorn running on http://0.0.0.0:7860"
```

### Critical Startup Logs to Watch

**SUCCESS INDICATORS:**
```bash
✓ "Database connection pool established"
✓ "Qdrant collection 'textbook_chunks' found: 913 points"
✓ "Embedding model loaded: all-MiniLM-L6-v2"
✓ "CORS origins configured: ['http://localhost:3000', 'https://...vercel.app']"
✓ "Application startup complete"
```

**FAILURE INDICATORS (require immediate fix):**
```bash
✗ "ImportError: cannot import name 'cached_download'"
   → Fix: Update requirements.txt with sentence-transformers==3.0.1, huggingface-hub>=0.20.0

✗ "ModuleNotFoundError: No module named 'asyncpg'"
   → Fix: Add asyncpg==0.29.0 to requirements.txt

✗ "asyncpg.exceptions.InvalidPasswordError"
   → Fix: Check NEON_DATABASE_URL includes ?sslmode=require

✗ "QdrantException: timed out"
   → Fix: Verify QDRANT_URL format (must include https:// and :6333)

✗ "ConnectionRefusedError: [Errno 111] Connection refused"
   → Fix: Verify external service URLs and API keys in HF Space settings

✗ "CORS policy: No 'Access-Control-Allow-Origin'"
   → Fix: Add Vercel domain to CORS_ORIGINS environment variable
```

## Health Check Requirements

### Health Endpoint Implementation
```python
# In app/main.py
from fastapi import FastAPI
from app.clients.db_client import get_db_pool
from app.clients.qdrant_client import get_qdrant_client

@app.get("/health")
async def health_check():
    """
    Comprehensive health check for HF Spaces monitoring
    Returns status of all critical dependencies
    """
    health_status = {
        "status": "healthy",
        "service": "PhyAI RAG Chatbot API",
        "version": "1.0.0",
        "dependencies": {}
    }

    # Check database connection
    try:
        pool = get_db_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        health_status["dependencies"]["database"] = "connected"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["dependencies"]["database"] = f"error: {str(e)}"

    # Check Qdrant connection
    try:
        qdrant = get_qdrant_client()
        collections = qdrant.get_collections()
        health_status["dependencies"]["qdrant"] = "connected"
        health_status["dependencies"]["qdrant_collections"] = len(collections.collections)
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["dependencies"]["qdrant"] = f"error: {str(e)}"

    # Check embedding model loaded
    try:
        from app.clients.local_embedding_client import embedding_model
        health_status["dependencies"]["embeddings"] = "loaded"
        health_status["dependencies"]["embedding_dimension"] = 384
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["dependencies"]["embeddings"] = f"error: {str(e)}"

    return health_status
```

### Expected Health Response Format
**Healthy State:**
```json
{
  "status": "healthy",
  "service": "PhyAI RAG Chatbot API",
  "version": "1.0.0",
  "dependencies": {
    "database": "connected",
    "qdrant": "connected",
    "qdrant_collections": 1,
    "embeddings": "loaded",
    "embedding_dimension": 384
  }
}
```

**Degraded State:**
```json
{
  "status": "degraded",
  "service": "PhyAI RAG Chatbot API",
  "version": "1.0.0",
  "dependencies": {
    "database": "connected",
    "qdrant": "error: connection timeout",
    "embeddings": "loaded"
  }
}
```

### Testing Health Endpoint
```bash
# Test immediately after deployment (wait 8-10 min first)
curl https://your-username-your-space-name.hf.space/health

# Expected: HTTP 200 with JSON response showing all dependencies "connected"

# If status is "degraded", check HF Spaces Logs for error details
```

## Post-Deployment Verification Commands

### 1. Wait for Build Completion
```bash
# CRITICAL: Wait 8-10 minutes after git push
# Check HF Spaces Logs tab for "Application startup complete"
```

### 2. Test Health Endpoint
```bash
curl https://your-username-your-space-name.hf.space/health
# Expected: {"status": "healthy", "dependencies": {...}}
```

### 3. Test Sessions Endpoint
```bash
curl -X POST https://your-username-your-space-name.hf.space/api/v1/sessions \
  -H "Content-Type: application/json"
# Expected: {"session_id": "uuid-here", ...}
```

### 4. Test Chat Stream Endpoint
```bash
curl -X POST https://your-username-your-space-name.hf.space/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-123", "question": "What is ROS 2?"}' \
  -N
# Expected: SSE stream with data: {"type": "token", ...}
```

### 5. Verify CORS Headers
```bash
curl -X OPTIONS https://your-username-your-space-name.hf.space/api/v1/chat \
  -H "Origin: https://your-site.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -v
# Expected: access-control-allow-origin header in response
```

## Output
Properly structured, production-ready FastAPI application for HF Spaces with comprehensive health monitoring and deployment verification