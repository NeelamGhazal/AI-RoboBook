"""
FastAPI main application for RAG Chatbot Backend.
Includes lifespan management, middleware, and API routing.
"""
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
from app.clients.db_client import db_client
from app.clients.gemini_client import gemini_client
from app.clients.local_embedding_client import local_embedding_client
from app.clients.qdrant_client import qdrant_client
from app.config import settings
from app.utils.logging import get_logger
from app.utils.metrics import CONCURRENT_REQUESTS, ERROR_COUNTER, REQUEST_DURATION
import os
import uvicorn

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown.
    Initializes database pool and external clients.
    """
    # Startup
    logger.info("application_starting")
    try:
        await db_client.connect()
        logger.info("database_connected")

        await local_embedding_client.initialize()
        logger.info("local_embedding_client_ready")

        await gemini_client.initialize()
        logger.info("gemini_client_ready")

        await qdrant_client.initialize()
        logger.info("qdrant_client_ready")

        logger.info("application_started", environment="production")
    except Exception as e:
        logger.error("application_startup_failed", error=str(e))
        raise

    yield

    # Shutdown
    logger.info("application_shutting_down")
    try:
        await qdrant_client.close()
        await local_embedding_client.close()
        await gemini_client.close()
        await db_client.disconnect()
        logger.info("application_shutdown_complete")
    except Exception as e:
        logger.error("application_shutdown_error", error=str(e))

# Create FastAPI application
app = FastAPI(
    title="RAG Chatbot Backend API",
    description="Intelligent Q&A System for Physical AI & Humanoid Robotics Textbook",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request tracking middleware
@app.middleware("http")
async def track_requests(request: Request, call_next):
    """Track concurrent requests and latency."""
    CONCURRENT_REQUESTS.inc()
    import time
    start_time = time.time()
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        REQUEST_DURATION.labels(endpoint=request.url.path, stage="total").observe(duration)
        logger.info(
            "request_complete",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration * 1000, 2),
        )
        return response
    except Exception as e:
        ERROR_COUNTER.labels(error_type=type(e).__name__).inc()
        logger.error(
            "request_failed",
            method=request.method,
            path=request.url.path,
            error=str(e),
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_error",
                "message": "An internal error occurred",
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
    finally:
        CONCURRENT_REQUESTS.dec()

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "RAG Chatbot Backend API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    status = "healthy"
    dependencies = {}
    try:
        try:
            await db_client.fetchval("SELECT 1")
            dependencies["postgres"] = "up"
        except Exception as e:
            dependencies["postgres"] = "down"
            status = "degraded"
            logger.error("health_check_postgres_failed", error=str(e))

        try:
            exists = await qdrant_client.collection_exists()
            dependencies["qdrant"] = "up" if exists else "down"
            if not exists:
                status = "degraded"
        except Exception as e:
            dependencies["qdrant"] = "down"
            status = "degraded"
            logger.error("health_check_qdrant_failed", error=str(e))

        dependencies["openai"] = "assumed_up"

        return {
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "dependencies": dependencies,
            "version": "1.0.0",
        }
    except Exception as e:
        logger.error("health_check_failed", error=str(e))
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
            },
        )

# Import and register routers
print("[Backend] Loading routers...")
from app.api.v1 import sessions, chat_minimal

app.include_router(sessions.router)
print("[Backend] ✓ Sessions router registered")

app.include_router(chat_minimal.router, prefix="/api/v1/chat", tags=["chat"])
print("[Backend] ✓ Minimal chat router registered: /api/v1/chat")

print("[Backend] Available endpoints:")
print("[Backend] - POST /api/v1/chat/stream")
print("[Backend] - GET /api/v1/chat/health")
print("[Backend] - GET /api/v1/chat/test")

print("\n[Backend] ===== Registered Routes =====")
for route in app.routes:
    if hasattr(route, 'methods') and hasattr(route, 'path'):
        methods = ', '.join(sorted(route.methods))
        print(f"[Backend] {methods:20s} {route.path}")
print("[Backend] ===================================\n")

# Mount Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# =============== RAILWAY-FRIENDLY STARTUP BLOCK ===============
if __name__ == "__main__":
    # Railway automatically sets PORT env variable
    port = int(os.environ.get("PORT", 8000))  # fallback 8000 for local dev
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
    )
