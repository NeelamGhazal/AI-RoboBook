# Quick Start: Deploy to Hugging Face Spaces (5 Minutes)

**Fast-track deployment guide for experienced developers**

---

## 1. Create HF Space (1 min)

```
https://huggingface.co/spaces → Create new Space
- Name: phyai-rag-chatbot-backend
- SDK: Docker
- Hardware: CPU basic (free)
- Visibility: Public
```

---

## 2. Push Code (2 min)

```bash
# Clone HF Space repo
git clone https://huggingface.co/spaces/YOUR_USERNAME/phyai-rag-chatbot-backend
cd phyai-rag-chatbot-backend

# Copy backend files
cp -r ../phyai-humanoid-textbook/backend/rag-chatbot/app .
cp -r ../phyai-humanoid-textbook/backend/rag-chatbot/scripts .
cp ../phyai-humanoid-textbook/backend/rag-chatbot/requirements.txt .
cp ../phyai-humanoid-textbook/backend/rag-chatbot/Dockerfile.hf Dockerfile
cp ../phyai-humanoid-textbook/backend/rag-chatbot/README-HF.md README.md

# Push to HF
git add .
git commit -m "Initial deployment"
git push
```

---

## 3. Configure Secrets (2 min)

**Settings > Repository Secrets > Add secrets:**

```bash
# Required (8 secrets)
OPENROUTER_API_KEY=sk-or-v1-xxx
OPENROUTER_MODEL=mistralai/devstral-2512:free
BASE_URL=https://openrouter.ai/api/v1
QDRANT_URL=https://xxx.gcp.cloud.qdrant.io:6333
QDRANT_API_KEY=xxx
QDRANT_COLLECTION_NAME=textbook_chunks
NEON_DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require
CORS_ORIGINS=https://phyai-humanoid-textbook.vercel.app,http://localhost:3000

# Optional (1 secret)
FRONTEND_URL=https://phyai-humanoid-textbook.vercel.app
```

---

## 4. Verify Deployment (<1 min)

**Check build logs:**
```
Logs tab → Wait for "Uvicorn running on http://0.0.0.0:7860"
```

**Test health:**
```bash
curl https://YOUR_USERNAME-phyai-rag-chatbot-backend.hf.space/health
```

**Expected:**
```json
{"status": "healthy", "dependencies": {"postgres": "up", "qdrant": "up"}}
```

---

## 5. Update Frontend

**Vercel Environment Variable:**
```
VITE_API_BASE_URL=https://YOUR_USERNAME-phyai-rag-chatbot-backend.hf.space
```

**Or update config file:**
```typescript
// frontend/src/components/ChatWidget/config.ts
return 'https://YOUR_USERNAME-phyai-rag-chatbot-backend.hf.space';
```

**Redeploy frontend:**
```bash
git commit -am "Update API endpoint"
git push
```

---

## Done! 🚀

**Your backend is live at:**
```
https://YOUR_USERNAME-phyai-rag-chatbot-backend.hf.space
```

**API Docs:**
```
https://YOUR_USERNAME-phyai-rag-chatbot-backend.hf.space/docs
```

---

## Troubleshooting

**Build fails?**
- Check Logs tab for errors
- Verify all 8 secrets are set correctly

**CORS errors?**
- Ensure CORS_ORIGINS includes your Vercel URL
- Restart Space after updating secrets

**Database/Qdrant down?**
- Verify connection strings in secrets
- Check Neon/Qdrant console for service status

---

**Full documentation:** See HUGGINGFACE_DEPLOYMENT.md
