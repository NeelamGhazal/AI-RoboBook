# fastapi-serverless

Convert FastAPI application to Vercel serverless functions.

## Purpose
Transform FastAPI backend into Vercel-compatible serverless functions for seamless deployment.

## Tasks
1. Create /api directory structure
2. Convert FastAPI routes to serverless handlers
3. Setup requirements.txt for Python dependencies
4. Configure CORS for frontend integration
5. Create serverless function wrappers
6. Setup RAG chatbot API endpoints

## Directory Structure
```
/api
  ├── index.py          # Main handler
  ├── chat.py           # Chatbot endpoints
  ├── requirements.txt  # Dependencies
  └── __init__.py
```

## Key Points
- Each API route becomes a separate serverless function
- Use FastAPI with Mangum adapter for serverless
- Configure proper response headers
- Handle async operations
- Setup database connections efficiently

## Dependencies
- fastapi
- mangum (for serverless adapter)
- uvicorn
- python-dotenv
- Database clients (psycopg2, qdrant-client)
- openai
- langchain (optional)

## Output
Production-ready FastAPI serverless functions in /api directory