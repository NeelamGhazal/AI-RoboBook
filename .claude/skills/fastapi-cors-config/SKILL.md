# fastapi-cors-config

Configure CORS for FastAPI to allow Vercel frontend connections.

## Purpose
Setup Cross-Origin Resource Sharing (CORS) to enable secure communication between Vercel frontend and Hugging Face backend.

## Tasks
1. Configure CORS middleware in FastAPI
2. Allow Vercel production and preview URLs
3. Setup allowed methods and headers
4. Configure credentials handling
5. Test CORS configuration

## CORS Configuration Code
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# CORS Configuration
cors_origins = os.getenv("CORS_ORIGINS", "")
if cors_origins:
    origins = cors_origins.split(",")
else:
    origins = [
        "http://localhost:3000",
        "https://phyai-humanoid-textbook.vercel.app"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Allowed Origins Configuration
Must include:
- Local development: `http://localhost:3000`
- Vercel production: `https://phyai-humanoid-textbook.vercel.app`
- Vercel preview URLs: `https://phyai-humanoid-textbook-*.vercel.app` (use pattern matching)

## Security Best Practices
- Use environment variables for origins list
- Never use `allow_origins=["*"]` in production
- Enable `allow_credentials` only if using cookies/auth
- Validate and sanitize all headers
- Log CORS rejections for debugging

## Testing CORS
```bash
# Test OPTIONS preflight
curl -H "Origin: https://phyai-humanoid-textbook.vercel.app" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS https://your-space.hf.space/api/chat

# Expected response headers:
# Access-Control-Allow-Origin: https://phyai-humanoid-textbook.vercel.app
# Access-Control-Allow-Methods: POST, GET, OPTIONS
# Access-Control-Allow-Headers: Content-Type
```

## Common CORS Issues
- Missing OPTIONS handler: FastAPI handles automatically
- Wrong origin format: Must include protocol (https://)
- Credentials without explicit origin: Can't use * with credentials
- Browser caching: Use Ctrl+Shift+R to hard refresh

## Output
Properly configured CORS middleware allowing secure Vercel frontend access