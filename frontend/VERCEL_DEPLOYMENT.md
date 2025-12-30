# Vercel Deployment Guide - Docusaurus Frontend

This guide covers deploying the PhyAI Humanoid Textbook Docusaurus site to Vercel.

## Prerequisites

- Vercel account (free tier available)
- GitHub repository connected to Vercel
- Node.js 18+ (configured in vercel.json)

## Deployment Configuration

### vercel.json

The site is configured with:
- **Framework**: Docusaurus
- **Build Command**: `npm run build`
- **Output Directory**: `build/`
- **Node Version**: >=18.0

### Features Enabled

✅ **Performance Optimizations**
- Asset caching (1 year for immutable assets)
- Minification enabled
- Clean URLs

✅ **Security Headers**
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block

✅ **Routing**
- SPA fallback to index.html
- Trailing slash handling
- Clean URLs

## Deployment Methods

### Method 1: Automatic Deployment (Recommended)

1. **Connect Repository to Vercel**
   ```bash
   # Install Vercel CLI (optional)
   npm i -g vercel

   # Login to Vercel
   vercel login
   ```

2. **Import Project**
   - Go to https://vercel.com/new
   - Import your GitHub repository
   - Select `frontend/` as the root directory
   - Vercel will auto-detect Docusaurus configuration

3. **Configure Project**
   - **Framework Preset**: Docusaurus
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `build` (auto-detected)
   - **Install Command**: `npm install` (auto-detected)

4. **Deploy**
   - Click "Deploy"
   - Vercel will build and deploy automatically
   - Every push to main branch triggers a new deployment

### Method 2: Manual Deployment via CLI

```bash
# Navigate to frontend directory
cd frontend

# Deploy to Vercel
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? [Your account]
# - Link to existing project? No
# - Project name? phyai-humanoid-textbook
# - Directory? ./
# - Override settings? No

# Deploy to production
vercel --prod
```

## Backend Configuration

**Important**: The backend (FastAPI RAG chatbot) is deployed separately on **Hugging Face Spaces**, not Vercel.

### Update ChatWidget Configuration

After deploying the frontend, update the backend URL in the ChatWidget:

**File**: `src/components/ChatWidget/config.ts`

```typescript
export function getBackendUrl(): string {
  // Production: Hugging Face backend
  if (typeof window !== 'undefined' && window.location.hostname !== 'localhost') {
    return 'https://your-hf-space.hf.space'; // Replace with actual HF URL
  }

  // Development: Local backend
  return 'http://localhost:8000';
}
```

## Environment Variables

If you need environment variables (e.g., for API keys):

1. Go to Vercel Dashboard → Project Settings → Environment Variables
2. Add variables:
   - `NEXT_PUBLIC_BACKEND_URL` (if needed)
   - Any other public env vars

## Post-Deployment Checklist

- [ ] Frontend deployed successfully to Vercel
- [ ] Backend deployed to Hugging Face Spaces
- [ ] ChatWidget backend URL updated to point to HF backend
- [ ] CORS configured on backend to allow Vercel domain
- [ ] Test chatbot functionality on production site
- [ ] Verify all pages load correctly
- [ ] Check mobile responsiveness
- [ ] Verify search functionality works

## Deployment URLs

After deployment, you'll receive:
- **Production URL**: `https://phyai-humanoid-textbook.vercel.app`
- **Preview URLs**: Unique URL for each branch/PR

## Troubleshooting

### Build Fails

**Issue**: Build timeout or memory error

**Solution**:
```bash
# Locally test the build
npm run build

# If it works locally, increase Vercel build timeout
# (available in Pro plan or contact support)
```

### 404 Errors on Routes

**Issue**: Direct navigation to routes returns 404

**Solution**: Already configured in `vercel.json` with SPA fallback:
```json
"rewrites": [
  { "source": "/(.*)", "destination": "/index.html" }
]
```

### Assets Not Loading

**Issue**: CSS/JS files return 404

**Solution**: Ensure `outputDirectory` is set to `build` in `vercel.json`

## Monitoring

- **Analytics**: Available in Vercel Dashboard
- **Logs**: View build and runtime logs in Vercel
- **Performance**: Vercel provides Web Vitals monitoring

## Custom Domain (Optional)

1. Go to Project Settings → Domains
2. Add your custom domain
3. Configure DNS records as instructed
4. SSL certificate auto-generated

## Support

- **Vercel Docs**: https://vercel.com/docs
- **Docusaurus Deployment**: https://docusaurus.io/docs/deployment

---

**Note**: This configuration is optimized for Docusaurus static site deployment. The backend API runs separately on Hugging Face Spaces.
