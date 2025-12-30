# Deployment Files Index

**Complete list of all files created for Hugging Face Spaces deployment**

---

## Quick Navigation

- **Start Here:** [DEPLOYMENT_QUICK_START.md](#deployment_quick_startmd)
- **Full Guide:** [HUGGINGFACE_DEPLOYMENT.md](#huggingface_deploymentmd)
- **Architecture:** [HF_DEPLOYMENT_ARCHITECTURE.md](#hf_deployment_architecturemd)
- **Summary:** [HF_DEPLOYMENT_SUMMARY.md](#hf_deployment_summarymd)

---

## Created Files

### 1. Docker Configuration

#### `Dockerfile.hf`
**Location:** `/mnt/e/phyai-humanoid-textbook/backend/rag-chatbot/Dockerfile.hf`

**Purpose:** HF Spaces-optimized Dockerfile

**Key Features:**
- Python 3.11-slim base image
- CPU-only PyTorch (smaller image)
- Sentence-transformers pre-installed
- Port 7860 (HF Spaces default)
- Non-root user (appuser, UID 1000)
- Health check every 30 seconds
- Optimized layer caching

**Usage:**
```bash
# Build locally for testing
docker build -f Dockerfile.hf -t rag-chatbot-hf .

# Run locally on port 7860
docker run -p 7860:7860 --env-file .env rag-chatbot-hf
```

**Deploy to HF Spaces:**
- Copy as `Dockerfile` in HF Space repository

---

### 2. Environment Configuration

#### `.env.hf-example`
**Location:** `/mnt/e/phyai-humanoid-textbook/backend/rag-chatbot/.env.hf-example`

**Purpose:** Template for HF Spaces environment variables

**Required Variables (8):**
- `OPENROUTER_API_KEY` - OpenRouter API key
- `OPENROUTER_MODEL` - LLM model (default: mistralai/devstral-2512:free)
- `BASE_URL` - OpenRouter base URL
- `QDRANT_URL` - Qdrant Cloud cluster URL
- `QDRANT_API_KEY` - Qdrant API key
- `QDRANT_COLLECTION_NAME` - Collection name (textbook_chunks)
- `NEON_DATABASE_URL` - Neon PostgreSQL connection string
- `CORS_ORIGINS` - Allowed frontend origins (comma-separated)

**Optional Variables (1):**
- `FRONTEND_URL` - Frontend URL (auto-added to CORS)

**Usage:**
1. Copy values to HF Spaces Settings > Repository Secrets
2. Each variable becomes a separate secret
3. Never commit actual values to git

---

### 3. HF Spaces README

#### `README-HF.md`
**Location:** `/mnt/e/phyai-humanoid-textbook/backend/rag-chatbot/README-HF.md`

**Purpose:** README for HF Spaces with metadata header

**Contains:**
- HF Spaces metadata (emoji, SDK, port)
- Project overview and features
- Technology stack
- API documentation
- Usage examples
- Environment variable reference
- Troubleshooting guide
- Performance metrics

**Deploy to HF Spaces:**
- Copy as `README.md` in HF Space repository

**HF Spaces Metadata:**
```yaml
---
title: PhyAI RAG Chatbot Backend
emoji: 🤖
colorFrom: blue
colorTo: cyan
sdk: docker
pinned: false
license: mit
app_port: 7860
---
```

---

### 4. Comprehensive Deployment Guide

#### `HUGGINGFACE_DEPLOYMENT.md`
**Location:** `/mnt/e/phyai-humanoid-textbook/backend/rag-chatbot/HUGGINGFACE_DEPLOYMENT.md`

**Purpose:** Complete step-by-step deployment instructions (15,000 words)

**Sections:**
1. Prerequisites
2. Create HF Space
3. Prepare repository files
4. Configure environment secrets
5. Deploy and monitor
6. Verify deployment
7. Update frontend configuration
8. Update CORS for new URLs
9. Troubleshooting guide
10. Performance optimization
11. Security best practices
12. Maintenance checklist
13. Cost breakdown

**Use Cases:**
- First-time deployment
- Detailed troubleshooting
- Understanding deployment process
- Reference documentation

---

### 5. Quick Start Guide

#### `DEPLOYMENT_QUICK_START.md`
**Location:** `/mnt/e/phyai-humanoid-textbook/backend/rag-chatbot/DEPLOYMENT_QUICK_START.md`

**Purpose:** Fast-track deployment (5 minutes)

**Sections:**
1. Create HF Space (1 min)
2. Push code (2 min)
3. Configure secrets (2 min)
4. Verify deployment (<1 min)
5. Update frontend

**Use Cases:**
- Experienced developers
- Quick redeployment
- Testing deployment process
- Team onboarding

---

### 6. Deployment Summary

#### `HF_DEPLOYMENT_SUMMARY.md`
**Location:** `/mnt/e/phyai-humanoid-textbook/backend/rag-chatbot/HF_DEPLOYMENT_SUMMARY.md`

**Purpose:** Overview of all deployment files and steps

**Contains:**
- Files created/modified list
- Prerequisites checklist
- Quick reference steps
- Environment variables table
- Health check format
- Troubleshooting quick reference
- Next steps

**Use Cases:**
- Project overview
- Quick reference
- Team documentation
- Status tracking

---

### 7. Architecture Diagrams

#### `HF_DEPLOYMENT_ARCHITECTURE.md`
**Location:** `/mnt/e/phyai-humanoid-textbook/backend/rag-chatbot/HF_DEPLOYMENT_ARCHITECTURE.md`

**Purpose:** Visual architecture documentation

**Diagrams:**
1. System Architecture (full stack)
2. Data Flow Diagram (request → response)
3. Network Flow (CORS, SSE)
4. Deployment Architecture (Docker layers)
5. Security Architecture (7 layers)
6. Monitoring Architecture (observability)
7. Cost Architecture (free tier breakdown)
8. Performance Architecture (latency breakdown)
9. Scalability Architecture (limits & scaling)

**Use Cases:**
- Understanding system design
- Troubleshooting flow issues
- Performance optimization
- Scaling planning

---

### 8. Local Testing Script

#### `test-hf-docker.sh`
**Location:** `/mnt/e/phyai-humanoid-textbook/backend/rag-chatbot/test-hf-docker.sh`

**Purpose:** Test Docker build locally before deploying to HF Spaces

**Features:**
- Builds Dockerfile.hf locally
- Runs container on port 7860
- Tests health endpoint
- Shows container logs
- Validates deployment

**Usage:**
```bash
cd backend/rag-chatbot
chmod +x test-hf-docker.sh
./test-hf-docker.sh
```

**Output:**
- Build status
- Container status
- Health check response
- API docs availability
- Container logs (last 20 lines)
- Next steps

---

### 9. This Index File

#### `DEPLOYMENT_FILES_INDEX.md`
**Location:** `/mnt/e/phyai-humanoid-textbook/backend/rag-chatbot/DEPLOYMENT_FILES_INDEX.md`

**Purpose:** Complete catalog of all deployment files

**Contains:**
- File listings with descriptions
- Usage instructions
- Navigation guide
- Workflow recommendations

---

## Modified Files

### 1. Main Application

#### `app/main.py`
**Location:** `/mnt/e/phyai-humanoid-textbook/backend/rag-chatbot/app/main.py`

**Changes:**
- Updated startup block comment to mention HF Spaces
- PORT environment variable supports 7860 (HF Spaces) and 8000 (local)
- No breaking changes to existing functionality

**Modified Section:**
```python
# =============== PLATFORM-FRIENDLY STARTUP BLOCK ===============
if __name__ == "__main__":
    # HF Spaces uses PORT=7860, Railway sets PORT dynamically
    # Fallback to 8000 for local development
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
    )
```

---

### 2. Configuration

#### `app/config.py`
**Location:** `/mnt/e/phyai-humanoid-textbook/backend/rag-chatbot/app/config.py`

**Changes:**
- Updated default CORS_ORIGINS to include Vercel production URL
- Added localhost:5173 for Vite development
- Supports FRONTEND_URL environment variable

**Modified Section:**
```python
# CORS Configuration (comma-separated origins)
# Production frontend URLs + local development
CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,https://phyai-humanoid-textbook.vercel.app"
```

**Impact:**
- CORS now allows Vercel production frontend by default
- Still supports local development
- Dynamic FRONTEND_URL can override/supplement

---

## Deployment Workflows

### Workflow 1: Quick Deployment (5 minutes)

**Recommended for:** Experienced developers, quick testing

1. Read: `DEPLOYMENT_QUICK_START.md`
2. Create HF Space
3. Copy files to HF Space repo
4. Configure 8 secrets
5. Push to HF Spaces
6. Verify health endpoint

**Files needed:**
- `Dockerfile.hf` → `Dockerfile`
- `README-HF.md` → `README.md`
- `requirements.txt`
- `app/` directory
- `scripts/` directory

---

### Workflow 2: Comprehensive Deployment (30 minutes)

**Recommended for:** First-time deployment, production setup

1. Read: `HUGGINGFACE_DEPLOYMENT.md` (full guide)
2. Review: `HF_DEPLOYMENT_ARCHITECTURE.md` (understand system)
3. Test locally: `./test-hf-docker.sh`
4. Create HF Space with proper settings
5. Configure all secrets with verification
6. Deploy and monitor build logs
7. Verify all endpoints
8. Update frontend configuration
9. Test end-to-end
10. Set up monitoring

**Files needed:**
- All deployment files
- Documentation for reference
- Testing script for validation

---

### Workflow 3: Local Testing First (10 minutes)

**Recommended for:** Validating changes, debugging

1. Create `.env` from `.env.hf-example`
2. Run: `./test-hf-docker.sh`
3. Verify health endpoint: `http://localhost:7860/health`
4. Test chat endpoint
5. Review logs
6. Fix any issues locally
7. Deploy to HF Spaces

**Files needed:**
- `Dockerfile.hf`
- `test-hf-docker.sh`
- `.env` (local configuration)

---

## File Dependencies

```
Dockerfile.hf
  ├─ requires: requirements.txt
  ├─ requires: app/ directory
  └─ requires: scripts/ directory

README-HF.md
  ├─ standalone (no dependencies)
  └─ metadata header for HF Spaces

.env.hf-example
  ├─ template for secrets
  └─ values copied to HF Spaces UI

test-hf-docker.sh
  ├─ requires: Dockerfile.hf
  ├─ requires: .env (local)
  └─ requires: Docker installed

HUGGINGFACE_DEPLOYMENT.md
  ├─ references: .env.hf-example
  ├─ references: Dockerfile.hf
  └─ references: README-HF.md

DEPLOYMENT_QUICK_START.md
  ├─ references: HUGGINGFACE_DEPLOYMENT.md
  └─ simplified subset of steps

HF_DEPLOYMENT_SUMMARY.md
  ├─ overview of all files
  └─ quick reference guide

HF_DEPLOYMENT_ARCHITECTURE.md
  ├─ standalone diagrams
  └─ explains deployment structure

DEPLOYMENT_FILES_INDEX.md (this file)
  └─ catalog of all files
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] Read deployment documentation
- [ ] Understand architecture (HF_DEPLOYMENT_ARCHITECTURE.md)
- [ ] Have Neon PostgreSQL credentials
- [ ] Have Qdrant Cloud credentials
- [ ] Have OpenRouter API key
- [ ] Note Vercel frontend URL
- [ ] Test locally (optional but recommended)

### HF Spaces Setup

- [ ] Create HF Space (Docker SDK, CPU basic)
- [ ] Clone HF Space repository
- [ ] Copy Dockerfile.hf as Dockerfile
- [ ] Copy README-HF.md as README.md
- [ ] Copy requirements.txt
- [ ] Copy app/ directory
- [ ] Copy scripts/ directory
- [ ] Commit and push to HF Spaces

### Environment Configuration

- [ ] Add OPENROUTER_API_KEY secret
- [ ] Add OPENROUTER_MODEL secret
- [ ] Add BASE_URL secret
- [ ] Add QDRANT_URL secret
- [ ] Add QDRANT_API_KEY secret
- [ ] Add QDRANT_COLLECTION_NAME secret
- [ ] Add NEON_DATABASE_URL secret
- [ ] Add CORS_ORIGINS secret (with Vercel URL)
- [ ] Add FRONTEND_URL secret (optional)

### Verification

- [ ] Build logs show success
- [ ] Health endpoint returns "healthy"
- [ ] /docs accessible (Swagger UI)
- [ ] Chat endpoint responds
- [ ] No CORS errors in browser
- [ ] Database connected (postgres: up)
- [ ] Qdrant connected (qdrant: up)

### Frontend Integration

- [ ] Update Vercel env var (VITE_API_BASE_URL)
- [ ] Or update frontend config file
- [ ] Redeploy frontend
- [ ] Test chat widget
- [ ] Verify streaming works
- [ ] Check citations appear

### Post-Deployment

- [ ] Document HF Space URL
- [ ] Update team documentation
- [ ] Set up monitoring (optional)
- [ ] Test with multiple users
- [ ] Verify performance acceptable

---

## Quick Reference Commands

### Local Testing

```bash
# Build and test locally
cd backend/rag-chatbot
./test-hf-docker.sh

# Manual Docker build
docker build -f Dockerfile.hf -t rag-chatbot-hf .

# Manual Docker run
docker run -p 7860:7860 --env-file .env rag-chatbot-hf

# View logs
docker logs -f rag-chatbot-hf-container

# Stop container
docker stop rag-chatbot-hf-container
docker rm rag-chatbot-hf-container
```

### HF Spaces Deployment

```bash
# Clone HF Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/phyai-rag-chatbot-backend

# Copy files
cp -r backend/rag-chatbot/app .
cp -r backend/rag-chatbot/scripts .
cp backend/rag-chatbot/requirements.txt .
cp backend/rag-chatbot/Dockerfile.hf Dockerfile
cp backend/rag-chatbot/README-HF.md README.md

# Deploy
git add .
git commit -m "Deploy RAG chatbot backend"
git push
```

### Testing Endpoints

```bash
# Health check
curl https://YOUR_USERNAME-phyai-rag-chatbot-backend.hf.space/health

# API docs (browser)
open https://YOUR_USERNAME-phyai-rag-chatbot-backend.hf.space/docs

# Chat test
curl -X POST "https://YOUR_USERNAME-phyai-rag-chatbot-backend.hf.space/api/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "question": "What is ROS 2?"}'

# Metrics
curl https://YOUR_USERNAME-phyai-rag-chatbot-backend.hf.space/metrics
```

---

## Support Resources

### Documentation Files

| File | Purpose | When to Use |
|------|---------|-------------|
| DEPLOYMENT_QUICK_START.md | Fast deployment | Quick setup, experienced devs |
| HUGGINGFACE_DEPLOYMENT.md | Full guide | First time, troubleshooting |
| HF_DEPLOYMENT_SUMMARY.md | Overview | Quick reference, status check |
| HF_DEPLOYMENT_ARCHITECTURE.md | Diagrams | Understanding system, debugging |
| .env.hf-example | Config template | Setting up secrets |
| test-hf-docker.sh | Local testing | Pre-deployment validation |

### External Resources

- **HF Spaces:** https://huggingface.co/docs/hub/spaces
- **FastAPI:** https://fastapi.tiangolo.com/
- **Qdrant:** https://qdrant.tech/documentation/
- **Neon:** https://neon.tech/docs
- **OpenRouter:** https://openrouter.ai/docs

---

## File Sizes

```
Dockerfile.hf                     1.7 KB
.env.hf-example                   1.7 KB
README-HF.md                      11 KB
HUGGINGFACE_DEPLOYMENT.md         15 KB
DEPLOYMENT_QUICK_START.md         2.8 KB
HF_DEPLOYMENT_SUMMARY.md          9.7 KB
HF_DEPLOYMENT_ARCHITECTURE.md     16 KB
test-hf-docker.sh                 3.5 KB
DEPLOYMENT_FILES_INDEX.md         (this file)

Total documentation:              ~60 KB
```

---

## Version History

**v1.0.0 - Initial Release (2025-12-30)**
- Created all deployment files
- Configured for HF Spaces
- Added CORS for Vercel
- Comprehensive documentation
- Local testing script
- Architecture diagrams

---

## Next Steps

1. **Choose Your Path:**
   - Quick: Start with `DEPLOYMENT_QUICK_START.md`
   - Comprehensive: Start with `HUGGINGFACE_DEPLOYMENT.md`
   - Test First: Run `./test-hf-docker.sh`

2. **Deploy to HF Spaces**

3. **Update Frontend**

4. **Test End-to-End**

5. **Monitor and Optimize**

---

**All files are ready for deployment!** 🚀

For questions or issues, refer to:
- Troubleshooting section in HUGGINGFACE_DEPLOYMENT.md
- Architecture diagrams in HF_DEPLOYMENT_ARCHITECTURE.md
- Quick reference in HF_DEPLOYMENT_SUMMARY.md
