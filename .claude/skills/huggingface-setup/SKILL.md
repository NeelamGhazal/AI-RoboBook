# huggingface-setup

Configure FastAPI application for Hugging Face Spaces deployment.

## Purpose
Prepare and configure FastAPI backend for deployment on Hugging Face Spaces with proper Docker configuration.

## Tasks
1. Create Dockerfile for FastAPI application
2. Setup requirements.txt with all dependencies
3. Create app.py as entry point
4. Configure HF Spaces settings
5. Setup environment variables
6. Configure port and host settings

## Dockerfile Template
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

## Requirements.txt Must Include
- fastapi
- uvicorn[standard]
- python-dotenv
- psycopg2-binary (for Neon Postgres)
- qdrant-client
- openai
- langchain (optional)
- pydantic
- httpx

## HF Spaces Configuration
- Port: 7860 (required by HF Spaces)
- Host: 0.0.0.0
- Framework: Docker SDK
- Hardware: CPU Basic (free tier)

## Environment Variables Setup
Create `.env` file structure (add actual values in HF Spaces settings):
```
OPENAI_API_KEY=your_key
NEON_DATABASE_URL=postgresql://...
QDRANT_URL=https://...
QDRANT_API_KEY=your_key
QDRANT_COLLECTION_NAME=book_content
CORS_ORIGINS=https://phyai-humanoid-textbook.vercel.app
```

## Key Points
- Always use port 7860 for HF Spaces
- Dockerfile must be in root directory
- Environment variables set in Space settings, not .env file
- Health check endpoint recommended
- Use uvicorn with proper host and port

## Critical Dependency Versions (PINNED)

**MUST use these exact versions to avoid deployment failures:**

```txt
# requirements.txt - Verified Working Versions
fastapi==0.115.0
uvicorn[standard]==0.30.6
python-multipart==0.0.9

# Database - CRITICAL: Pinned for Neon compatibility
asyncpg==0.29.0                # Use asyncpg, NOT psycopg2
pydantic>=2.12.3
pydantic-settings>=2.5.2

# Vector Database - CRITICAL: Pinned for Qdrant Cloud
qdrant-client==1.16.2

# Embeddings - CRITICAL: Version compatibility
sentence-transformers==3.0.1   # Must match huggingface-hub
huggingface-hub>=0.20.0        # Avoid ImportError: cached_download

# LLM Integration
openai>=2.9.0
openai-agents>=0.6.0           # For streaming support
litellm==1.80.11
tiktoken==0.7.0

# Utilities
httpx==0.27.2
structlog==24.4.0
prometheus-client==0.17.0
```

**Why These Versions Matter:**
- `sentence-transformers==3.0.1` + `huggingface-hub>=0.20.0`: Fixes ImportError for cached_download
- `asyncpg==0.29.0`: Required for Neon Serverless Postgres with SSL
- `qdrant-client==1.16.2`: Tested stable version for Qdrant Cloud
- `openai-agents>=0.6.0`: Enables streaming responses with Server-Sent Events

## Common Deployment Issues & Solutions

### Issue 1: ImportError - cached_download

**Error:**
```bash
ImportError: cannot import name 'cached_download' from 'huggingface_hub'
```

**Root Cause:**
Incompatible versions of `sentence-transformers` and `huggingface-hub`. Version `huggingface-hub>=0.26` removed the `cached_download()` function.

**Solution:**
```bash
# Update requirements.txt with compatible versions:
sentence-transformers==3.0.1
huggingface-hub>=0.20.0

# Also check Dockerfile - remove any duplicate sentence-transformers installation:
# BAD (in Dockerfile):
# RUN pip install sentence-transformers==2.2.2

# GOOD (only in requirements.txt):
# sentence-transformers==3.0.1
```

### Issue 2: CORS Errors from Vercel Frontend

**Error:**
```bash
Access to fetch at 'https://...hf.space/api/v1/chat' from origin 'https://...vercel.app'
has been blocked by CORS policy
```

**Root Cause:**
Backend CORS_ORIGINS doesn't include Vercel production domain.

**Solution:**
```bash
# 1. Go to HF Space Settings → Variables
# 2. Add or update CORS_ORIGINS:
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://your-site.vercel.app

# 3. In app/config.py, ensure CORS is parsed correctly:
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

# 4. In app/main.py, add CORS middleware:
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Rebuild HF Space (takes 8-10 min)
```

### Issue 3: Qdrant Connection Timeout

**Error:**
```bash
QdrantException: timed out
qdrant_client.http.exceptions.UnexpectedResponse: Unexpected Response: 401
```

**Root Cause:**
Incorrect QDRANT_URL format or missing/invalid API key.

**Solution:**
```bash
# Verify environment variables in HF Space Settings:
QDRANT_URL=https://your-cluster-id.us-east4-0.gcp.cloud.qdrant.io:6333
QDRANT_API_KEY=your-api-key-here
QDRANT_COLLECTION_NAME=textbook_chunks

# CRITICAL: URL must include:
# - https:// protocol
# - :6333 port
# - Full cluster URL from Qdrant Cloud dashboard

# Test connection manually:
curl -X GET "https://your-cluster-id.cloud.qdrant.io:6333/collections" \
  -H "api-key: your-qdrant-api-key"

# Expected: JSON response with collections list
```

### Issue 4: Neon Database Connection Failed

**Error:**
```bash
asyncpg.exceptions.InvalidPasswordError: password authentication failed
asyncpg.exceptions.UnsupportedClientFeatureError: SSL connection required
```

**Root Cause:**
Missing `?sslmode=require` parameter or incorrect connection string format.

**Solution:**
```bash
# In HF Space Settings → Variables, ensure correct format:
NEON_DATABASE_URL=postgresql://user:password@ep-name.region.neon.tech/dbname?sslmode=require

# CRITICAL components:
# 1. postgresql:// prefix (NOT postgres://)
# 2. Full endpoint URL from Neon dashboard
# 3. ?sslmode=require at the end (REQUIRED for Neon)
# 4. Use asyncpg driver, NOT psycopg2

# In requirements.txt:
asyncpg==0.29.0  # ✓ Correct
# psycopg2-binary  # ✗ Won't work with Neon Serverless

# Test connection:
python -c "
import asyncio
import asyncpg

async def test():
    conn = await asyncpg.connect('your-neon-url')
    result = await conn.fetchval('SELECT 1')
    print(f'Connection successful: {result}')
    await conn.close()

asyncio.run(test())
"
```

### Issue 5: ModuleNotFoundError After Deployment

**Error:**
```bash
ModuleNotFoundError: No module named 'asyncpg'
ModuleNotFoundError: No module named 'qdrant_client'
```

**Root Cause:**
Missing dependency in requirements.txt or typo in module name.

**Solution:**
```bash
# Verify requirements.txt includes ALL dependencies:
fastapi==0.115.0
uvicorn[standard]==0.30.6
asyncpg==0.29.0              # ← Database driver
qdrant-client==1.16.2        # ← Vector database client
sentence-transformers==3.0.1 # ← Embeddings
openai>=2.9.0                # ← LLM client

# Check for typos:
# ✓ asyncpg (correct)
# ✗ async-pg (wrong)
# ✓ qdrant-client (correct, with hyphen)
# ✗ qdrant_client (wrong in requirements.txt)

# Rebuild HF Space after fixing requirements.txt
```

### Issue 6: Application Startup Hangs

**Error:**
```bash
INFO:     Waiting for application startup...
# (then nothing, hangs indefinitely)
```

**Root Cause:**
Blocking operation in startup event or synchronous code in async function.

**Solution:**
```python
# Check app/main.py for startup events
# BAD (blocks startup):
@app.on_event("startup")
def startup():
    # Synchronous blocking call
    initialize_database()  # ✗

# GOOD (async, non-blocking):
@app.on_event("startup")
async def startup():
    # Async initialization
    await initialize_database()  # ✓

# Also check for:
# - Database connection pool creation (should be async)
# - Embedding model loading (move to lazy load if too slow)
# - External API calls during startup (should timeout)
```

## Deployment Verification Commands

### After Pushing to HF Spaces (wait 8-10 min):

```bash
# 1. Check build logs in HF Spaces dashboard
# Look for: "Application startup complete"

# 2. Test health endpoint
curl https://your-username-your-space-name.hf.space/health
# Expected: {"status": "healthy", "dependencies": {...}}

# 3. Test sessions creation
curl -X POST https://your-username-your-space-name.hf.space/api/v1/sessions \
  -H "Content-Type: application/json"
# Expected: {"session_id": "uuid-here"}

# 4. Test chat streaming
curl -X POST https://your-username-your-space-name.hf.space/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "question": "What is ROS 2?"}' \
  -N
# Expected: SSE stream with tokens

# 5. Verify CORS headers
curl -X OPTIONS https://your-username-your-space-name.hf.space/api/v1/chat \
  -H "Origin: https://your-site.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -v
# Expected: access-control-allow-origin in response headers
```

## Output
Docker-ready FastAPI application configured for HF Spaces deployment with verified dependency versions and comprehensive troubleshooting