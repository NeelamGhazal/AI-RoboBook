# Research: RAG Chatbot Backend Technical Patterns

**Feature**: 003-rag-chatbot-backend
**Created**: 2025-12-17
**Purpose**: Research findings for production RAG system design decisions

---

## 1. FastAPI Async Patterns for RAG Pipelines

### Decision
Use fully async/await architecture with:
- `httpx.AsyncClient` for OpenAI API calls with connection pooling
- `asyncpg` for Postgres database operations
- `qdrant-client` async methods for vector operations
- FastAPI background tasks for non-blocking operations
- Semaphore-based concurrency limiting

### Rationale
- **Performance**: Async I/O prevents thread blocking during network calls (OpenAI, Qdrant, Postgres)
- **Concurrency**: Single-threaded event loop handles 100+ concurrent requests efficiently
- **Latency**: Non-blocking operations critical for <3s response target
- **Connection Reuse**: Pooled connections reduce handshake overhead (100-200ms savings per request)

### Alternatives Considered
- **Threading**: Higher memory overhead, GIL contention, not suitable for I/O-bound workload
- **Sync FastAPI**: Blocks worker threads, poor concurrency, requires more uvicorn workers
- **Celery workers**: Adds complexity, unnecessary for streaming responses, higher latency

### Implementation Notes
```python
# Connection pool configuration
httpx_client = httpx.AsyncClient(
    timeout=httpx.Timeout(30.0, connect=5.0),
    limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
)

# Concurrency limiting
semaphore = asyncio.Semaphore(10)  # Max 10 concurrent OpenAI calls

# Async RAG pipeline
async with semaphore:
    embedding = await generate_embedding(question)
    chunks = await search_vectors(embedding)
    answer = await generate_response(question, chunks)
```

**Performance Target**: <500ms for embedding + <1s for retrieval + <1.5s for generation = <3s total

---

## 2. Qdrant Cloud Optimization

### Decision
Use Qdrant Cloud with:
- **Collection**: Single collection `textbook_chunks` with HNSW index
- **Vector size**: 1536 dimensions (OpenAI text-embedding-3-small)
- **Distance metric**: Cosine similarity
- **HNSW parameters**: `m=16`, `ef_construct=100`
- **Search parameters**: `top_k=10`, `score_threshold=0.70`, `ef=64`
- **Batch operations**: Ingest 100-500 points per batch

### Rationale
- **Latency**: HNSW index provides <50ms search at 500-1000 vectors scale
- **Accuracy**: Cosine similarity ideal for normalized embeddings
- **Free tier fit**: 23 chapters × 20 chunks = 460 vectors (well under 100K limit)
- **Batch ingestion**: 100-500 points/batch optimizes network overhead vs memory

### Alternatives Considered
- **Pinecone**: More expensive, no free tier, overkill for 500 vectors
- **pgvector**: Added complexity in Postgres, slower than dedicated vector DB
- **Chroma**: Requires self-hosting, less production-ready than Qdrant Cloud
- **Weaviate**: More complex schema, higher resource requirements

### Implementation Notes
```python
# Collection configuration
collection_config = {
    "vectors": {
        "size": 1536,
        "distance": "Cosine"
    },
    "hnsw_config": {
        "m": 16,  # 16 connections per layer
        "ef_construct": 100  # Higher = better accuracy, slower indexing
    },
    "optimizer_config": {
        "indexing_threshold": 10000  # Defer indexing until 10K points
    }
}

# Search parameters
search_params = {
    "limit": 10,  # Retrieve top 10 chunks
    "score_threshold": 0.70,  # Filter low-relevance results
    "params": {
        "hnsw_ef": 64,  # Search accuracy (higher = slower but more accurate)
        "exact": False  # Use approximate search (faster)
    }
}

# Batch ingestion
async def batch_upsert(points: List[PointStruct], batch_size=250):
    for i in range(0, len(points), batch_size):
        batch = points[i:i+batch_size]
        await qdrant_client.upsert(collection_name="textbook_chunks", points=batch)
```

**Performance Target**: <200ms for vector search with 460 vectors

---

## 3. Neon Serverless Postgres Patterns

### Decision
Use Neon Serverless Postgres with:
- **Connection pooling**: `asyncpg` pool (min=5, max=20 connections)
- **Query optimization**: Indexed columns, prepared statements
- **Cold start mitigation**: Keep-alive pings, connection pre-warming
- **Schema design**: JSONB for flexible citations, cascading deletes

### Rationale
- **Serverless fit**: Auto-scaling, pay-per-use, no infrastructure management
- **Free tier**: 512MB storage sufficient for 200K+ messages
- **Async support**: `asyncpg` is fastest Postgres driver for Python
- **Connection pooling**: Amortizes cold start penalty across requests

### Alternatives Considered
- **Supabase**: Postgres-based but requires more setup, no better performance
- **PlanetScale**: MySQL, not optimal for JSONB and async patterns
- **MongoDB**: Document model less suitable for relational session/message structure
- **DynamoDB**: Higher complexity, less query flexibility, cost unpredictable

### Implementation Notes
```python
# Connection pool setup
pool = await asyncpg.create_pool(
    dsn=NEON_DATABASE_URL,
    min_size=5,  # Minimum connections
    max_size=20,  # Maximum connections
    max_queries=50000,  # Refresh connections periodically
    max_inactive_connection_lifetime=300,  # 5 minutes
    command_timeout=10  # 10 second query timeout
)

# Prepared statement for history retrieval
async def get_history(session_id: UUID, limit: int = 50):
    query = """
        SELECT message_id, role, content, timestamp, citations
        FROM messages
        WHERE session_id = $1
        ORDER BY timestamp DESC
        LIMIT $2
    """
    async with pool.acquire() as conn:
        return await conn.fetch(query, session_id, limit)

# Keep-alive to reduce cold starts
async def keep_alive():
    while True:
        await asyncio.sleep(60)
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
```

**Performance Target**: <50ms for session CRUD, <100ms for history retrieval (50 messages)

---

## 4. OpenAI ChatKit SDK Integration

### Decision
Design API with OpenAI ChatKit SDK compatibility patterns:
- **Session management**: Create sessions with unique tokens (compatible with ChatKit client)
- **Streaming responses**: SSE format matching ChatKit expectations
- **Tool definition**: Prepare structure for future custom tools (e.g., Qdrant query tool)
- **Message format**: Follow ChatKit message schema (role, content, metadata)

### Rationale
- **Future-proofing**: Easy to extend with ChatKit agentic features (tools, client effects)
- **Standard patterns**: ChatKit SDK provides well-tested streaming and tool interfaces
- **Compatibility**: Frontend can use ChatKit client libraries for real-time updates
- **Modularity**: Clean separation between RAG logic and streaming/session management

### Alternatives Considered
- **Custom protocol**: More flexibility but reinventing wheel, no client library support
- **WebSockets**: More complex than SSE, overkill for unidirectional streaming
- **Plain REST**: No streaming support, poor UX for long responses

### Implementation Notes
```python
# ChatKit-compatible session endpoint
@app.post("/sessions")
async def create_session(user_id: Optional[str] = None):
    session_id = uuid4()
    # Store in Postgres
    await db.create_session(session_id, user_id)
    return {"session_id": session_id, "created_at": datetime.utcnow()}

# SSE streaming format (ChatKit-compatible)
@app.post("/chat")
async def chat(request: ChatRequest):
    if request.stream:
        return StreamingResponse(
            stream_response(request.session_id, request.question),
            media_type="text/event-stream"
        )
    else:
        return await generate_response(request.session_id, request.question)

# Future tool definition (ChatKit pattern)
qdrant_query_tool = {
    "type": "function",
    "function": {
        "name": "query_vector_store",
        "description": "Search textbook content for relevant chunks",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "top_k": {"type": "integer", "default": 5}
            }
        }
    }
}
```

**Note**: Full ChatKit SDK integration is optional for MVP but architecture supports future adoption.

---

## 5. RAG Pipeline Optimization

### Decision
Implement RAG pipeline with:
- **Chunking**: 500-1000 tokens per chunk, split by markdown headings
- **Chunk overlap**: 50 tokens between consecutive chunks
- **Context window**: 4K tokens max (GPT-4o supports 128K but constrain for cost/latency)
- **Retrieval strategy**: Top-10 chunks, filter to top-5 by confidence (>0.70)
- **Prompt engineering**: System prompt with explicit citation instructions
- **Citation extraction**: Parse LLM response for [source: chapter/section] markers

### Rationale
- **Chunk size**: 500-1000 tokens balances granularity (retrieval precision) vs context (semantic completeness)
- **Overlap**: Prevents information loss at chunk boundaries
- **Context limit**: 4K tokens = ~3 chunks + question + system prompt, optimizes cost and latency
- **Top-k filtering**: Retrieve 10, filter to 5 reduces false positives while ensuring diversity
- **Citation format**: Structured markers easier to parse than free-form references

### Alternatives Considered
- **Smaller chunks (200-300 tokens)**: More granular but loses context, noisier retrieval
- **Larger chunks (1500-2000 tokens)**: Better context but fewer chunks fit in window, less precise retrieval
- **No overlap**: Risks losing information at boundaries, lower recall
- **Dynamic context**: Complexity not justified for MVP, add if needed

### Implementation Notes
```python
# Chunking strategy
def chunk_markdown(content: str, max_tokens=800, overlap=50):
    chunks = []
    sections = content.split("##")  # Split by headings
    for section in sections:
        if len(tokenize(section)) > max_tokens:
            # Sub-chunk large sections
            sub_chunks = sliding_window(section, max_tokens, overlap)
            chunks.extend(sub_chunks)
        else:
            chunks.append(section)
    return chunks

# System prompt template
SYSTEM_PROMPT = """You are an expert on Physical AI and Humanoid Robotics textbook assistant.

Answer the user's question based on the provided textbook excerpts. Be accurate and cite your sources.

For each factual claim, cite the source using this format: [source: module{N}/chapter{M}, section: {heading}]

If the answer is not in the provided excerpts, say "This topic is not covered in the textbook."

Textbook excerpts:
{retrieved_chunks}
"""

# Retrieval and filtering
chunks = await qdrant.search(query_embedding, limit=10)
filtered_chunks = [c for c in chunks if c.score >= 0.70][:5]

# Context building
context = "\n\n---\n\n".join([
    f"[Excerpt {i+1}] Chapter: {c.chapter}, Section: {c.section}\n{c.text}"
    for i, c in enumerate(filtered_chunks)
])
```

**Performance Target**: <1s for embedding + retrieval + context building

---

## 6. Performance Monitoring and Bottleneck Detection

### Decision
Implement structured logging and metrics with:
- **Logging framework**: `structlog` for structured JSON logs
- **Latency tracking**: Measure each pipeline stage (embed, retrieve, generate, store)
- **Metrics**: Prometheus-compatible metrics (request duration, error rate, concurrency)
- **Health checks**: Postgres, Qdrant, OpenAI API status monitoring
- **Alerts**: Trigger on >3s p95 latency or >5% error rate

### Rationale
- **Observability**: Structured logs enable post-hoc analysis of slow requests
- **Bottleneck detection**: Per-stage metrics pinpoint optimization targets
- **Production readiness**: Prometheus standard for metrics, integrates with Grafana
- **SLA compliance**: Real-time monitoring ensures <3s response time SLA

### Alternatives Considered
- **Python logging**: Unstructured, harder to parse and analyze
- **APM tools (DataDog, New Relic)**: More expensive, overkill for MVP
- **No monitoring**: Unacceptable for performance-critical feature

### Implementation Notes
```python
import structlog
from prometheus_client import Histogram, Counter

# Structured logging
logger = structlog.get_logger()

# Prometheus metrics
REQUEST_DURATION = Histogram(
    "rag_request_duration_seconds",
    "RAG request latency",
    ["endpoint", "stage"]
)
ERROR_COUNTER = Counter("rag_errors_total", "Total errors", ["error_type"])

# Latency tracking
async def rag_pipeline(question: str):
    start = time.time()

    # Stage 1: Embedding
    with REQUEST_DURATION.labels(endpoint="/chat", stage="embed").time():
        embedding = await generate_embedding(question)
    logger.info("embedding_complete", duration_ms=(time.time()-start)*1000)

    # Stage 2: Retrieval
    retrieval_start = time.time()
    with REQUEST_DURATION.labels(endpoint="/chat", stage="retrieve").time():
        chunks = await search_vectors(embedding)
    logger.info("retrieval_complete", duration_ms=(time.time()-retrieval_start)*1000)

    # Stage 3: Generation
    gen_start = time.time()
    with REQUEST_DURATION.labels(endpoint="/chat", stage="generate").time():
        answer = await generate_response(question, chunks)
    logger.info("generation_complete", duration_ms=(time.time()-gen_start)*1000)

    total_duration = time.time() - start
    logger.info("request_complete", total_duration_ms=total_duration*1000)

    if total_duration > 3.0:
        logger.warning("slow_request", duration_ms=total_duration*1000)

    return answer
```

**Performance Target**: <3s p95 latency, <1% error rate, 100+ concurrent requests

---

## Summary of Key Technical Decisions

| Component | Decision | Key Metric |
|-----------|----------|------------|
| **Framework** | FastAPI with full async/await | 100 concurrent requests |
| **Database** | Neon Serverless Postgres + asyncpg | <100ms query latency |
| **Vector Store** | Qdrant Cloud (HNSW index) | <200ms search latency |
| **LLM** | OpenAI GPT-4o with streaming | <1.5s generation time |
| **Embeddings** | OpenAI text-embedding-3-small | <500ms embed time |
| **Chunking** | 500-1000 tokens, 50 token overlap | 460 total chunks |
| **Context** | Top-5 chunks, 4K token limit | <0.70 min confidence |
| **Monitoring** | Structlog + Prometheus | <3s p95 latency |

---

## Risk Mitigation for <3s Latency Goal

### Identified Risks

1. **OpenAI API latency variance (500ms-2s)**
   - Mitigation: Use GPT-4o-mini for faster responses if needed, implement timeout and retry
   - Fallback: Cache frequent Q&A pairs (bonus feature)

2. **Cold start penalty (Neon Postgres, Qdrant Cloud)**
   - Mitigation: Connection pooling, keep-alive pings, pre-warm connections at startup
   - Monitoring: Track cold start frequency and duration

3. **Large context exceeds token limit**
   - Mitigation: Limit to top-5 chunks, truncate if needed, use GPT-4o (128K context)
   - Detection: Log when context exceeds 4K tokens

4. **Concurrent request overload**
   - Mitigation: Semaphore-based rate limiting (10 concurrent OpenAI calls), queue excess requests
   - Scaling: Horizontal scaling with multiple FastAPI instances if needed

5. **Network latency (API calls to external services)**
   - Mitigation: Use connection pooling, async operations, timeout configuration
   - Monitoring: Track per-service latency (OpenAI, Qdrant, Neon)

### Performance Budget Breakdown

| Stage | Target | Worst Case | Notes |
|-------|--------|------------|-------|
| Embedding generation | 300ms | 500ms | OpenAI API call |
| Vector search | 100ms | 200ms | Qdrant HNSW index |
| Context building | 50ms | 100ms | In-memory operations |
| LLM generation | 1.2s | 2.0s | OpenAI GPT-4o streaming |
| History storage | 50ms | 100ms | Async Postgres insert |
| **Total** | **1.7s** | **2.9s** | Target: <3s p95 |

**Contingency Plans**:
- If p95 > 3s: Switch to GPT-4o-mini (faster but slightly less accurate)
- If embedding slow: Batch embeddings for similar questions (cache)
- If Qdrant slow: Optimize HNSW parameters or reduce top-k
- If Postgres slow: Batch history inserts (background task)
