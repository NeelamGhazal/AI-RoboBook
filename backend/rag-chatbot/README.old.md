# RAG Chatbot Backend

**Production-Ready Retrieval-Augmented Generation API for PhyAI Humanoid Textbook**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![OpenAI Agents SDK](https://img.shields.io/badge/OpenAI_Agents-0.6.0-412991?logo=openai&logoColor=white)](https://github.com/openai/agents-sdk)
[![Qdrant](https://img.shields.io/badge/Qdrant_Cloud-1.16-DC244C?logo=qdrant&logoColor=white)](https://qdrant.tech/)
[![Neon](https://img.shields.io/badge/Neon_Postgres-Serverless-00E699?logo=postgresql&logoColor=white)](https://neon.tech/)

---

## Overview

FastAPI-based RAG chatbot backend providing intelligent Q&A with streaming responses, citations, and context-aware explanations. Built with OpenAI Agents SDK, Neon Serverless PostgreSQL, and Qdrant Cloud Free Tier.

### Key Features

✅ **Streaming Responses** - Server-Sent Events (SSE) for progressive text display
✅ **Selected Text Q&A** - Context-aware answers based on user-highlighted text
✅ **Citation Support** - Source references with confidence scores
✅ **Session Persistence** - Conversation history stored in Neon PostgreSQL
✅ **Free Embeddings** - Local sentence-transformers (zero API costs)
✅ **Free LLM Tier** - OpenRouter with mistralai/devstral-2512:free
✅ **Production Ready** - Structured logging, Prometheus metrics, async architecture

---

## Technology Stack

### Core Framework
- **FastAPI 0.115** - Async Python web framework
- **Uvicorn** - ASGI server with auto-reload

### AI & RAG Pipeline
- **OpenAI Agents SDK 0.6.0** - LLM orchestration and streaming
- **LiteLLM 1.80.11** - OpenRouter integration proxy
- **Sentence-Transformers** - Local embeddings (all-MiniLM-L6-v2, 384 dimensions)
- **Qdrant Cloud 1.16** - Vector database (913 textbook chunks)

### Data Storage
- **Neon Serverless PostgreSQL** - Session and message persistence
- **asyncpg** - Async PostgreSQL driver with connection pooling

### Observability
- **Structlog** - Structured JSON logging
- **Prometheus** - Metrics and monitoring

---

## Architecture

### RAG Data Flow

```
User Question
    ↓
Local Embeddings (sentence-transformers, FREE)
    ↓
Qdrant Vector Search (913 textbook chunks)
    ↓
Context Building (retrieval + conversation history)
    ↓
OpenAI Agents SDK → LiteLLM → OpenRouter
    ↓
Streaming Response (Server-Sent Events)
    ↓
Citations + Metadata
```

### Directory Structure

```
backend/rag-chatbot/
├── app/
│   ├── main.py                    # FastAPI application
│   ├── config.py                  # Pydantic settings
│   ├── api/v1/
│   │   ├── chat.py               # Chat streaming endpoint
│   │   └── sessions.py           # Session management
│   ├── clients/
│   │   ├── db_client.py          # Neon PostgreSQL client
│   │   ├── local_embedding_client.py  # Sentence-transformers
│   │   └── qdrant_client.py      # Qdrant Cloud client
│   ├── services/
│   │   ├── rag.py                # RAG pipeline orchestration
│   │   ├── vector_search.py      # Embedding + retrieval
│   │   ├── llm.py                # OpenAI Agents SDK
│   │   └── citation_builder.py  # Citation extraction
│   ├── db/crud.py                # Database operations
│   ├── models/                   # Pydantic + SQLAlchemy models
│   └── utils/                    # Logging + Metrics
│
├── scripts/
│   ├── ingest_book.py            # Textbook data ingestion
│   └── init_qdrant.py            # Qdrant collection setup
│
├── requirements.txt              # Production dependencies
├── .env                          # Environment variables
└── README.md                     # This file
```

---

## Quick Start

### Prerequisites

- **Python 3.11+**
- **Neon PostgreSQL** database (free tier available)
- **Qdrant Cloud** account (free tier available)
- **OpenRouter API key** (free tier available)

### 1. Clone and Setup

```bash
cd backend/rag-chatbot

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file:

```bash
# Neon Serverless PostgreSQL
NEON_DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/dbname?sslmode=require

# Qdrant Cloud
QDRANT_URL=https://xxx.gcp.cloud.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-api-key
QDRANT_COLLECTION_NAME=textbook_chunks

# OpenRouter LLM (Free Tier)
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=mistralai/devstral-2512:free
BASE_URL=https://openrouter.ai/api/v1

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Logging
LOG_LEVEL=INFO
```

### 3. Start Backend

```bash
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Backend runs on:** http://localhost:8000
**API docs:** http://localhost:8000/docs
**Metrics:** http://localhost:8000/metrics

### 4. Verify Health

```bash
curl http://localhost:8000/health
```

**Expected Response:**
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

---

## API Endpoints

### Chat

```
POST /api/v1/chat/stream      - Streaming chat (SSE)
POST /api/v1/chat             - Non-streaming chat
GET  /api/v1/chat/history/{id} - Get conversation history
GET  /api/v1/chat/health      - Chat service health
```

### Sessions

```
POST /api/v1/sessions          - Create new session
GET  /api/v1/sessions/{id}     - Get session details
```

### System

```
GET /health                    - System health check
GET /docs                      - Swagger UI
GET /metrics                   - Prometheus metrics
```

### Request Format

```json
{
  "session_id": "uuid-string",
  "question": "What is ROS 2?",
  "selected_text": "optional-user-highlighted-text"
}
```

### Response Format (SSE)

```
data: {"type": "token", "content": "ROS "}
data: {"type": "token", "content": "2 "}
data: {"type": "citations", "citations": [{...}]}
data: {"type": "metadata", "metadata": {...}}
data: {"type": "done"}
```

---

## Selected Text Q&A Feature

When `selected_text` is provided in the request:

1. Selected text becomes **primary context** (confidence: 1.0)
2. Chatbot answers **strictly based on selected text**
3. Optionally supplements with 2 related chunks from vector search
4. Response focuses on explaining the selected content

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test",
    "question": "explain this",
    "selected_text": "ROS 2 is a next-generation robotics framework..."
  }'
```

---

## RAG Pipeline Details

### Embedding Generation

- **Model:** sentence-transformers/all-MiniLM-L6-v2
- **Dimensions:** 384
- **Cost:** FREE (local execution)
- **Latency:** ~100-200ms

### Vector Search

- **Database:** Qdrant Cloud Free Tier
- **Vectors:** 913 textbook chunks
- **Similarity:** Cosine similarity
- **Threshold:** 0.70 (adjustable)
- **Top-K:** 3-5 chunks retrieved

### LLM Generation

- **SDK:** OpenAI Agents SDK 0.6.0
- **Proxy:** LiteLLM → OpenRouter
- **Model:** mistralai/devstral-2512:free
- **Streaming:** Server-Sent Events (SSE)
- **Cost:** FREE (OpenRouter free tier)

### Citation System

Every response includes:
- Source chunk (chapter, section, URL)
- Confidence score (0.0-1.0)
- Text snippet (first 100 characters)
- Traceability to original content

---

## Performance Characteristics

- **First Token Latency:** ~1-2 seconds
- **Retrieval Time:** ~200-500ms (embedding + vector search)
- **Generation Time:** ~3-6 seconds (streaming)
- **Total End-to-End:** ~5-8 seconds
- **Concurrent Users:** 20+ supported

---

## Configuration

### Database Pool

```python
DB_POOL_MIN_SIZE=5
DB_POOL_MAX_SIZE=20
```

### Rate Limiting

```python
RATE_LIMIT_PER_MINUTE=10
```

### Logging

```python
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
LOG_JSON=false  # Set true for production
```

---

## Windows + WSL Support

If running backend on WSL and frontend on Windows:

1. Get WSL IP:
```bash
ip addr show eth0 | grep inet
```

2. Update frontend config to point to WSL IP:
```typescript
// frontend/src/components/ChatWidget/config.ts
return 'http://172.25.218.26:8000';  // Replace with your WSL IP
```

3. Ensure CORS allows frontend origin:
```bash
CORS_ORIGINS=http://localhost:3000,http://172.25.218.26:3000
```

---

## Testing

### Manual Testing

```bash
# Health check
curl http://localhost:8000/health

# Chat request
curl -X POST "http://localhost:8000/api/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "question": "What is ROS 2?"}'
```

### Expected Results

✅ Health endpoint returns `"status": "healthy"`
✅ Chat returns streaming SSE response with answer
✅ Citations included in metadata
✅ Conversation saved to PostgreSQL

---

## Troubleshooting

### Backend Won't Start

**Issue:** `ModuleNotFoundError` or import errors

**Solution:**
```bash
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

**Issue:** Health check shows `postgres: down`

**Solution:**
- Verify `NEON_DATABASE_URL` in `.env` is correct
- Ensure URL includes `?sslmode=require`
- Check network connectivity to Neon

### Qdrant Connection Failed

**Issue:** Health check shows `qdrant: down`

**Solution:**
- Verify `QDRANT_URL` and `QDRANT_API_KEY`
- Check Qdrant Cloud cluster status
- Ensure collection `textbook_chunks` exists (913 vectors)

### Embedding Model Not Loading

**Issue:** Sentence-transformers download fails

**Solution:**
```bash
# Pre-download model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

---

## Documentation

### Architecture
- **BACKEND_ARCHITECTURE_REPORT.md** - Complete system architecture
- **CLEANUP_SUMMARY.md** - Cleanup verification results
- **START_COMMANDS.md** - Startup procedures

### References
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **OpenAI Agents SDK:** https://github.com/openai/agents-sdk
- **Qdrant Cloud:** https://qdrant.tech/documentation/cloud/
- **Neon Postgres:** https://neon.tech/docs

---

## Production Checklist

- [x] FastAPI with async/await architecture
- [x] Neon Serverless PostgreSQL connected
- [x] Qdrant Cloud Free Tier operational (913 vectors)
- [x] OpenAI Agents SDK integrated
- [x] Local embeddings (zero API costs)
- [x] Streaming responses (SSE)
- [x] Selected text Q&A feature
- [x] Citation system
- [x] Session persistence
- [x] Structured logging
- [x] Prometheus metrics
- [x] Health check endpoint
- [x] CORS configured
- [x] Error handling

---

## License

MIT License - See root README for details

---

**Built with OpenAI Agents SDK, FastAPI, Neon PostgreSQL, and Qdrant Cloud** 🚀
