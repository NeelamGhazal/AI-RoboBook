# Hugging Face Spaces Deployment Architecture

**Visual guide to the deployed RAG chatbot architecture**

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER BROWSER                             │
│              (https://phyai-humanoid-textbook.vercel.app)       │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          │ HTTPS Request
                          │ (CORS-validated)
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   VERCEL FRONTEND                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  React App (Next.js/Vite)                               │   │
│  │  - ChatWidget Component                                 │   │
│  │  - EventSource (SSE) Client                             │   │
│  │  - API Integration Layer                                │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          │ POST /api/v1/chat/stream
                          │ (Server-Sent Events)
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              HUGGING FACE SPACES BACKEND                        │
│       (https://username-phyai-rag-chatbot-backend.hf.space)     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Docker Container (Port 7860)                           │   │
│  │  ┌───────────────────────────────────────────────────┐  │   │
│  │  │  FastAPI Application                              │  │   │
│  │  │  ┌─────────────────────────────────────────────┐  │  │   │
│  │  │  │  CORS Middleware                            │  │  │   │
│  │  │  │  - Validates Vercel origin                  │  │  │   │
│  │  │  │  - Allows credentials                       │  │  │   │
│  │  │  └─────────────────────────────────────────────┘  │  │   │
│  │  │  ┌─────────────────────────────────────────────┐  │  │   │
│  │  │  │  API Endpoints                              │  │  │   │
│  │  │  │  - /health (health check)                   │  │  │   │
│  │  │  │  - /docs (Swagger UI)                       │  │  │   │
│  │  │  │  - /api/v1/chat/stream (streaming chat)     │  │  │   │
│  │  │  │  - /api/v1/sessions (session mgmt)          │  │  │   │
│  │  │  │  - /metrics (Prometheus)                    │  │  │   │
│  │  │  └─────────────────────────────────────────────┘  │  │   │
│  │  │  ┌─────────────────────────────────────────────┐  │  │   │
│  │  │  │  RAG Pipeline                               │  │  │   │
│  │  │  │  ┌───────────────────────────────────────┐  │  │  │   │
│  │  │  │  │ 1. Local Embedding Client             │  │  │  │   │
│  │  │  │  │    (sentence-transformers)            │  │  │  │   │
│  │  │  │  │    - Model: all-MiniLM-L6-v2          │  │  │  │   │
│  │  │  │  │    - Dimensions: 384                  │  │  │  │   │
│  │  │  │  │    - Cost: FREE (local)               │  │  │  │   │
│  │  │  │  └───────────────────────────────────────┘  │  │  │   │
│  │  │  │  ┌───────────────────────────────────────┐  │  │  │   │
│  │  │  │  │ 2. Vector Search Service              │  │  │  │   │
│  │  │  │  │    - Queries Qdrant Cloud             │  │  │  │   │
│  │  │  │  │    - Top-K retrieval (3-5 chunks)     │  │  │  │   │
│  │  │  │  │    - Cosine similarity (>0.70)        │  │  │  │   │
│  │  │  │  └───────────────────────────────────────┘  │  │  │   │
│  │  │  │  ┌───────────────────────────────────────┐  │  │  │   │
│  │  │  │  │ 3. LLM Service                        │  │  │  │   │
│  │  │  │  │    - OpenAI Agents SDK                │  │  │  │   │
│  │  │  │  │    - LiteLLM → OpenRouter             │  │  │  │   │
│  │  │  │  │    - Streaming SSE responses          │  │  │  │   │
│  │  │  │  └───────────────────────────────────────┘  │  │  │   │
│  │  │  │  ┌───────────────────────────────────────┐  │  │  │   │
│  │  │  │  │ 4. Citation Builder                   │  │  │  │   │
│  │  │  │  │    - Extracts sources                 │  │  │  │   │
│  │  │  │  │    - Confidence scores                │  │  │  │   │
│  │  │  │  └───────────────────────────────────────┘  │  │  │   │
│  │  │  └─────────────────────────────────────────────┘  │  │   │
│  │  └───────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
└──────────┬───────────────┬───────────────┬──────────────────────┘
           │               │               │
           │               │               │
           ▼               ▼               ▼
┌──────────────┐  ┌─────────────────┐  ┌──────────────────┐
│ Neon         │  │ Qdrant Cloud    │  │ OpenRouter       │
│ PostgreSQL   │  │                 │  │                  │
│              │  │                 │  │                  │
│ - Sessions   │  │ - Collection:   │  │ - Model:         │
│ - Messages   │  │   textbook_     │  │   mistralai/     │
│ - User data  │  │   chunks        │  │   devstral-      │
│              │  │ - 913 vectors   │  │   2512:free      │
│ - Free tier  │  │ - 384 dims      │  │                  │
│ - SSL conn   │  │ - Free tier     │  │ - Free tier      │
└──────────────┘  └─────────────────┘  └──────────────────┘
```

---

## Data Flow Diagram

```
User Question
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: REQUEST RECEIVED                                    │
│ - User types question in frontend                           │
│ - Frontend sends POST to /api/v1/chat/stream                │
│ - CORS validated (Vercel origin allowed)                    │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: SESSION LOOKUP                                      │
│ - Check if session_id exists in Neon PostgreSQL             │
│ - Create new session if needed                              │
│ - Load conversation history (last 10 messages)              │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: EMBEDDING GENERATION                                │
│ - Question text → Local sentence-transformers               │
│ - Generate 384-dimensional vector                           │
│ - Latency: ~100-200ms                                       │
│ - Cost: FREE (local execution)                              │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: VECTOR SEARCH                                       │
│ - Query Qdrant Cloud with embedding vector                  │
│ - Search in textbook_chunks collection (913 vectors)        │
│ - Retrieve top 3-5 similar chunks (cosine similarity >0.70) │
│ - Include metadata: chapter, section, page, URL             │
│ - Latency: ~200-300ms                                       │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: CONTEXT BUILDING                                    │
│ - Combine retrieved chunks                                  │
│ - Add conversation history                                  │
│ - Include selected_text if provided (confidence: 1.0)       │
│ - Build prompt with context                                 │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 6: LLM GENERATION                                      │
│ - OpenAI Agents SDK creates agent                           │
│ - LiteLLM routes to OpenRouter                              │
│ - Model: mistralai/devstral-2512:free                       │
│ - Streaming mode (token-by-token)                           │
│ - Latency: ~3-6 seconds                                     │
│ - Cost: FREE (OpenRouter free tier)                         │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 7: STREAMING RESPONSE                                  │
│ - Server-Sent Events (SSE) stream                           │
│ - Token events: {"type": "token", "content": "..."}         │
│ - Citation events: {"type": "citations", "citations": [...]}│
│ - Metadata events: {"type": "metadata", "metadata": {...}}  │
│ - Done event: {"type": "done"}                              │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 8: PERSISTENCE                                         │
│ - Save user question to Neon PostgreSQL                     │
│ - Save assistant response to Neon PostgreSQL                │
│ - Update session timestamp                                  │
│ - Log metrics to Prometheus                                 │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
                    Response Complete ✓
```

---

## Network Flow

```
┌──────────────────────────────────────────────────────────────┐
│                    BROWSER (User)                            │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            │ 1. HTTPS Request
                            │    Origin: https://phyai-humanoid-textbook.vercel.app
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│               VERCEL CDN (Frontend)                          │
│  - Serves React app                                          │
│  - Static assets cached                                      │
│  - Automatic HTTPS                                           │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            │ 2. API Request
                            │    POST /api/v1/chat/stream
                            │    Content-Type: application/json
                            │    Origin: https://phyai-humanoid-textbook.vercel.app
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│         HF SPACES (Backend - Port 7860)                      │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ CORS Middleware Check                                  │  │
│  │ - Verify origin in CORS_ORIGINS                        │  │
│  │ - Allow credentials: true                              │  │
│  │ - Set headers: Access-Control-Allow-Origin             │  │
│  └────────────────────────┬───────────────────────────────┘  │
│                           │ ✓ CORS Valid                     │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ FastAPI Router                                         │  │
│  │ - Route to /api/v1/chat/stream endpoint                │  │
│  │ - Parse request body (session_id, question)            │  │
│  └────────────────────────┬───────────────────────────────┘  │
│                           │                                   │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ RAG Pipeline Execution                                 │  │
│  │ (Steps 2-7 from Data Flow Diagram)                     │  │
│  └────────────────────────┬───────────────────────────────┘  │
│                           │                                   │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ SSE Response Stream                                    │  │
│  │ Content-Type: text/event-stream                        │  │
│  │ Cache-Control: no-cache                                │  │
│  │ Connection: keep-alive                                 │  │
│  └────────────────────────┬───────────────────────────────┘  │
└────────────────────────────┼──────────────────────────────────┘
                            │
                            │ 3. Streaming Response
                            │    data: {"type": "token", ...}
                            │    data: {"type": "token", ...}
                            │    data: {"type": "citations", ...}
                            │    data: {"type": "done"}
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│               VERCEL CDN (Frontend)                          │
│  - Receives SSE stream                                       │
│  - Passes to EventSource in browser                          │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            │ 4. Display in UI
                            │    Token-by-token rendering
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                    BROWSER (User)                            │
│  - EventSource processes stream                              │
│  - Updates UI in real-time                                   │
│  - Shows citations when received                             │
└──────────────────────────────────────────────────────────────┘
```

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              HUGGING FACE SPACES                            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Space Configuration                                   │  │
│  │ - SDK: Docker                                         │  │
│  │ - Hardware: CPU Basic (free)                          │  │
│  │ - Port: 7860 (exposed)                                │  │
│  │ - Visibility: Public                                  │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Docker Container                                      │  │
│  │ ┌─────────────────────────────────────────────────┐   │  │
│  │ │ Base Image: python:3.11-slim                    │   │  │
│  │ └─────────────────────────────────────────────────┘   │  │
│  │ ┌─────────────────────────────────────────────────┐   │  │
│  │ │ System Dependencies                             │   │  │
│  │ │ - gcc (for building Python packages)            │   │  │
│  │ │ - curl (for health checks)                      │   │  │
│  │ └─────────────────────────────────────────────────┘   │  │
│  │ ┌─────────────────────────────────────────────────┐   │  │
│  │ │ PyTorch CPU (lightweight)                       │   │  │
│  │ │ - Version: 2.6.0+cpu                            │   │  │
│  │ │ - Index: pytorch.org/whl/cpu                    │   │  │
│  │ └─────────────────────────────────────────────────┘   │  │
│  │ ┌─────────────────────────────────────────────────┐   │  │
│  │ │ Sentence Transformers                           │   │  │
│  │ │ - Model: all-MiniLM-L6-v2                       │   │  │
│  │ │ - Pre-downloaded during build                   │   │  │
│  │ └─────────────────────────────────────────────────┘   │  │
│  │ ┌─────────────────────────────────────────────────┐   │  │
│  │ │ Application Code                                │   │  │
│  │ │ - /app (working directory)                      │   │  │
│  │ │ - app/ (FastAPI application)                    │   │  │
│  │ │ - scripts/ (utility scripts)                    │   │  │
│  │ └─────────────────────────────────────────────────┘   │  │
│  │ ┌─────────────────────────────────────────────────┐   │  │
│  │ │ Environment Variables (Secrets)                 │   │  │
│  │ │ - OPENROUTER_API_KEY                            │   │  │
│  │ │ - QDRANT_URL, QDRANT_API_KEY                    │   │  │
│  │ │ - NEON_DATABASE_URL                             │   │  │
│  │ │ - CORS_ORIGINS                                  │   │  │
│  │ └─────────────────────────────────────────────────┘   │  │
│  │ ┌─────────────────────────────────────────────────┐   │  │
│  │ │ Startup Command                                 │   │  │
│  │ │ uvicorn app.main:app --host 0.0.0.0 --port 7860 │   │  │
│  │ └─────────────────────────────────────────────────┘   │  │
│  │ ┌─────────────────────────────────────────────────┐   │  │
│  │ │ Health Check                                    │   │  │
│  │ │ - Interval: 30s                                 │   │  │
│  │ │ - Timeout: 10s                                  │   │  │
│  │ │ - Start period: 40s                             │   │  │
│  │ │ - Command: curl http://localhost:7860/health    │   │  │
│  │ └─────────────────────────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   SECURITY LAYERS                           │
└─────────────────────────────────────────────────────────────┘

1. TRANSPORT SECURITY
   ┌────────────────────────────────────────────────────────┐
   │ HTTPS Only                                             │
   │ - HF Spaces provides automatic HTTPS                   │
   │ - TLS 1.2+ enforced                                    │
   │ - Certificate managed by HF                            │
   └────────────────────────────────────────────────────────┘

2. CORS PROTECTION
   ┌────────────────────────────────────────────────────────┐
   │ Origin Validation                                      │
   │ - Allowed: https://phyai-humanoid-textbook.vercel.app  │
   │ - Blocked: All other origins                           │
   │ - Credentials: Allowed from trusted origins            │
   └────────────────────────────────────────────────────────┘

3. SECRETS MANAGEMENT
   ┌────────────────────────────────────────────────────────┐
   │ Repository Secrets (Encrypted)                         │
   │ - API keys stored securely                             │
   │ - Not visible in logs                                  │
   │ - Not exposed in code                                  │
   │ - Injected at runtime                                  │
   └────────────────────────────────────────────────────────┘

4. DATABASE SECURITY
   ┌────────────────────────────────────────────────────────┐
   │ SSL Connections                                        │
   │ - Neon: sslmode=require                                │
   │ - Qdrant: HTTPS with API key                           │
   │ - Connection pooling (asyncpg)                         │
   └────────────────────────────────────────────────────────┘

5. CONTAINER SECURITY
   ┌────────────────────────────────────────────────────────┐
   │ Non-Root User                                          │
   │ - App runs as user 'appuser' (UID 1000)                │
   │ - Limited filesystem access                            │
   │ - No privilege escalation                              │
   └────────────────────────────────────────────────────────┘

6. RATE LIMITING
   ┌────────────────────────────────────────────────────────┐
   │ Request Throttling                                     │
   │ - 10 requests/minute per IP                            │
   │ - Protects against abuse                               │
   │ - Configurable in environment                          │
   └────────────────────────────────────────────────────────┘

7. INPUT VALIDATION
   ┌────────────────────────────────────────────────────────┐
   │ Pydantic Models                                        │
   │ - Type validation                                      │
   │ - Length limits                                        │
   │ - SQL injection prevention (parameterized queries)     │
   └────────────────────────────────────────────────────────┘
```

---

## Monitoring Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   OBSERVABILITY STACK                       │
└─────────────────────────────────────────────────────────────┘

1. STRUCTURED LOGGING
   ┌────────────────────────────────────────────────────────┐
   │ Structlog (JSON logs)                                  │
   │ - Application events                                   │
   │ - Error tracking                                       │
   │ - Request/response logging                             │
   │ - Visible in HF Spaces Logs tab                        │
   └────────────────────────────────────────────────────────┘

2. PROMETHEUS METRICS
   ┌────────────────────────────────────────────────────────┐
   │ /metrics Endpoint                                      │
   │ - rag_concurrent_requests (gauge)                      │
   │ - rag_request_duration_seconds (histogram)             │
   │ - rag_errors_total (counter)                           │
   │ - Per endpoint, per stage                              │
   └────────────────────────────────────────────────────────┘

3. HEALTH CHECKS
   ┌────────────────────────────────────────────────────────┐
   │ /health Endpoint                                       │
   │ - Overall status (healthy/degraded/unhealthy)          │
   │ - Dependency status (postgres/qdrant/openai)           │
   │ - Timestamp                                            │
   │ - Version info                                         │
   └────────────────────────────────────────────────────────┘

4. REQUEST TRACKING
   ┌────────────────────────────────────────────────────────┐
   │ Middleware Instrumentation                             │
   │ - Request ID generation                                │
   │ - Latency measurement                                  │
   │ - Error counting                                       │
   │ - Stage-by-stage timing                                │
   └────────────────────────────────────────────────────────┘
```

---

## Cost Architecture (Free Tier)

```
┌─────────────────────────────────────────────────────────────┐
│                    FREE TIER BREAKDOWN                      │
└─────────────────────────────────────────────────────────────┘

Service             Plan         Cost    Limits
──────────────────────────────────────────────────────────────
HF Spaces           CPU Basic    $0      - May sleep after 48h
                                         - Public visibility
                                         - 16GB RAM
                                         - 8 CPU cores

Neon PostgreSQL     Free Tier    $0      - 500MB storage
                                         - 1 project
                                         - Auto-suspend

Qdrant Cloud        Free Tier    $0      - 1GB storage
                                         - 1 cluster
                                         - Limited QPS

OpenRouter          Free Tier    $0      - devstral-2512:free
                                         - Daily request limit
                                         - Rate limited

Sentence-           Local        $0      - Runs in container
Transformers                             - No API calls
                                         - CPU inference

──────────────────────────────────────────────────────────────
TOTAL MONTHLY COST:                      $0
──────────────────────────────────────────────────────────────

UPGRADE PATH (Production):
  - HF Spaces Persistent: ~$15/month (no sleeping)
  - Neon Pro: $19/month (10GB storage)
  - Qdrant Paid: $25/month (5GB storage)
  - OpenRouter Paid: Pay-per-request (better models)

ESTIMATED PRODUCTION COST: ~$60-80/month
```

---

## Performance Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   LATENCY BREAKDOWN                         │
└─────────────────────────────────────────────────────────────┘

Request Stage                    Latency      Optimizations
──────────────────────────────────────────────────────────────
1. Network (Browser→Vercel)      ~50-100ms    CDN caching
2. Network (Vercel→HF Spaces)    ~100-200ms   Geographic routing
3. CORS validation               ~1-2ms       Middleware cache
4. Session lookup (Neon)         ~50-100ms    Connection pooling
5. Embedding generation          ~100-200ms   Local execution
6. Vector search (Qdrant)        ~200-300ms   Indexed search
7. Context building              ~10-20ms     In-memory
8. LLM first token (OpenRouter)  ~1000-2000ms Model warm-up
9. LLM streaming                 ~3000-6000ms Token generation
10. Database save (Neon)         ~50-100ms    Async operation

──────────────────────────────────────────────────────────────
TOTAL END-TO-END:                ~5-8 seconds
  - First token: ~1-2 seconds
  - Complete response: ~5-8 seconds
──────────────────────────────────────────────────────────────

OPTIMIZATION STRATEGIES:
  ✓ Connection pooling (asyncpg)
  ✓ Local embeddings (no API latency)
  ✓ Async/await architecture
  ✓ Streaming responses (progressive display)
  ✓ Indexed vector search (Qdrant)
  ✓ Cached CORS validation

COLD START:
  - HF Spaces sleep: ~30-60 seconds (free tier)
  - Persistent hardware eliminates cold starts
```

---

## Scalability Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   SCALING LIMITS                            │
└─────────────────────────────────────────────────────────────┘

Component           Free Tier Limit    Scaling Strategy
──────────────────────────────────────────────────────────────
HF Spaces           ~20 concurrent     Upgrade to persistent
                    requests           or use load balancer

Neon PostgreSQL     500MB storage      Upgrade to Pro plan
                    1 database         or use multiple projects

Qdrant Cloud        1GB vectors        Upgrade to paid tier
                    Limited QPS        or self-host

OpenRouter          Rate limited       Upgrade to paid tier
                    (free model)       or use direct OpenAI

Sentence-           CPU bound          Use GPU hardware
Transformers        ~5 req/sec         or batch processing

──────────────────────────────────────────────────────────────

HORIZONTAL SCALING (Future):
  - Multiple HF Spaces with load balancer
  - Shared Neon database (connection pooling)
  - Shared Qdrant cluster
  - Queue-based processing (Celery/Redis)

VERTICAL SCALING:
  - Upgrade HF Space hardware (GPU, more RAM)
  - Larger database tier
  - Larger vector database tier
  - Better LLM models (GPT-4, Claude)
```

---

This architecture provides a complete view of how the RAG chatbot backend is deployed and operates on Hugging Face Spaces, with clear paths for scaling and upgrading as needed.
