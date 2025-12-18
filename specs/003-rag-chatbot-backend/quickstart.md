# Quick Start: RAG Chatbot Backend Development

**Feature**: 003-rag-chatbot-backend
**Purpose**: Get developers up and running with the RAG chatbot backend in <30 minutes

---

## Prerequisites

- Python 3.11+ installed
- Docker and Docker Compose (for local development)
- Git
- OpenAI API key
- Qdrant Cloud account (free tier)
- Neon Serverless Postgres account (free tier)

---

## 1. Clone and Setup

```bash
# Clone repository
git clone https://github.com/NeelamGhazal/AI-RoboBook.git
cd AI-RoboBook

# Check out feature branch
git checkout 003-rag-chatbot-backend

# Navigate to backend directory
cd backend/rag-chatbot
```

---

## 2. Create Virtual Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

---

## 3. Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

**requirements.txt** (reference):
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.0
pydantic-settings==2.1.0
openai==1.10.0
qdrant-client==1.7.0
asyncpg==0.29.0
httpx==0.26.0
python-multipart==0.0.6
structlog==24.1.0
prometheus-client==0.19.0
```

---

## 4. Environment Configuration

Create `.env` file in `backend/rag-chatbot/`:

```bash
# Copy template
cp .env.example .env

# Edit with your credentials
nano .env
```

**.env** contents:
```ini
# OpenAI Configuration
OPENAI_API_KEY=sk-...your-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Qdrant Cloud Configuration
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key
QDRANT_COLLECTION_NAME=textbook_chunks

# Neon Serverless Postgres
NEON_DATABASE_URL=postgresql://user:password@ep-xxxx.us-east-2.aws.neon.tech/neondb?sslmode=require

# Database Pool Configuration
DB_POOL_MIN_SIZE=5
DB_POOL_MAX_SIZE=20

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# CORS Configuration (comma-separated origins)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Rate Limiting
RATE_LIMIT_PER_MINUTE=10

# Logging
LOG_LEVEL=INFO
LOG_JSON=false
```

---

## 5. Database Schema Setup

```bash
# Run database migrations
python scripts/migrate.py

# Verify tables created
python scripts/verify_db.py
```

**Manual Postgres setup** (if needed):
```sql
-- Connect to Neon Postgres and run:
-- (Usually handled by migration script)

CREATE TABLE IF NOT EXISTS sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    token_count INTEGER NOT NULL,
    selected_text TEXT,
    citations JSONB,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_last_activity ON sessions(last_activity);
CREATE INDEX idx_messages_session_timestamp ON messages(session_id, timestamp DESC);
```

---

## 6. Qdrant Collection Setup

```bash
# Initialize Qdrant collection
python scripts/init_qdrant.py

# Verify collection created
python scripts/verify_qdrant.py
```

This creates the `textbook_chunks` collection with proper vector configuration.

---

## 7. Ingest Textbook Content

```bash
# Run ingestion pipeline
python scripts/ingest_textbook.py --source ../../frontend/docs --batch-size 250

# Expected output:
# ✓ Parsed 23 chapters
# ✓ Generated 460 chunks (500-1000 tokens each)
# ✓ Created embeddings for 460 chunks
# ✓ Uploaded to Qdrant in 2 batches
# ✓ Ingestion complete in 45 seconds
```

**Verify ingestion**:
```bash
# Check Qdrant collection stats
python scripts/verify_qdrant.py --verbose

# Output:
# Collection: textbook_chunks
# Vectors: 460
# Indexed: 460
# Status: ready
```

---

## 8. Start Development Server

```bash
# Start FastAPI server with hot-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Server should start at:
# http://localhost:8000

# API docs available at:
# http://localhost:8000/docs (Swagger)
# http://localhost:8000/redoc (ReDoc)
```

---

## 9. Test API Endpoints

### Health Check
```bash
curl http://localhost:8000/health

# Response:
# {
#   "status": "healthy",
#   "timestamp": "2025-12-17T10:30:00Z",
#   "dependencies": {
#     "postgres": "up",
#     "qdrant": "up",
#     "openai": "up"
#   }
# }
```

### Create Session
```bash
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{}'

# Response:
# {
#   "session_id": "123e4567-e89b-12d3-a456-426614174000",
#   "created_at": "2025-12-17T10:35:00Z"
# }
```

### Ask Question (General Q&A)
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "123e4567-e89b-12d3-a456-426614174000",
    "question": "What is a ROS 2 node?"
  }'

# Response:
# {
#   "message_id": "456e7890-e89b-12d3-a456-426614174000",
#   "session_id": "123e4567-e89b-12d3-a456-426614174000",
#   "answer": "A ROS 2 node is a fundamental building block...",
#   "citations": [
#     {
#       "chunk_id": "789e0123-e89b-12d3-a456-426614174000",
#       "chapter": "module1/chapter2",
#       "section": "Nodes, Topics, and Services",
#       "url": "/docs/module1/chapter2#nodes",
#       "confidence_score": 0.89,
#       "text_snippet": "In ROS 2, a node is an executable..."
#     }
#   ],
#   "timestamp": "2025-12-17T10:36:00Z",
#   "metadata": {
#     "retrieval_time_ms": 180,
#     "generation_time_ms": 1240,
#     "total_time_ms": 1420,
#     "token_count": 342,
#     "avg_confidence": 0.85
#   }
# }
```

### Selected Text Q&A
```bash
curl -X POST http://localhost:8000/chat/selected \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "123e4567-e89b-12d3-a456-426614174000",
    "question": "Can you explain this in simpler terms?",
    "selected_text": "The Data Distribution Service (DDS) is a middleware protocol..."
  }'
```

### Get Chat History
```bash
curl "http://localhost:8000/chat/history?session_id=123e4567-e89b-12d3-a456-426614174000&limit=10"

# Response:
# {
#   "session_id": "123e4567-e89b-12d3-a456-426614174000",
#   "messages": [
#     {
#       "message_id": "...",
#       "role": "user",
#       "content": "What is a ROS 2 node?",
#       "timestamp": "2025-12-17T10:36:00Z",
#       "token_count": 8
#     },
#     {
#       "message_id": "...",
#       "role": "assistant",
#       "content": "A ROS 2 node is...",
#       "timestamp": "2025-12-17T10:36:01Z",
#       "citations": [...],
#       "token_count": 342
#     }
#   ],
#   "total": 2,
#   "limit": 10,
#   "offset": 0
# }
```

---

## 10. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test suite
pytest tests/test_api.py -v

# Run with coverage
pytest --cov=app --cov-report=html tests/

# View coverage report
open htmlcov/index.html
```

---

## 11. Monitor Performance

### View Logs
```bash
# Tail logs in development
tail -f logs/app.log

# Filter for slow requests (>3s)
tail -f logs/app.log | grep slow_request
```

### Prometheus Metrics
```bash
# Metrics endpoint
curl http://localhost:8000/metrics

# Key metrics to watch:
# - rag_request_duration_seconds (latency)
# - rag_errors_total (error rate)
# - process_cpu_seconds_total (CPU usage)
```

---

## 12. Docker Compose (Alternative Setup)

```bash
# Start all services (backend + Postgres + optional monitoring)
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

**docker-compose.yml** (reference):
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - QDRANT_URL=${QDRANT_URL}
      - QDRANT_API_KEY=${QDRANT_API_KEY}
      - NEON_DATABASE_URL=${NEON_DATABASE_URL}
    volumes:
      - ./app:/app/app
      - ./logs:/app/logs
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
```

---

## Common Issues and Solutions

### Issue: "Connection refused" to Neon Postgres
**Solution**:
- Verify `NEON_DATABASE_URL` has `?sslmode=require` suffix
- Check network connectivity
- Confirm free tier is active (not suspended)

### Issue: Qdrant 401 Unauthorized
**Solution**:
- Verify `QDRANT_API_KEY` is correct
- Check Qdrant Cloud cluster is running
- Regenerate API key if needed

### Issue: OpenAI rate limit errors
**Solution**:
- Reduce `RATE_LIMIT_PER_MINUTE` to match your tier
- Implement exponential backoff retry logic
- Upgrade OpenAI plan if needed

### Issue: Slow responses (>3s)
**Solution**:
- Check `LOG_LEVEL=DEBUG` to see per-stage latency
- Verify Qdrant HNSW index is built (`indexed_vectors_count`)
- Consider switching to `gpt-4o-mini` for faster generation
- Reduce `top_k` from 10 to 5

### Issue: Database connection pool exhausted
**Solution**:
- Increase `DB_POOL_MAX_SIZE` (default 20)
- Check for connection leaks (ensure `async with` used)
- Restart server to reset pool

---

## Next Steps

1. **Read** `specs/003-rag-chatbot-backend/plan.md` for architecture details
2. **Explore** API docs at `http://localhost:8000/docs`
3. **Test** with frontend: Update frontend `.env` to point to `http://localhost:8000`
4. **Monitor** metrics: Set up Grafana dashboard for latency tracking
5. **Optimize**: Profile slow requests and tune HNSW/prompt parameters

---

## Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/your-feature

# 2. Make changes
# ...edit code...

# 3. Run tests
pytest tests/ -v

# 4. Lint and format
black app/ tests/
flake8 app/ tests/
mypy app/

# 5. Commit
git add .
git commit -m "feat: your feature description"

# 6. Push
git push origin feature/your-feature

# 7. Create PR
```

---

## Useful Commands

```bash
# Check API is running
curl http://localhost:8000/health

# View real-time logs
tail -f logs/app.log | jq .

# Monitor Postgres connections
python scripts/check_db_pool.py

# Re-ingest specific chapter
python scripts/ingest_textbook.py --chapter module1/chapter1

# Reset database (CAUTION: deletes all data)
python scripts/reset_db.py --confirm

# Export chat history for debugging
python scripts/export_history.py --session-id <uuid> --output history.json
```

---

**Happy coding!** 🚀

For questions or issues, check the [plan.md](./plan.md) architecture document or open a GitHub issue.
