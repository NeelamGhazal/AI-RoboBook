# Hugging Face Spaces Deployment Guide

**Step-by-step instructions to deploy the RAG Chatbot Backend to Hugging Face Spaces**

---

## Prerequisites

Before deploying, ensure you have:

1. **Hugging Face Account** - Sign up at https://huggingface.co/join
2. **Neon PostgreSQL Database** - Free tier at https://neon.tech/
3. **Qdrant Cloud Cluster** - Free tier at https://cloud.qdrant.io/
4. **OpenRouter API Key** - Free tier at https://openrouter.ai/keys
5. **Vercel Frontend URL** - Your deployed frontend URL

---

## Step 1: Create a New Hugging Face Space

1. **Go to Hugging Face Spaces**
   - Navigate to: https://huggingface.co/spaces
   - Click "Create new Space"

2. **Configure Space Settings**
   - **Owner:** Your username or organization
   - **Space name:** `phyai-rag-chatbot-backend` (or your preferred name)
   - **License:** MIT
   - **Select SDK:** Docker
   - **Space hardware:** CPU basic (free tier is sufficient)
   - **Visibility:** Public (or Private if preferred)

3. **Create Space**
   - Click "Create Space"
   - You'll be redirected to your new Space page

---

## Step 2: Prepare Your Repository Files

### Option A: Clone and Push to HF Spaces (Recommended)

1. **Clone your HF Space repository**
   ```bash
   git clone https://huggingface.co/spaces/YOUR_USERNAME/phyai-rag-chatbot-backend
   cd phyai-rag-chatbot-backend
   ```

2. **Copy backend files from your project**
   ```bash
   # From your project root
   cp -r backend/rag-chatbot/app ./app
   cp -r backend/rag-chatbot/scripts ./scripts
   cp backend/rag-chatbot/requirements.txt .
   cp backend/rag-chatbot/Dockerfile.hf ./Dockerfile
   cp backend/rag-chatbot/README-HF.md ./README.md
   ```

3. **Verify file structure**
   ```
   phyai-rag-chatbot-backend/
   ├── app/
   │   ├── main.py
   │   ├── config.py
   │   ├── api/
   │   ├── clients/
   │   ├── services/
   │   ├── models/
   │   └── utils/
   ├── scripts/
   ├── requirements.txt
   ├── Dockerfile
   └── README.md
   ```

4. **Commit and push to HF Spaces**
   ```bash
   git add .
   git commit -m "Initial deployment: FastAPI RAG chatbot backend"
   git push
   ```

### Option B: Manual File Upload

1. Go to your Space page on Hugging Face
2. Click "Files" tab
3. Upload files manually:
   - Upload `Dockerfile.hf` as `Dockerfile`
   - Upload `README-HF.md` as `README.md`
   - Upload `requirements.txt`
   - Upload entire `app/` directory
   - Upload entire `scripts/` directory

---

## Step 3: Configure Environment Secrets

1. **Navigate to Space Settings**
   - Go to your Space page
   - Click "Settings" tab
   - Scroll down to "Repository secrets"

2. **Add Required Secrets** (one by one)

   **Click "Add a new secret" for each:**

   ### OpenRouter Configuration
   ```
   Name: OPENROUTER_API_KEY
   Value: sk-or-v1-your-actual-api-key-here
   ```

   ```
   Name: OPENROUTER_MODEL
   Value: mistralai/devstral-2512:free
   ```

   ```
   Name: BASE_URL
   Value: https://openrouter.ai/api/v1
   ```

   ### Qdrant Configuration
   ```
   Name: QDRANT_URL
   Value: https://your-cluster-id.gcp.cloud.qdrant.io:6333
   ```

   ```
   Name: QDRANT_API_KEY
   Value: your-qdrant-api-key-here
   ```

   ```
   Name: QDRANT_COLLECTION_NAME
   Value: textbook_chunks
   ```

   ### Neon PostgreSQL Configuration
   ```
   Name: NEON_DATABASE_URL
   Value: postgresql://user:password@ep-xxx.region.neon.tech/dbname?sslmode=require
   ```

   ### CORS Configuration
   ```
   Name: CORS_ORIGINS
   Value: https://phyai-humanoid-textbook.vercel.app,http://localhost:3000,http://localhost:5173
   ```

   **IMPORTANT:** Replace with your actual Vercel URL!

   ### Optional Secrets
   ```
   Name: FRONTEND_URL
   Value: https://phyai-humanoid-textbook.vercel.app
   ```

3. **Verify Secrets**
   - Ensure all 8-9 secrets are added
   - Secret names must match exactly (case-sensitive)
   - Values should not have leading/trailing spaces

---

## Step 4: Deploy and Monitor

1. **Trigger Deployment**
   - After pushing code or uploading files, HF Spaces automatically builds
   - Go to "Logs" tab to monitor build progress

2. **Monitor Build Logs**

   **Expected log sequence:**
   ```
   Building Docker image...
   Installing PyTorch CPU...
   Installing sentence-transformers...
   Installing requirements...
   Copying application code...
   Starting uvicorn...
   INFO:     Started server process
   INFO:     Waiting for application startup.
   INFO:     application_starting
   INFO:     database_connected
   INFO:     local_embedding_client_ready
   INFO:     qdrant_client_ready
   INFO:     agents_sdk_configured
   INFO:     application_started
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://0.0.0.0:7860
   ```

3. **Common Build Issues**

   **Issue:** "Missing environment variable"
   ```
   ERROR: ValidationError: OPENROUTER_API_KEY field required
   ```
   **Solution:** Add the missing secret in Settings > Repository Secrets

   **Issue:** "Port already in use"
   ```
   ERROR: [Errno 98] Address already in use
   ```
   **Solution:** This shouldn't happen in HF Spaces. Restart the Space.

   **Issue:** "Database connection failed"
   ```
   ERROR: health_check_postgres_failed
   ```
   **Solution:** Verify NEON_DATABASE_URL format and database status

---

## Step 5: Verify Deployment

### 5.1 Health Check

Your Space URL will be: `https://YOUR_USERNAME-phyai-rag-chatbot-backend.hf.space`

**Test health endpoint:**
```bash
curl https://YOUR_USERNAME-phyai-rag-chatbot-backend.hf.space/health
```

**Expected response:**
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

### 5.2 API Documentation

**Open Swagger UI:**
```
https://YOUR_USERNAME-phyai-rag-chatbot-backend.hf.space/docs
```

This provides interactive API documentation.

### 5.3 Test Chat Endpoint

```bash
curl -X POST "https://YOUR_USERNAME-phyai-rag-chatbot-backend.hf.space/api/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-123",
    "question": "What is ROS 2?",
    "selected_text": ""
  }'
```

**Expected:** Streaming SSE response with answer and citations

---

## Step 6: Update Frontend Configuration

### Update Vercel Frontend to Use HF Spaces Backend

1. **Get your HF Space URL**
   ```
   https://YOUR_USERNAME-phyai-rag-chatbot-backend.hf.space
   ```

2. **Update frontend environment variables**

   **In Vercel Dashboard:**
   - Go to your Vercel project
   - Settings > Environment Variables
   - Add or update:
     ```
     VITE_API_BASE_URL=https://YOUR_USERNAME-phyai-rag-chatbot-backend.hf.space
     ```

3. **Or update frontend config file**

   ```typescript
   // frontend/src/components/ChatWidget/config.ts
   export const getApiBaseUrl = (): string => {
     // Production: Use HF Spaces backend
     if (import.meta.env.PROD) {
       return 'https://YOUR_USERNAME-phyai-rag-chatbot-backend.hf.space';
     }
     // Development: Use local backend
     return 'http://localhost:8000';
   };
   ```

4. **Redeploy frontend**
   ```bash
   git add .
   git commit -m "Update API endpoint to HF Spaces"
   git push
   ```

---

## Step 7: Update CORS for New Frontend URLs

If you add new Vercel preview URLs or change domains:

1. **Update CORS_ORIGINS secret in HF Spaces**
   - Go to Settings > Repository Secrets
   - Edit `CORS_ORIGINS`
   - Add new URLs (comma-separated):
     ```
     https://phyai-humanoid-textbook.vercel.app,https://phyai-humanoid-textbook-git-main.vercel.app,http://localhost:3000
     ```

2. **Restart Space**
   - Go to Space page
   - Click "Factory reboot" in Settings
   - Wait for Space to restart (check Logs tab)

---

## Troubleshooting Guide

### Issue: CORS Errors in Browser Console

**Symptoms:**
```
Access to fetch at 'https://xxx.hf.space/api/v1/chat/stream' from origin 'https://xxx.vercel.app' has been blocked by CORS policy
```

**Solution:**
1. Verify `CORS_ORIGINS` secret includes your exact Vercel URL
2. Check for typos (https:// vs http://, trailing slashes)
3. Restart Space after updating secrets
4. Test with curl first to isolate CORS issue

### Issue: Database Connection Failed

**Symptoms:**
- Health check shows `"postgres": "down"`
- Logs show: `health_check_postgres_failed`

**Solution:**
1. Verify `NEON_DATABASE_URL` format:
   ```
   postgresql://user:password@ep-xxx.region.neon.tech/dbname?sslmode=require
   ```
2. Ensure `?sslmode=require` is included
3. Check Neon console for database status
4. Verify database exists and user has permissions

### Issue: Qdrant Connection Failed

**Symptoms:**
- Health check shows `"qdrant": "down"`
- Logs show: `health_check_qdrant_failed`

**Solution:**
1. Verify `QDRANT_URL` includes port `:6333`
2. Check Qdrant Cloud console for cluster status
3. Ensure `textbook_chunks` collection exists
4. Verify API key is correct (no extra spaces)

### Issue: OpenRouter API Errors

**Symptoms:**
- Chat requests fail with 401 or 403
- Logs show: `OpenRouter authentication failed`

**Solution:**
1. Verify `OPENROUTER_API_KEY` is correct
2. Check OpenRouter dashboard for key status
3. Ensure free tier model is available: `mistralai/devstral-2512:free`
4. Check OpenRouter usage limits

### Issue: Space Build Timeout

**Symptoms:**
- Build hangs during PyTorch installation
- Build exceeds time limit

**Solution:**
1. Use CPU-only PyTorch (already configured in Dockerfile.hf)
2. Pre-download sentence-transformers model (already configured)
3. Consider using a smaller embedding model if needed
4. Ensure hardware tier is CPU basic (not sleeping)

### Issue: Streaming Not Working

**Symptoms:**
- Chat returns empty response
- SSE connection closes immediately

**Solution:**
1. Check browser console for JavaScript errors
2. Verify frontend is using EventSource correctly
3. Test endpoint with curl to isolate frontend issue
4. Check nginx/proxy settings if using custom domain

---

## Performance Optimization

### Cold Start Optimization

HF Spaces may sleep after 48 hours of inactivity (free tier). To improve cold starts:

1. **Keep Space Warm (Paid Tier)**
   - Upgrade to persistent hardware
   - Prevents auto-sleeping

2. **Optimize Docker Image**
   - Already using CPU-only PyTorch (smaller image)
   - Multi-stage build minimizes layers
   - Pre-downloaded models included

3. **Frontend Loading State**
   - Show "Waking up backend..." message
   - First request may take 30-60 seconds on cold start
   - Subsequent requests are fast (<2 seconds)

### Resource Monitoring

**Check Space metrics:**
1. Go to Space page
2. Click "Metrics" tab (if available)
3. Monitor:
   - CPU usage
   - Memory usage
   - Request latency
   - Error rate

**Use Prometheus endpoint:**
```bash
curl https://YOUR_USERNAME-phyai-rag-chatbot-backend.hf.space/metrics
```

---

## Security Best Practices

✅ **Use Repository Secrets** - Never commit API keys to git
✅ **Restrict CORS Origins** - Only allow specific frontend domains
✅ **Enable Rate Limiting** - Default 10 requests/minute per IP
✅ **Use SSL Connections** - Database uses `sslmode=require`
✅ **Non-Root Container** - Docker runs as unprivileged user
✅ **Monitor Logs** - Check for suspicious activity
✅ **Rotate Keys Regularly** - Update API keys periodically

---

## Maintenance

### Updating the Deployment

1. **Make changes to code locally**
2. **Test locally**
   ```bash
   docker build -f Dockerfile.hf -t rag-chatbot-test .
   docker run -p 7860:7860 --env-file .env rag-chatbot-test
   ```
3. **Commit and push to HF Space**
   ```bash
   git add .
   git commit -m "Update: description of changes"
   git push
   ```
4. **Monitor deployment logs**
5. **Verify health endpoint**

### Monitoring Checklist

**Daily:**
- [ ] Check Space status (running/building/sleeping)
- [ ] Verify health endpoint responds

**Weekly:**
- [ ] Review logs for errors
- [ ] Check Prometheus metrics
- [ ] Verify database connections
- [ ] Test chat endpoint functionality

**Monthly:**
- [ ] Review resource usage
- [ ] Update dependencies (if needed)
- [ ] Rotate API keys
- [ ] Check for security updates

---

## Cost Breakdown

### Free Tier Deployment

| Service | Plan | Cost | Notes |
|---------|------|------|-------|
| HF Spaces | CPU Basic | FREE | May sleep after 48h inactivity |
| Neon PostgreSQL | Free Tier | FREE | 500MB storage, 1 project |
| Qdrant Cloud | Free Tier | FREE | 1GB storage, 1 cluster |
| OpenRouter | Free Tier | FREE | Limited daily requests |
| Sentence-Transformers | Local | FREE | Runs in container |

**Total Cost:** $0/month

### Upgrading for Production

**HF Spaces Persistent Hardware:**
- CPU Persistent: ~$0.02/hour (~$15/month)
- Prevents sleeping, always available

**Neon PostgreSQL Pro:**
- $19/month: 10GB storage, autoscaling

**Qdrant Cloud Paid:**
- $25/month: 5GB storage, better performance

**OpenRouter Paid:**
- Pay-per-request pricing
- Better models available

---

## Next Steps

1. **Test thoroughly** - Verify all endpoints work
2. **Update frontend** - Point to HF Spaces URL
3. **Monitor performance** - Check logs and metrics
4. **Set up alerts** - Use UptimeRobot or similar
5. **Document API** - Share Space URL with team
6. **Consider upgrades** - If traffic increases

---

## Support Resources

- **HF Spaces Docs:** https://huggingface.co/docs/hub/spaces
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Qdrant Docs:** https://qdrant.tech/documentation/
- **Neon Docs:** https://neon.tech/docs
- **OpenRouter Docs:** https://openrouter.ai/docs

---

## Deployment Checklist

### Pre-Deployment
- [ ] Neon PostgreSQL database created and accessible
- [ ] Qdrant Cloud cluster created with `textbook_chunks` collection (913 vectors)
- [ ] OpenRouter API key obtained
- [ ] Vercel frontend URL noted
- [ ] All credentials ready

### HF Spaces Setup
- [ ] HF Space created (Docker SDK)
- [ ] Repository files uploaded/pushed
- [ ] All 8-9 secrets configured
- [ ] CORS_ORIGINS includes Vercel URL

### Verification
- [ ] Build logs show successful deployment
- [ ] Health endpoint returns "healthy"
- [ ] Swagger UI accessible at /docs
- [ ] Chat endpoint responds to test request
- [ ] Frontend can connect to backend
- [ ] CORS working (no console errors)

### Post-Deployment
- [ ] Frontend environment variables updated
- [ ] Frontend redeployed
- [ ] End-to-end testing complete
- [ ] Documentation updated with Space URL
- [ ] Team notified of new backend URL

---

**Deployment Complete!** Your RAG chatbot backend is now live on Hugging Face Spaces. 🚀
