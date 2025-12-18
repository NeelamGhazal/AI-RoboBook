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
        # Initialize database connection pool
        await db_client.connect()
        logger.info("database_connected")

        # Initialize local embedding client (no API key needed!)
        await local_embedding_client.initialize()
        logger.info("local_embedding_client_ready")

        # Initialize Gemini client (for text generation only)
        await gemini_client.initialize()
        logger.info("gemini_client_ready")

        # Initialize Qdrant client
        await qdrant_client.initialize()
        logger.info("qdrant_client_ready")

        logger.info("application_started", environment="development")

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

        # Record request duration
        REQUEST_DURATION.labels(
            endpoint=request.url.path, stage="total"
        ).observe(duration)

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
    """Root endpoint with API information."""
    return {
        "name": "RAG Chatbot Backend API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


# Health check endpoint (basic implementation for now)
@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    Verifies connectivity to all dependencies.
    """
    status = "healthy"
    dependencies = {}

    try:
        # Check Postgres
        try:
            await db_client.fetchval("SELECT 1")
            dependencies["postgres"] = "up"
        except Exception as e:
            dependencies["postgres"] = "down"
            status = "degraded"
            logger.error("health_check_postgres_failed", error=str(e))

        # Check Qdrant
        try:
            exists = await qdrant_client.collection_exists()
            dependencies["qdrant"] = "up" if exists else "down"
            if not exists:
                status = "degraded"
        except Exception as e:
            dependencies["qdrant"] = "down"
            status = "degraded"
            logger.error("health_check_qdrant_failed", error=str(e))

        # OpenAI check skipped (would count against quota)
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


# Include API routers BEFORE mounting metrics
print("[Backend] Loading routers...")

try:
    from app.api.v1 import sessions
    print("[Backend] ✓ Sessions router imported successfully")
except Exception as e:
    print(f"[Backend] ✗ Failed to import sessions router: {e}")
    raise

try:
    from app.api.v1 import chat_minimal
    print("[Backend] ✓ Minimal chat router imported successfully")
except Exception as e:
    print(f"[Backend] ✗ Failed to import minimal chat router: {e}")
    import traceback
    traceback.print_exc()
    raise

app.include_router(sessions.router)
print("[Backend] ✓ Sessions router registered: /api/v1/sessions")

# Register minimal chat router with /api/v1/chat prefix
app.include_router(chat_minimal.router, prefix="/api/v1/chat", tags=["chat"])
print("[Backend] ✓ Minimal chat router registered: /api/v1/chat (includes /stream endpoint)")
print("[Backend] Available endpoints:")
print("[Backend]   - POST   /api/v1/chat/stream")
print("[Backend]   - GET    /api/v1/chat/health")
print("[Backend]   - GET    /api/v1/chat/test")

# Log all registered routes for debugging
print("\n[Backend] ===== Registered Routes =====")
for route in app.routes:
    if hasattr(route, 'methods') and hasattr(route, 'path'):
        methods = ', '.join(route.methods)
        print(f"[Backend] {methods:20s} {route.path}")
print("[Backend] ===================================\n")

# Mount Prometheus metrics endpoint (AFTER routers)
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
    )
