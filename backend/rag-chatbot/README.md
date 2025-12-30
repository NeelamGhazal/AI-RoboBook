---
title: PhyAI RAG Chatbot Backend
emoji: 🤖
colorFrom: blue
colorTo: blue
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# RAG Chatbot Backend - Hugging Face Spaces

**Production-Ready FastAPI Backend for Physical AI & Humanoid Robotics Textbook**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![OpenAI Agents SDK](https://img.shields.io/badge/OpenAI_Agents-0.6.0-412991?logo=openai&logoColor=white)](https://github.com/openai/agents-sdk)
[![Qdrant](https://img.shields.io/badge/Qdrant_Cloud-1.16-DC244C?logo=qdrant&logoColor=white)](https://qdrant.tech/)
[![Neon](https://img.shields.io/badge/Neon_Postgres-Serverless-00E699?logo=postgresql&logoColor=white)](https://neon.tech/)

---

## Overview

This is a FastAPI-based RAG (Retrieval-Augmented Generation) chatbot backend deployed on Hugging Face Spaces. It provides intelligent Q&A with streaming responses, citations, and context-aware explanations for the Physical AI & Humanoid Robotics Textbook.

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
- **Uvicorn** - ASGI server for production deployment

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
- **Prometheus** - Metrics and monitoring (`/metrics` endpoint)

---

## API Endpoints

### Health & Docs
```
GET  /                         - API information
GET  /health                   - Health check (dependencies status)
GET  /docs                     - Swagger UI (interactive API docs)
GET  /metrics                  - Prometheus metrics
```

### Chat
```
POST /api/v1/chat/stream      - Streaming chat (SSE)
GET  /api/v1/chat/health      - Chat service health
```

### Sessions
```
POST /api/v1/sessions          - Create new session
GET  /api/v1/sessions/{id}     - Get session details
```

---

## Usage

### Frontend Integration

This backend is designed to work with the Vercel-hosted frontend at:
**https://phyai-humanoid-textbook.vercel.app**

Update your frontend configuration to point to this HF Space URL:

```typescript
// frontend/src/components/ChatWidget/config.ts
export const API_BASE_URL = 'https://your-space-name.hf.space';
```

### Direct API Testing

#### Health Check
```bash
curl https://your-space-name.hf.space/health
```

#### Chat Request (Streaming)
```bash
curl -X POST "https://your-space-name.hf.space/api/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-123",
    "question": "What is ROS 2?",
    "selected_text": ""
  }'
```

#### Chat Request with Selected Text
```bash
curl -X POST "https://your-space-name.hf.space/api/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-123",
    "question": "Explain this concept",
    "selected_text": "ROS 2 is a next-generation robotics framework..."
  }'
```

---

## Request/Response Format

### Request Body
```json
{
  "session_id": "uuid-string",
  "question": "What is ROS 2?",
  "selected_text": "optional-user-highlighted-text"
}
```

### Streaming Response (SSE)
```
data: {"type": "token", "content": "ROS "}
data: {"type": "token", "content": "2 "}
data: {"type": "token", "content": "is "}
data: {"type": "citations", "citations": [{"chapter": "2", "confidence": 0.85, ...}]}
data: {"type": "metadata", "metadata": {"total_tokens": 150, ...}}
data: {"type": "done"}
```

---

## Environment Configuration

This Space requires the following **Repository Secrets** (configured in Settings):

### Required Secrets

1. **OPENROUTER_API_KEY** - OpenRouter API key for LLM access
   - Get from: https://openrouter.ai/keys
   - Example: `sk-or-v1-xxxxxxxxxxxxx`

2. **QDRANT_URL** - Qdrant Cloud cluster URL
   - Example: `https://xxx-xxx.gcp.cloud.qdrant.io:6333`

3. **QDRANT_API_KEY** - Qdrant Cloud API key
   - Get from: https://cloud.qdrant.io/

4. **NEON_DATABASE_URL** - Neon PostgreSQL connection string
   - Format: `postgresql://user:password@ep-xxx.region.neon.tech/dbname?sslmode=require`

5. **CORS_ORIGINS** - Allowed frontend origins (comma-separated)
   - Example: `https://phyai-humanoid-textbook.vercel.app,http://localhost:3000`

### Optional Configuration

- **OPENROUTER_MODEL** - LLM model (default: `mistralai/devstral-2512:free`)
- **QDRANT_COLLECTION_NAME** - Collection name (default: `textbook_chunks`)
- **DB_POOL_MIN_SIZE** - Min database connections (default: `5`)
- **DB_POOL_MAX_SIZE** - Max database connections (default: `20`)
- **RATE_LIMIT_PER_MINUTE** - Rate limit (default: `10`)
- **LOG_LEVEL** - Logging level (default: `INFO`)

---

## CORS Configuration

The backend is configured to accept requests from:

1. **Production Frontend** - `https://phyai-humanoid-textbook.vercel.app`
2. **Vercel Preview Deployments** - Add preview URLs to `CORS_ORIGINS`
3. **Local Development** - `http://localhost:3000`, `http://localhost:5173`

**Important:** Ensure your Vercel frontend URL is added to the `CORS_ORIGINS` environment variable.

---

## RAG Pipeline Details

### Data Flow

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

### Embedding Generation
- **Model:** sentence-transformers/all-MiniLM-L6-v2
- **Dimensions:** 384
- **Cost:** FREE (local execution)
- **Latency:** ~100-200ms

### Vector Search
- **Database:** Qdrant Cloud Free Tier
- **Vectors:** 913 textbook chunks
- **Similarity:** Cosine similarity
- **Threshold:** 0.70
- **Top-K:** 3-5 chunks retrieved

### LLM Generation
- **SDK:** OpenAI Agents SDK 0.6.0
- **Proxy:** LiteLLM → OpenRouter
- **Model:** mistralai/devstral-2512:free
- **Streaming:** Server-Sent Events (SSE)
- **Cost:** FREE (OpenRouter free tier)

---

## Performance

- **First Token Latency:** ~1-2 seconds
- **Retrieval Time:** ~200-500ms (embedding + vector search)
- **Generation Time:** ~3-6 seconds (streaming)
- **Total End-to-End:** ~5-8 seconds
- **Concurrent Users:** 20+ supported

---

## Monitoring

### Health Check
```bash
curl https://your-space-name.hf.space/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-30T12:00:00Z",
  "dependencies": {
    "postgres": "up",
    "qdrant": "up",
    "openai": "assumed_up"
  },
  "version": "1.0.0"
}
```

### Prometheus Metrics
```bash
curl https://your-space-name.hf.space/metrics
```

**Available Metrics:**
- `rag_concurrent_requests` - Active concurrent requests
- `rag_request_duration_seconds` - Request latency by endpoint and stage
- `rag_errors_total` - Error counter by type

---

## Deployment Instructions

### Setting Up Repository Secrets

1. **Navigate to Space Settings**
   - Go to your HF Space
   - Click "Settings" tab
   - Select "Repository Secrets"

2. **Add Required Secrets**
   - Click "Add a new secret"
   - Enter secret name (e.g., `OPENROUTER_API_KEY`)
   - Paste secret value
   - Click "Add secret"
   - Repeat for all required secrets

3. **Verify Configuration**
   - Check "Logs" tab after deployment
   - Ensure no errors in startup logs
   - Test `/health` endpoint

### Updating CORS Origins

When deploying to a new Vercel URL:

1. Update `CORS_ORIGINS` secret in HF Spaces
2. Include both production and preview URLs:
   ```
   https://phyai-humanoid-textbook.vercel.app,https://phyai-humanoid-textbook-git-feature-yourname.vercel.app
   ```
3. Restart the Space for changes to take effect

---

## Troubleshooting

### Space Won't Start

**Check Logs:**
- Go to "Logs" tab in HF Space
- Look for error messages during startup

**Common Issues:**
- Missing environment variables (check all required secrets are set)
- Invalid database URL (verify Neon connection string)
- Qdrant collection not found (ensure collection exists with 913 vectors)

### CORS Errors from Frontend

**Symptoms:**
- Browser console shows "blocked by CORS policy"

**Solution:**
1. Verify `CORS_ORIGINS` includes your Vercel URL
2. Ensure no typos in the URL (check protocol: `https://`)
3. Restart Space after updating secrets

### Database Connection Failed

**Symptoms:**
- Health check shows `postgres: down`

**Solution:**
- Verify `NEON_DATABASE_URL` format includes `?sslmode=require`
- Check Neon console for database status
- Ensure IP whitelisting allows HF Spaces (Neon allows all IPs by default)

### Qdrant Connection Failed

**Symptoms:**
- Health check shows `qdrant: down`

**Solution:**
- Verify `QDRANT_URL` format: `https://xxx.gcp.cloud.qdrant.io:6333`
- Check Qdrant Cloud console for cluster status
- Ensure collection `textbook_chunks` exists

---

## Security Best Practices

✅ **All secrets stored in HF Spaces Repository Secrets (encrypted)**
✅ **CORS restricted to specific frontend domains**
✅ **Non-root user in Docker container**
✅ **Database connections use SSL (`sslmode=require`)**
✅ **Rate limiting enabled (10 requests/minute per IP)**
✅ **Structured logging (no sensitive data in logs)**

---

## License

MIT License - See repository for details

---

## Support

For issues or questions:
- **Documentation:** See full README in repository
- **API Docs:** Visit `/docs` endpoint for interactive Swagger UI
- **Health Check:** Monitor `/health` endpoint for system status

---

**Built with OpenAI Agents SDK, FastAPI, Neon PostgreSQL, and Qdrant Cloud** 🚀
