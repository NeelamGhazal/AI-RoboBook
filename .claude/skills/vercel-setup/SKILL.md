# vercel-setup

Handle Vercel deployment configuration and setup.

## Purpose
Create and configure Vercel deployment settings for full-stack applications including Docusaurus static sites and FastAPI serverless backends.

## Tasks
1. Generate vercel.json configuration file
2. Setup environment variables structure
3. Configure build commands and output directories
4. Setup serverless function configuration
5. Configure routing for static and API routes
6. Handle framework-specific presets (Docusaurus, FastAPI)

## Key Configurations

### vercel.json Structure
- buildCommand: Build script for the project
- outputDirectory: Where build files are located
- framework: Framework preset (docusaurus, custom)
- functions: Serverless function configuration
- rewrites: API routing rules
- env: Environment variables

### Best Practices
- Use environment variables for sensitive data
- Configure proper CORS headers
- Set appropriate Node.js version
- Optimize build settings
- Setup preview deployments

## Frontend Config Verification Steps (CRITICAL)

### Pre-Build Verification Checklist

**MANDATORY: Execute these steps BEFORE every build**

#### 1. Verify Backend URL Configuration
```bash
# Navigate to frontend directory
cd frontend

# Check config.ts for production backend URL
cat src/components/ChatWidget/config.ts | grep "return '"

# Expected for PRODUCTION:
return 'https://your-username-your-space-name.hf.space';

# NOT this (localhost):
return 'http://localhost:8000';  # ✗ WRONG for production

# If showing localhost, edit config.ts:
function getApiUrl(): string {
  if (typeof window !== 'undefined' && (window as any).CHAT_API_URL) {
    return (window as any).CHAT_API_URL;
  }
  // Production: Hugging Face Spaces backend
  return 'https://your-username-your-space-name.hf.space';  // ✓ CORRECT
}
```

#### 2. Clean Build Cache (ALWAYS)
```bash
# Remove ALL cache directories before building
rm -rf .docusaurus build node_modules/.cache

# Verify directories are deleted
ls -la | grep -E "(\.docusaurus|build|node_modules/\.cache)"
# Expected: NO OUTPUT (directories should be gone)
```

#### 3. Build Docusaurus Site
```bash
# Run build command
npm run build

# Wait for successful completion:
# ✓ Client bundle compiled successfully
# ✓ Server bundle compiled successfully
# Success! Generated static files in "build"
```

## Build Validation Process

### Critical Validation Checks

**Check 1: No Localhost References (CRITICAL)**
```bash
# Search for localhost in build output
grep -r "localhost:8000" build/

# Expected: EMPTY OUTPUT (no matches)
# If you see matches: STOP, fix config.ts, clean, rebuild

# Example of FAILED validation:
build/assets/js/4760.bbefef89.js:  apiUrl:"http://localhost:8000"
# ↑ This means you need to fix config.ts and rebuild
```

**Check 2: Production URL Present**
```bash
# Verify production backend URL is in build
grep -r "hf.space" build/ | head -5

# Expected: Several matches showing HF Spaces URL
# Example of SUCCESS:
build/assets/js/4760.bbefef89.js:  apiUrl:"https://username-space.hf.space"
```

**Check 3: Chat Widget Bundle Exists**
```bash
# Verify chat widget was included in build
find build/ -name "*ChatWidget*" -o -name "*chat*" | head -10

# Expected: Multiple JavaScript and CSS files
```

**Check 4: Index File Valid**
```bash
# Check main index file
cat build/index.html | grep -i "docusaurus"

# Expected: Docusaurus meta tags present
```

## Deployment Commands

### Standard Deployment
```bash
# Standard production deployment
vercel --prod

# WAIT 2-5 minutes for deployment to complete
```

### Force Deploy (Bypass Cache)
```bash
# Use when Vercel cache is stale or showing old build
vercel --prod --force

# This forces:
# 1. Fresh git clone
# 2. Fresh npm install
# 3. Fresh build from source
# 4. Skip cache entirely

# Use when:
# - Previous deployment shows localhost URL (not fixed)
# - Build succeeds but deployment shows old version
# - Vercel cache is corrupted
```

### Deployment with Environment Override
```bash
# Deploy with custom backend URL (testing)
CHAT_API_URL=https://test-backend.hf.space vercel --prod
```

## Post-Deploy Testing

### Browser Console Checks (CRITICAL)

**Step 1: Open Deployment in Incognito**
```bash
# Use incognito/private window to avoid cached old version
# Navigate to: https://your-site.vercel.app
```

**Step 2: Check Console for Errors**
```javascript
// Open DevTools (F12) → Console tab
// Look for these ERRORS (indicates failure):

✗ "ERR_CONNECTION_REFUSED"
  → Means localhost:8000 in build (rebuild needed)

✗ "net::ERR_BLOCKED_BY_CLIENT"
  → Means localhost:8000 in build (rebuild needed)

✗ "Failed to load resource: net::ERR_NAME_NOT_RESOLVED"
  → Wrong backend URL in config

// Look for these SUCCESS indicators:
✓ No connection errors
✓ "EventSource connected" or "WebSocket connected"
✓ Requests to HF Spaces URL (not localhost)
```

**Step 3: Network Tab Verification**
```javascript
// DevTools → Network tab
// Click chat widget → Send test message
// Inspect the request URL:

✓ https://your-username-your-space-name.hf.space/api/v1/chat/stream
  → CORRECT (production backend)

✗ http://localhost:8000/api/v1/chat/stream
  → WRONG (old build with localhost)
```

**Step 4: Test Chat Functionality**
```bash
# User actions to test:
1. Click chat widget icon (bottom right)
   ✓ Panel opens smoothly
2. Type message: "What is ROS 2?"
3. Click send
   ✓ Loading indicator appears
   ✓ Response streams in token by token
   ✓ NO empty message box before streaming starts
   ✓ Citations appear after response
4. Check console
   ✓ No errors
   ✓ Requests go to HF Spaces (not localhost)
```

### Curl Verification
```bash
# Test homepage loads
curl -I https://your-site.vercel.app
# Expected: HTTP/2 200

# Check for production backend URL in JavaScript
curl https://your-site.vercel.app/assets/js/runtime~main.*.js | grep -o "hf.space"
# Expected: "hf.space" found

# Verify NO localhost references
curl https://your-site.vercel.app/assets/js/*.js | grep -o "localhost:8000"
# Expected: EMPTY (no matches)
```

## Common Issues & Solutions

### Issue 1: Deployment Shows Old Localhost Build

**Symptoms:**
- Vercel deployment succeeds
- Site loads but chat doesn't connect
- Console shows ERR_CONNECTION_REFUSED to localhost:8000
- Network tab shows requests to localhost

**Root Cause:**
Vercel used cached build with old localhost URL

**Solution:**
```bash
# 1. Verify config.ts has production URL (NOT localhost)
cat frontend/src/components/ChatWidget/config.ts | grep "return '"

# 2. If localhost found, UPDATE to production HF Spaces URL

# 3. Clean build cache completely
cd frontend
rm -rf .docusaurus build node_modules/.cache

# 4. Rebuild from scratch
npm run build

# 5. Validate build (NO localhost)
grep -r "localhost:8000" build/
# MUST BE EMPTY

# 6. Force deploy to bypass Vercel cache
vercel --prod --force

# 7. Wait 2-3 minutes, test in incognito window
```

### Issue 2: Widget Visible But Not Connecting

**Symptoms:**
- Chat widget appears on page
- Click icon, panel opens
- Send message → spinner never stops
- No response appears

**Root Cause:**
Backend URL misconfigured or backend not running

**Solution:**
```bash
# 1. Test backend health directly
curl https://your-username-your-space-name.hf.space/health
# Expected: {"status": "healthy"}

# If backend is down:
# - Check HF Spaces is running
# - Wait 8-10 min if just deployed

# 2. Check frontend is using correct backend URL
# In browser DevTools → Network tab
# Look at request URL when sending message
# Should be: https://...hf.space/api/v1/chat/stream
# NOT: http://localhost:8000/...

# 3. If wrong URL, rebuild with correct config
```

### Issue 3: Empty Response Box Appears Before Streaming

**Symptoms:**
- Empty assistant message box flashes
- Then content streams into it
- Visual flicker/poor UX

**Root Cause:**
Frontend creates message object optimistically before first token

**Solution:**
See vercel-deployer agent documentation for complete fix in ChatWidget.tsx handleSendMessage function. Key change: Only create assistant message on first token arrival, not before.

### Issue 4: CORS Errors in Console

**Symptoms:**
- Console shows: "Access to fetch blocked by CORS policy"
- Backend is running and healthy
- Frontend deployment is correct

**Root Cause:**
Backend CORS_ORIGINS doesn't include Vercel production domain

**Solution:**
```bash
# 1. Check backend CORS configuration
# Go to HF Space Settings → Variables
# Verify CORS_ORIGINS includes:
CORS_ORIGINS=http://localhost:3000,https://your-site.vercel.app

# 2. If missing, add Vercel domain and rebuild HF Space
# (Rebuild takes 8-10 minutes)

# 3. Test CORS after rebuild:
curl -X OPTIONS https://your-username-your-space-name.hf.space/api/v1/chat \
  -H "Origin: https://your-site.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -v
# Expected: access-control-allow-origin header in response
```

## Deployment Timing Expectations

- **Clean Build**: 1-3 minutes (Docusaurus compilation)
- **Vercel Upload**: 30-60 seconds
- **Edge Propagation**: 2-3 minutes (CDN distribution)
- **Total Time**: 5-8 minutes from build to live site
- **Force Deploy**: Add 1-2 minutes (fresh build)

## Complete Deployment Workflow

### Phase 1: Pre-Deployment
```bash
1. cd frontend
2. Verify config.ts has production URL (NOT localhost)
3. rm -rf .docusaurus build node_modules/.cache
4. npm run build
5. grep -r "localhost:8000" build/ (MUST BE EMPTY)
```

### Phase 2: Deploy
```bash
6. vercel --prod (or vercel --prod --force if cache is stale)
7. Copy deployment URL from output
```

### Phase 3: Verification
```bash
8. Wait 2-3 minutes for CDN propagation
9. Open in incognito: https://your-site.vercel.app
10. Check console (no localhost errors)
11. Check network tab (requests to HF Spaces)
12. Test chat widget functionality
```

### Phase 4: Validation Checklist
```bash
✓ Homepage loads
✓ Chat widget visible
✓ Click widget → panel opens
✓ Send message → streams response
✓ No empty box before streaming
✓ Citations appear
✓ Console shows NO errors
✓ Network tab shows HF Spaces URL (NOT localhost)
```

## Output
Ready-to-use vercel.json and deployment configuration files with comprehensive build validation and testing procedures