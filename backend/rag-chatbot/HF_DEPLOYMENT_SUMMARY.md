# Hugging Face Spaces Deployment - Summary

**All configuration files have been created for HF Spaces deployment**

---

## Files Created

### 1. Docker Configuration
- **File:** `/mnt/e/phyai-humanoid-textbook/backend/rag-chatbot/Dockerfile.hf`
- **Purpose:** HF Spaces-optimized Dockerfile (port 7860, non-root user, health checks)
- **Key features:**
  - Python 3.11-slim base image
  - CPU-only PyTorch for smaller image size
  - Sentence-transformers pre-installed
  - Runs on port 7860 (HF Spaces default)
  - Non-root user for security
  - Health check every 30 seconds

### 2. Environment Configuration
- **File:** `/mnt/e/phyai-humanoid-textbook/backend/rag-chatbot/.env.hf-example`
- **Purpose:** Template for HF Spaces environment variables
- **Variables required:**
  - `OPENROUTER_API_KEY` - OpenRouter API key
  - `OPENROUTER_MODEL` - Model name (default: mistralai/devstral-2512:free)
  - `BASE_URL` - OpenRouter base URL
  - `QDRANT_URL` - Qdrant Cloud cluster URL
  - `QDRANT_API_KEY` - Qdrant API key
  - `QDRANT_COLLECTION_NAME` - Collection name (textbook_chunks)
  - `NEON_DATABASE_URL` - Neon PostgreSQL connection string
  - `CORS_ORIGINS` - Allowed frontend origins (includes Vercel URL)

### 3. HF Spaces README
- **File:** `/mnt/e/phyai-humanoid-textbook/backend/rag-chatbot/README-HF.md`
- **Purpose:** README with HF Spaces metadata header
- **Includes:**
  - Space configuration (emoji, SDK, port)
  - API documentation
  - Usage examples
  - Environment variable documentation
  - Troubleshooting guide

### 4. Deployment Guide (Comprehensive)
- **File:** `/mnt/e/phyai-humanoid-textbook/backend/rag-chatbot/HUGGINGFACE_DEPLOYMENT.md`
- **Purpose:** Complete step-by-step deployment instructions
- **Covers:**
  - Prerequisites
  - Space creation
  - File preparation
  - Secret configuration
  - Deployment verification
  - Frontend integration
  - Troubleshooting
  - Performance optimization
  - Maintenance

### 5. Quick Start Guide
- **File:** `/mnt/e/phyai-humanoid-textbook/backend/rag-chatbot/DEPLOYMENT_QUICK_START.md`
- **Purpose:** Fast-track deployment (5 minutes)
- **For:** Experienced developers who want quick deployment

### 6. Local Testing Script
- **File:** `/mnt/e/phyai-humanoid-textbook/backend/rag-chatbot/test-hf-docker.sh`
- **Purpose:** Test Docker build locally before pushing to HF Spaces
- **Usage:**
  ```bash
  cd backend/rag-chatbot
  ./test-hf-docker.sh
  ```

---

## Files Modified

### 1. Main Application
- **File:** `/mnt/e/phyai-humanoid-textbook/backend/rag-chatbot/app/main.py`
- **Changes:**
  - Updated startup block comment to mention HF Spaces
  - Supports PORT environment variable (7860 for HF Spaces)

### 2. Configuration
- **File:** `/mnt/e/phyai-humanoid-textbook/backend/rag-chatbot/app/config.py`
- **Changes:**
  - Updated default CORS_ORIGINS to include Vercel production URL
  - Added support for FRONTEND_URL environment variable

---

## Deployment Prerequisites

Before deploying, ensure you have:

1. **Hugging Face Account**
   - Sign up: https://huggingface.co/join
   - Free tier is sufficient

2. **Neon PostgreSQL Database**
   - Already configured in your .env
   - Connection string format: `postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require`

3. **Qdrant Cloud Cluster**
   - Already configured in your .env
   - Collection: textbook_chunks (913 vectors)

4. **OpenRouter API Key**
   - Already configured in your .env
   - Free tier model: mistralai/devstral-2512:free

5. **Vercel Frontend URL**
   - Production URL: `https://phyai-humanoid-textbook.vercel.app`
   - Will be added to CORS_ORIGINS

---

## Deployment Steps (Quick Reference)

### Step 1: Create HF Space
1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Choose Docker SDK, CPU basic hardware
4. Name: `phyai-rag-chatbot-backend`

### Step 2: Upload Files
```bash
# Clone HF Space repo
git clone https://huggingface.co/spaces/YOUR_USERNAME/phyai-rag-chatbot-backend

# Copy files
cp -r backend/rag-chatbot/app .
cp -r backend/rag-chatbot/scripts .
cp backend/rag-chatbot/requirements.txt .
cp backend/rag-chatbot/Dockerfile.hf Dockerfile
cp backend/rag-chatbot/README-HF.md README.md

# Push
git add .
git commit -m "Initial deployment"
git push
```

### Step 3: Configure Secrets
In HF Space Settings > Repository Secrets, add:
- OPENROUTER_API_KEY
- OPENROUTER_MODEL
- BASE_URL
- QDRANT_URL
- QDRANT_API_KEY
- QDRANT_COLLECTION_NAME
- NEON_DATABASE_URL
- CORS_ORIGINS

### Step 4: Verify Deployment
```bash
curl https://YOUR_USERNAME-phyai-rag-chatbot-backend.hf.space/health
```

### Step 5: Update Frontend
Add to Vercel environment variables:
```
VITE_API_BASE_URL=https://YOUR_USERNAME-phyai-rag-chatbot-backend.hf.space
```

---

## Testing Before Deployment

**Local Docker test:**
```bash
cd backend/rag-chatbot
./test-hf-docker.sh
```

This will:
- Build the Docker image locally
- Run on port 7860
- Test health endpoint
- Show container logs
- Verify everything works

---

## Expected HF Space URL

After deployment, your backend will be available at:
```
https://YOUR_USERNAME-phyai-rag-chatbot-backend.hf.space
```

**API Documentation:**
```
https://YOUR_USERNAME-phyai-rag-chatbot-backend.hf.space/docs
```

**Health Check:**
```
https://YOUR_USERNAME-phyai-rag-chatbot-backend.hf.space/health
```

---

## CORS Configuration

The backend is configured to accept requests from:

1. **Vercel Production:** `https://phyai-humanoid-textbook.vercel.app`
2. **Local Development:** `http://localhost:3000`, `http://localhost:5173`
3. **Additional URLs:** Add to `CORS_ORIGINS` environment variable

**Format:**
```
CORS_ORIGINS=https://phyai-humanoid-textbook.vercel.app,https://preview-url.vercel.app,http://localhost:3000
```

---

## Environment Variables Reference

### Required (8 variables)

| Variable | Description | Example |
|----------|-------------|---------|
| OPENROUTER_API_KEY | OpenRouter API key | sk-or-v1-xxx |
| OPENROUTER_MODEL | LLM model name | mistralai/devstral-2512:free |
| BASE_URL | OpenRouter base URL | https://openrouter.ai/api/v1 |
| QDRANT_URL | Qdrant cluster URL | https://xxx.gcp.cloud.qdrant.io:6333 |
| QDRANT_API_KEY | Qdrant API key | xxx |
| QDRANT_COLLECTION_NAME | Collection name | textbook_chunks |
| NEON_DATABASE_URL | PostgreSQL connection | postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require |
| CORS_ORIGINS | Allowed origins | https://phyai-humanoid-textbook.vercel.app,http://localhost:3000 |

### Optional (1 variable)

| Variable | Description | Example |
|----------|-------------|---------|
| FRONTEND_URL | Frontend URL (auto-added to CORS) | https://phyai-humanoid-textbook.vercel.app |

---

## Health Check Response

**Expected healthy response:**
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

**Degraded response (some services down):**
```json
{
  "status": "degraded",
  "dependencies": {
    "postgres": "down",
    "qdrant": "up",
    "openai": "assumed_up"
  }
}
```

---

## Troubleshooting Quick Reference

### CORS Errors
- Verify CORS_ORIGINS includes exact Vercel URL
- Check for typos (https:// vs http://)
- Restart Space after updating secrets

### Database Connection Failed
- Verify NEON_DATABASE_URL includes `?sslmode=require`
- Check Neon console for database status
- Ensure database exists and is accessible

### Qdrant Connection Failed
- Verify QDRANT_URL includes port `:6333`
- Check Qdrant Cloud console
- Ensure collection `textbook_chunks` exists (913 vectors)

### Build Timeout
- Check Logs tab in HF Space
- Ensure all dependencies are in requirements.txt
- CPU-only PyTorch is already configured

---

## Next Steps

1. **Test Locally (Optional but Recommended)**
   ```bash
   cd backend/rag-chatbot
   ./test-hf-docker.sh
   ```

2. **Deploy to HF Spaces**
   - Follow DEPLOYMENT_QUICK_START.md for fast deployment
   - Or HUGGINGFACE_DEPLOYMENT.md for comprehensive guide

3. **Update Frontend**
   - Add HF Space URL to Vercel environment variables
   - Redeploy frontend

4. **Test End-to-End**
   - Open frontend in browser
   - Test chat widget
   - Verify streaming responses work
   - Check citations appear

5. **Monitor**
   - Check HF Space Logs tab
   - Monitor health endpoint
   - Review Prometheus metrics at /metrics

---

## Support

**Documentation:**
- Comprehensive guide: HUGGINGFACE_DEPLOYMENT.md
- Quick start: DEPLOYMENT_QUICK_START.md
- HF Spaces README: README-HF.md

**Testing:**
- Local Docker test: ./test-hf-docker.sh
- Environment template: .env.hf-example

**Resources:**
- HF Spaces Docs: https://huggingface.co/docs/hub/spaces
- FastAPI Docs: https://fastapi.tiangolo.com/
- Qdrant Docs: https://qdrant.tech/documentation/
- Neon Docs: https://neon.tech/docs

---

## Deployment Checklist

### Pre-Deployment
- [ ] Local testing complete (./test-hf-docker.sh)
- [ ] All environment variables ready
- [ ] Neon database accessible
- [ ] Qdrant collection verified (913 vectors)
- [ ] OpenRouter API key working
- [ ] Vercel frontend URL noted

### HF Spaces Setup
- [ ] HF Space created (Docker SDK)
- [ ] Files uploaded/pushed
- [ ] All 8 secrets configured
- [ ] CORS_ORIGINS includes Vercel URL

### Verification
- [ ] Build logs show success
- [ ] Health endpoint returns "healthy"
- [ ] /docs accessible
- [ ] Chat endpoint tested
- [ ] Frontend connects successfully
- [ ] No CORS errors

### Post-Deployment
- [ ] Frontend environment updated
- [ ] Frontend redeployed
- [ ] End-to-end testing complete
- [ ] Documentation updated
- [ ] Team notified

---

**All files are ready for deployment!** 🚀

Choose your deployment path:
- **Fast:** DEPLOYMENT_QUICK_START.md (5 minutes)
- **Comprehensive:** HUGGINGFACE_DEPLOYMENT.md (detailed guide)
- **Test First:** ./test-hf-docker.sh (verify locally)
