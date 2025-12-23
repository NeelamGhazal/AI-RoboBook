# Backend RAG Chatbot: Institutional Knowledge & Skills

> **Purpose**: Reusable knowledge base extracted from real implementation challenges and solutions during the RAG chatbot backend development. Use this as a reference to prevent recurring issues.

**Last Updated**: 2025-12-23
**Project**: PhyAI Humanoid Textbook - RAG Backend
**Tech Stack**: FastAPI, Qdrant, Ollama, PostgreSQL, LangChain

---

## 🎯 Quick Reference: Top 5 Critical Rules

1. **NEVER validate or connect during module import** - Always use deferred `initialize()` pattern
2. **ALWAYS document path traversal** - Add inline comments showing each `parent` step
3. **USE local models by default** - Avoid API quota/cost issues
4. **ENFORCE consistent async patterns** - All clients must have `initialize()` and `close()`
5. **LOG with structure** - No print statements, use structured logging with context

---

## 📚 Detailed Knowledge Base

### 1. Path Resolution in Nested Structures

**When**: Working with scripts in deeply nested directory structures
**Problem**: Path traversal errors when accessing files in other parts of the project

**Solution Pattern**:
```python
from pathlib import Path

# ALWAYS document each level
# Current: backend/rag-chatbot/scripts/ingest_book.py
# parent = backend/rag-chatbot/scripts/
# parent.parent = backend/rag-chatbot/
# parent.parent.parent = backend/
# parent.parent.parent.parent = project root ✓
DOCS_DIR = Path(__file__).parent.parent.parent.parent / "frontend" / "docs"

# ALWAYS validate with debug output
print(f"[Path] Resolved docs directory: {DOCS_DIR.resolve()}")
print(f"[Path] Directory exists: {DOCS_DIR.exists()}")
assert DOCS_DIR.exists(), f"Docs directory not found: {DOCS_DIR}"
```

**Real Example**: Ingestion script failed with `parent.parent.parent` (3 levels) when it needed 4 levels to reach project root.

**Prevention Checklist**:
- [ ] Add inline comment documenting each `parent` step
- [ ] Print resolved path for debugging
- [ ] Add assertion to fail fast if path doesn't exist
- [ ] Test from different working directories

---

### 2. Async Client Initialization Pattern

**When**: Creating clients for external services (Qdrant, PostgreSQL, Ollama, etc.)
**Problem**: Module-level validation crashes application before startup

**Anti-Pattern (WRONG)**:
```python
# ❌ BAD: Runs at import time
import os
from qdrant_client import QdrantClient

QDRANT_URL = os.getenv("QDRANT_URL")
if not QDRANT_URL:
    raise ValueError("QDRANT_URL not set")  # Crashes on import!

client = QdrantClient(url=QDRANT_URL)  # Connects immediately
```

**Correct Pattern**:
```python
# ✅ GOOD: Deferred initialization
from app.core.config import settings

class QdrantClientWrapper:
    def __init__(self):
        self.client = None  # No connection yet

    async def initialize(self) -> None:
        """Connect and validate. Called AFTER app startup."""
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )
        # Verify connection
        await self.client.get_collections()

    async def close(self) -> None:
        """Cleanup resources."""
        if self.client:
            await self.client.close()

    async def search(self, query_vector, limit=5):
        if not self.client:
            raise RuntimeError("Client not initialized. Call initialize() first.")
        return await self.client.search(...)

# Global instance (not connected yet)
qdrant_client = QdrantClientWrapper()
```

**Integration with FastAPI**:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize all clients
    await db_client.initialize()
    await qdrant_client.initialize()
    await ollama_client.initialize()

    yield

    # Shutdown: Close all clients
    await ollama_client.close()
    await qdrant_client.close()
    await db_client.close()

app = FastAPI(lifespan=lifespan)
```

**Testing**:
```bash
# Should NOT crash on import
python -c "from app.clients.qdrant_client import qdrant_client; print('OK')"
```

**Prevention Checklist**:
- [ ] Client class with `__init__()` that doesn't connect
- [ ] `async initialize()` method that connects and validates
- [ ] `async close()` method for cleanup
- [ ] Operations check `if not self.client: raise RuntimeError(...)`
- [ ] Global instance registered in lifespan manager
- [ ] Test import doesn't crash

---

### 3. Vector Dimension Immutability

**When**: Changing embedding models or API providers
**Problem**: Vector dimensions are immutable in Qdrant collections

**Dimension Matrix**:
| Provider | Model | Dimensions | Status |
|----------|-------|------------|--------|
| OpenAI | text-embedding-3-small | 1536 | ❌ Expensive |
| Google | models/embedding-001 | 768 | ⚠️ Quota limits |
| Local | all-MiniLM-L6-v2 | 384 | ✅ Recommended |
| Local | all-mpnet-base-v2 | 768 | ✅ Higher quality |

**Migration Checklist** (when changing embedding model):
```python
# 1. Document new dimensions
VECTOR_SIZE = 384  # all-MiniLM-L6-v2
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# 2. Delete old collection
await qdrant_client.delete_collection("textbook_chunks")

# 3. Create new collection with new dimensions
await qdrant_client.create_collection(
    collection_name="textbook_chunks",
    vectors_config=VectorParams(
        size=VECTOR_SIZE,  # NEW dimensions
        distance=Distance.COSINE
    )
)

# 4. Re-ingest ALL content with new embeddings
await ingest_all_content()

# 5. Add validation check
async def validate_dimensions():
    info = await qdrant_client.get_collection("textbook_chunks")
    actual_dim = info.config.params.vectors.size
    if actual_dim != VECTOR_SIZE:
        raise ValueError(
            f"Dimension mismatch! Expected {VECTOR_SIZE}, got {actual_dim}. "
            f"Run migration script to recreate collection."
        )
```

**Prevention Checklist**:
- [ ] Choose embedding model carefully upfront (ADR required)
- [ ] Document dimensions in config.py with comment
- [ ] Add dimension validation on startup
- [ ] Include migration script in `/scripts/migrate_embeddings.py`
- [ ] Test with small dataset before full migration

---

### 4. API Quota Management

**When**: Using cloud API providers for embeddings or generation
**Problem**: Free tier quotas block batch operations

**Quota Reality Check**:
```
OpenAI Free Tier: No free tier (paid only)
Gemini Free Tier: 15 RPM, 1500 RPD (≈100-200 chunks/day max)
Textbook Size: 542 chunks (full ingestion impossible on free tier)
```

**Solution: Local-First Architecture**:
```python
# ✅ RECOMMENDED: Local embeddings (unlimited, free)
from sentence_transformers import SentenceTransformer

class LocalEmbeddingClient:
    async def initialize(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    async def embed(self, texts: List[str]) -> List[List[float]]:
        # Unlimited, free, fast (10ms per embedding)
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

# ⚠️ USE WITH CAUTION: API embeddings (quota limits)
class APIEmbeddingClient:
    async def embed_with_backoff(self, texts: List[str]):
        try:
            return await self.api.embed(texts)
        except QuotaExceededError as e:
            logger.error(
                "quota_exceeded",
                provider="gemini",
                quota="15 RPM / 1500 RPD",
                docs_url="/docs/local-embeddings-setup"
            )
            raise HTTPException(
                status_code=429,
                detail="Quota exceeded. Switch to local embeddings."
            )
```

**Prevention Checklist**:
- [ ] Default to local models (sentence-transformers)
- [ ] Document quota limits in README
- [ ] Add quota detection and helpful error messages
- [ ] Implement exponential backoff for API calls
- [ ] Log quota usage for monitoring

---

### 5. Token Counting Accuracy

**When**: Managing context windows for LLMs
**Problem**: Different providers use different tokenization

**Token Counting Strategies**:
```python
def count_tokens(text: str, model: str) -> int:
    """Provider-specific token counting."""

    if "gpt" in model:
        # OpenAI: Accurate counting with tiktoken
        import tiktoken
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))

    elif "gemini" in model:
        # Gemini: No official tokenizer, use approximation
        # Conservative estimate: 1 token ≈ 4 characters
        return len(text) // 4

    elif "llama" in model:
        # Llama: Use transformers tokenizer
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained(model)
        return len(tokenizer.encode(text))

    else:
        # Unknown: Very conservative fallback
        return len(text) // 3

# ALWAYS use conservative context limits
MAX_CONTEXT_TOKENS = int(model_max_tokens * 0.8)  # 80% of limit
```

**Prevention Checklist**:
- [ ] Use provider-specific counting when available
- [ ] Document approximation method in comments
- [ ] Set conservative limits (80% of actual max)
- [ ] Log actual vs estimated tokens for calibration
- [ ] Add buffer for system prompt and formatting

---

### 6. Streaming vs Non-Streaming Separation

**When**: Implementing both streaming and non-streaming endpoints
**Problem**: Trying to abstract both modes into one function creates complexity

**Pattern: Separate Functions**:
```python
# Non-streaming: Simple return
async def execute_rag_pipeline(
    question: str,
    conversation_history: List[Message]
) -> Tuple[str, List[Citation], dict]:
    chunks = await vector_search.search(question)
    citations = citation_builder.build(chunks)
    context = build_context(chunks, conversation_history)

    response = await llm.generate(context, question)
    metadata = {"chunks": len(chunks), ...}

    return response, citations, metadata

# Streaming: Async generator
async def execute_rag_pipeline_stream(
    question: str,
    conversation_history: List[Message]
):
    chunks = await vector_search.search(question)
    citations = citation_builder.build(chunks)
    context = build_context(chunks, conversation_history)

    # Stream tokens
    async for token in llm.generate_stream(context, question):
        yield {"type": "token", "content": token}

    # Send citations after completion
    yield {"type": "citations", "citations": citations}
    yield {"type": "done"}
```

**Prevention Checklist**:
- [ ] Separate functions for streaming vs non-streaming
- [ ] Don't try to abstract with flag like `stream=True`
- [ ] Share common logic (search, context building) via helper functions
- [ ] Document when to use each mode

---

### 7. Citation Deduplication

**When**: Building citations from vector search results
**Problem**: Multiple chunks from same chapter create redundant citations

**Deduplication Strategy**:
```python
def deduplicate_citations(citations: List[Citation]) -> List[Citation]:
    """Keep only highest-confidence citation per chapter."""

    # Sort by confidence (highest first)
    sorted_citations = sorted(
        citations,
        key=lambda c: c.confidence_score,
        reverse=True
    )

    # Keep first occurrence of each chapter
    seen_chapters = {}
    unique_citations = []

    for citation in sorted_citations:
        chapter_key = citation.chapter
        if chapter_key not in seen_chapters:
            seen_chapters[chapter_key] = True
            unique_citations.append(citation)

            # Limit to top 5 citations
            if len(unique_citations) >= 5:
                break

    return unique_citations
```

**Prevention Checklist**:
- [ ] Deduplicate at citation build time, not display time
- [ ] Sort by confidence before deduplication
- [ ] Limit total citations (3-5 is optimal)
- [ ] Log when deduplication reduces citation count

---

### 8. Context Window Management

**When**: Building prompts for LLMs
**Problem**: Exceeding context limits causes generation failures

**Conservative Context Management**:
```python
MAX_CONTEXT_TOKENS = 2000  # Conservative (model max is ~4000)
MAX_HISTORY_MESSAGES = 12  # Last 6 exchanges
MAX_CHUNK_TOKENS = 500     # Per chunk

def build_context(
    chunks: List[Chunk],
    conversation_history: List[Message]
) -> str:
    context_parts = []
    token_count = 0

    # Add chunks (priority)
    for i, chunk in enumerate(chunks):
        chunk_tokens = count_tokens(chunk.text)

        if token_count + chunk_tokens > MAX_CONTEXT_TOKENS:
            logger.info(
                "context_truncated",
                chunks_used=i,
                chunks_available=len(chunks),
                tokens_used=token_count
            )
            break

        context_parts.append(f"\n[Source: {chunk.chapter}]\n{chunk.text}")
        token_count += chunk_tokens

    # Add history if space remains
    history_budget = MAX_CONTEXT_TOKENS - token_count
    history_text = format_history(conversation_history[-MAX_HISTORY_MESSAGES:])
    history_tokens = count_tokens(history_text)

    if history_tokens <= history_budget:
        context_parts.insert(0, history_text)

    return "\n\n".join(context_parts)
```

**Prevention Checklist**:
- [ ] Set conservative token limits (80% of model max)
- [ ] Track token usage throughout context building
- [ ] Prioritize: chunks > conversation history
- [ ] Log when truncation occurs
- [ ] Test with maximum-size inputs

---

### 9. Structured Logging

**When**: All production code
**Problem**: Print statements and unstructured logs make debugging impossible

**Correct Logging Pattern**:
```python
import structlog

logger = structlog.get_logger(__name__)

# ✅ GOOD: Structured with context
logger.info(
    "rag_pipeline_complete",
    session_id=session_id,
    question=question[:50],  # Truncate for privacy
    chunks_retrieved=len(chunks),
    retrieval_time_ms=retrieval_ms,
    generation_time_ms=generation_ms,
    total_time_ms=total_ms,
    trace_id=request.headers.get("X-Trace-ID")
)

# ❌ BAD: Unstructured
print(f"RAG done in {total_ms}ms for question: {question}")
```

**Configuration**:
```python
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)
```

**Prevention Checklist**:
- [ ] Configure structlog at application startup
- [ ] Ban print() in linting rules
- [ ] Include trace_id for request tracking
- [ ] Use consistent event names (snake_case)
- [ ] Add context (session_id, user_id, etc.)

---

### 10. Error Handling Granularity

**When**: Handling external service failures
**Problem**: Generic errors make debugging and user communication difficult

**Granular Error Pattern**:
```python
from fastapi import HTTPException

async def execute_rag_pipeline(question: str):
    try:
        # Vector search
        try:
            chunks = await qdrant_client.search(question)
            if not chunks:
                logger.warning("no_chunks_found", question=question[:50])
                return {
                    "answer": "I couldn't find relevant information in the textbook.",
                    "citations": [],
                    "metadata": {"chunks_retrieved": 0}
                }
        except Exception as e:
            logger.error("qdrant_search_failed", error=str(e), error_type=type(e).__name__)
            raise HTTPException(
                status_code=503,
                detail="Vector search temporarily unavailable. Please try again."
            )

        # LLM generation
        try:
            response = await ollama_client.generate(question, chunks)
        except Exception as e:
            logger.error("llm_generation_failed", error=str(e), error_type=type(e).__name__)
            # Fallback: Return chunk text directly
            fallback = "\n\n".join(chunk.text for chunk in chunks[:2])
            return {
                "answer": f"Here's relevant information from the textbook:\n\n{fallback}",
                "citations": build_citations(chunks),
                "metadata": {"fallback_mode": True}
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("rag_pipeline_critical_failure", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Internal error processing your question."
        )
```

**Prevention Checklist**:
- [ ] Catch specific exceptions, not `Exception`
- [ ] Log with structured context (error type, message)
- [ ] Map errors to user-friendly messages
- [ ] Implement fallback strategies when possible
- [ ] Re-raise HTTPException without wrapping

---

### 11. Session Security

**When**: Implementing session-based APIs
**Problem**: Users accessing other users' sessions

**Secure Session Validation**:
```python
async def validate_session(
    session_id: str,
    user_id: str  # From auth token
) -> Session:
    """Validate session exists and belongs to user."""

    # Check session exists
    session = await db.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    # Check ownership
    if session.user_id != user_id:
        logger.warning(
            "unauthorized_session_access",
            session_id=session_id,
            session_owner=session.user_id,
            attempted_by=user_id
        )
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    # Update activity timestamp
    await db.update_session_activity(session_id)

    return session
```

**Prevention Checklist**:
- [ ] Always validate session ownership
- [ ] Log unauthorized access attempts
- [ ] Update activity timestamp on access
- [ ] Use UUIDs for session IDs (not incrementing integers)
- [ ] Consider rate limiting per user

---

### 12. Database Connection Pooling

**When**: Configuring PostgreSQL connections
**Problem**: Default settings cause timeouts under load

**Optimal Pool Configuration**:
```python
import asyncpg

pool = await asyncpg.create_pool(
    dsn=settings.DATABASE_URL,

    # Connection limits
    min_size=5,              # Minimum persistent connections
    max_size=20,             # Maximum concurrent connections

    # Lifecycle settings
    max_queries=50000,       # Queries per connection before refresh
    max_inactive_connection_lifetime=300,  # 5 minutes

    # Timeout settings
    command_timeout=10,      # 10 seconds per query
    timeout=30,              # 30 seconds to acquire connection

    # Health checking
    setup=setup_connection   # Run on each new connection
)

async def setup_connection(conn):
    """Run on each new connection."""
    # Set timezone
    await conn.execute("SET timezone TO 'UTC'")
    # Enable query logging (if needed)
    # await conn.execute("SET log_statement TO 'all'")
```

**Monitoring**:
```python
from prometheus_client import Gauge

db_pool_size = Gauge('db_pool_size', 'Database connection pool size')
db_pool_available = Gauge('db_pool_available', 'Available database connections')

# Update metrics periodically
async def monitor_pool():
    while True:
        db_pool_size.set(pool.get_size())
        db_pool_available.set(pool.get_idle_size())
        await asyncio.sleep(10)
```

**Prevention Checklist**:
- [ ] Start conservative (min=5, max=20)
- [ ] Monitor pool utilization with metrics
- [ ] Set appropriate timeouts
- [ ] Test under load with load testing tools
- [ ] Document pool settings in config comments

---

### 13. Performance Budgets

**When**: Ensuring acceptable response times
**Problem**: No visibility into where time is being spent

**Latency Tracking**:
```python
import time
from prometheus_client import Histogram

LATENCY = Histogram(
    'rag_latency_seconds',
    'RAG pipeline latency',
    ['stage']  # embedding, retrieval, generation, total
)

async def execute_rag_pipeline(question: str):
    start = time.time()
    stages = {}

    # Stage 1: Embedding
    t1 = time.time()
    query_embedding = await embedding_client.embed(question)
    stages['embedding_ms'] = (time.time() - t1) * 1000
    LATENCY.labels(stage='embedding').observe(time.time() - t1)

    # Stage 2: Vector search
    t2 = time.time()
    chunks = await qdrant_client.search(query_embedding)
    stages['retrieval_ms'] = (time.time() - t2) * 1000
    LATENCY.labels(stage='retrieval').observe(time.time() - t2)

    # Stage 3: LLM generation
    t3 = time.time()
    response = await llm.generate(chunks, question)
    stages['generation_ms'] = (time.time() - t3) * 1000
    LATENCY.labels(stage='generation').observe(time.time() - t3)

    # Total
    total_ms = (time.time() - start) * 1000
    stages['total_ms'] = total_ms
    LATENCY.labels(stage='total').observe(time.time() - start)

    # Alert on slow requests (> 3 seconds)
    if total_ms > 3000:
        logger.warning(
            "slow_request",
            question=question[:50],
            **stages
        )

    return response, citations, stages
```

**Prevention Checklist**:
- [ ] Track latency per stage
- [ ] Expose Prometheus metrics
- [ ] Log slow requests with stage breakdown
- [ ] Set up alerting for p95 > threshold
- [ ] Test with realistic data sizes

---

### 14. Hybrid Search for Selected Text

**When**: Implementing context-aware search
**Problem**: Balancing user question vs selected text importance

**Weighted Search Strategy**:
```python
async def search_with_selected_text(
    question: str,
    selected_text: str,
    question_weight: float = 0.7  # 70% question, 30% context
) -> List[Chunk]:
    """Hybrid search combining question and selected text."""

    # Generate separate embeddings
    question_emb = await embedding_client.embed(question)
    context_emb = await embedding_client.embed(selected_text)

    # Weighted combination
    hybrid_emb = [
        question_weight * q + (1 - question_weight) * c
        for q, c in zip(question_emb, context_emb)
    ]

    # Search with hybrid embedding
    chunks = await qdrant_client.search(
        query_vector=hybrid_emb,
        limit=8,  # More chunks for context-aware mode
        score_threshold=0.65  # Lower threshold (context is already relevant)
    )

    logger.info(
        "hybrid_search",
        question=question[:50],
        selected_text_length=len(selected_text),
        chunks_found=len(chunks),
        weight=question_weight
    )

    return chunks
```

**Weight Tuning Guide**:
- `0.5` (50/50): Equal importance to question and context
- `0.7` (70/30): **RECOMMENDED** - Prioritize question, use context as guide
- `0.8` (80/20): Mostly question, context is minor influence
- `0.3` (30/70): Mostly context (rare, for "explain this" type queries)

**Prevention Checklist**:
- [ ] Test multiple weight ratios
- [ ] Document chosen weights in ADR
- [ ] Make weights configurable
- [ ] Log weight in search metrics
- [ ] A/B test with users if possible

---

### 15. CORS Configuration for Streaming

**When**: Setting up SSE (Server-Sent Events) endpoints
**Problem**: Browsers block streaming requests without proper CORS

**Complete CORS Setup**:
```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "https://your-production-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, OPTIONS, etc.
    allow_headers=["*"],  # All headers
    expose_headers=["*"]  # Expose all response headers
)

# Streaming endpoint headers
@router.post("/stream")
async def stream_response():
    async def generate():
        # ... streaming logic
        yield "data: {}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
            # CORS headers automatically added by middleware
        }
    )
```

**Prevention Checklist**:
- [ ] Add CORS middleware before routes
- [ ] Include all dev server origins
- [ ] Set `allow_credentials=True` for cookies/auth
- [ ] Use `allow_methods=["*"]` for simplicity
- [ ] Test with browser DevTools network tab

---

## 🔍 Diagnostic Checklist

Use this when troubleshooting backend issues:

### Startup Issues
- [ ] Check all environment variables are set
- [ ] Verify clients don't connect during import
- [ ] Confirm `initialize()` called for each client
- [ ] Check port availability (8000, 6333, 5432)
- [ ] Review startup logs for errors

### Database Issues
- [ ] Verify connection pool settings
- [ ] Check PostgreSQL is running
- [ ] Confirm migrations are applied
- [ ] Test connection manually: `psql $DATABASE_URL`
- [ ] Monitor connection pool metrics

### Vector Search Issues
- [ ] Verify Qdrant is running: `curl localhost:6333/health`
- [ ] Check collection exists and has correct dimensions
- [ ] Confirm embeddings use same model as ingestion
- [ ] Test search manually via Qdrant UI
- [ ] Review similarity scores (should be > 0.7)

### LLM Generation Issues
- [ ] Verify Ollama is running: `curl localhost:11434/api/tags`
- [ ] Check model is pulled: `ollama list`
- [ ] Confirm context doesn't exceed limits
- [ ] Test generation with simple prompt
- [ ] Review generation parameters (temperature, max_tokens)

### Performance Issues
- [ ] Check p95 latency in metrics
- [ ] Review slow request logs
- [ ] Profile each stage (embedding, retrieval, generation)
- [ ] Monitor resource usage (CPU, RAM, GPU)
- [ ] Test with production-size data

---

## 📊 Success Metrics

Track these to ensure backend health:

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Availability** | 99.9% | Uptime monitoring |
| **P95 Latency** | < 3 seconds | Prometheus histogram |
| **Error Rate** | < 1% | Error counter / total requests |
| **Vector Search** | < 50ms | Stage latency tracking |
| **Embedding** | < 10ms | Stage latency tracking |
| **Generation** | < 2s | Stage latency tracking |
| **Connection Pool** | < 80% utilized | Pool metrics |
| **Memory Usage** | < 4GB | System metrics |

---

## 🚀 Quick Wins

Apply these for immediate improvements:

1. **Add health checks** to all external dependencies
2. **Implement connection pooling** for database
3. **Use structured logging** everywhere
4. **Add performance tracking** to RAG pipeline stages
5. **Set up Prometheus metrics** for observability
6. **Document all environment variables** in `.env.example`
7. **Create migration scripts** for schema/data changes
8. **Add input validation** with Pydantic models
9. **Implement graceful degradation** for service failures
10. **Write integration tests** for critical paths

---

## 📚 References

- **Specifications**: `/specs/003-rag-chatbot-backend/spec.md`
- **Implementation Plan**: `/specs/003-rag-chatbot-backend/plan.md`
- **Task Breakdown**: `/specs/003-rag-chatbot-backend/tasks.md`
- **Prompt History**: `/history/prompts/003-rag-chatbot-backend/`
- **Migration Guides**: `/backend/rag-chatbot/*_MIGRATION.md`
- **Fix Summaries**: `/backend/rag-chatbot/*_FIX_SUMMARY.md`

---

**Last Updated**: 2025-12-23
**Maintainer**: Development Team
**Status**: Living Document (update after each significant learning)
