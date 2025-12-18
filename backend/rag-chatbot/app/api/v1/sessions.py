"""
Session management endpoints.
Creates and manages chat sessions.
"""
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from app.db import crud
from app.models.schemas import SessionCreate, SessionResponse
from app.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])

# In-memory session store (fallback if database fails)
_in_memory_sessions = {}


@router.post("", response_model=SessionResponse, status_code=201)
async def create_session(
    session_data: SessionCreate = SessionCreate(),
) -> SessionResponse:
    """
    Create a new chat session.

    Tries to use database first, falls back to in-memory if database unavailable.

    Args:
        session_data: Optional session metadata (user_id, metadata)

    Returns:
        Created session with ID and timestamp
    """
    print(f"[Backend] POST /api/v1/sessions called")
    print(f"[Backend] Session data: user_id={session_data.user_id}, metadata={session_data.metadata}")

    # Try database first
    try:
        print("[Backend] Attempting database session creation...")
        session = await crud.create_session(
            user_id=session_data.user_id,
            metadata=session_data.metadata,
        )

        session_id = str(session.session_id)
        print(f"[Backend] ✓ Session created in database: {session_id}")

        logger.info(
            "session_created_db",
            session_id=session_id,
            user_id=session_data.user_id,
        )

        return SessionResponse(
            session_id=session_id,
            created_at=session.created_at,
            last_activity=session.last_activity,
        )

    except Exception as db_error:
        # Log database error but don't fail - use in-memory fallback
        print(f"[Backend] ⚠ Database session creation failed: {type(db_error).__name__}: {str(db_error)}")
        print("[Backend] Falling back to in-memory session storage...")

        logger.warning(
            "session_db_failed_using_memory",
            error=str(db_error),
            error_type=type(db_error).__name__,
        )

        # Fallback to in-memory session
        try:
            session_id = str(uuid4())
            now = datetime.utcnow()

            _in_memory_sessions[session_id] = {
                "session_id": session_id,
                "user_id": session_data.user_id,
                "metadata": session_data.metadata or {},
                "created_at": now,
                "last_activity": now,
                "messages": [],
            }

            print(f"[Backend] ✓ Session created in memory: {session_id}")
            print(f"[Backend] In-memory sessions count: {len(_in_memory_sessions)}")

            logger.info(
                "session_created_memory",
                session_id=session_id,
                user_id=session_data.user_id,
            )

            return SessionResponse(
                session_id=session_id,
                created_at=now,
                last_activity=now,
            )

        except Exception as mem_error:
            # This should never happen, but handle it anyway
            print(f"[Backend] ✗ Critical error: In-memory session creation failed: {str(mem_error)}")
            logger.error(
                "session_creation_critical_failure",
                db_error=str(db_error),
                memory_error=str(mem_error),
            )
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create session (both database and in-memory): {str(mem_error)}"
            )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
) -> SessionResponse:
    """
    Get session by ID.

    Checks database first, then in-memory store.

    Args:
        session_id: Session UUID

    Returns:
        Session information
    """
    print(f"[Backend] GET /api/v1/sessions/{session_id} called")

    # Try database first
    try:
        print("[Backend] Checking database for session...")
        session = await crud.get_session(session_id)

        if session:
            print(f"[Backend] ✓ Session found in database: {session_id}")
            return SessionResponse(
                session_id=str(session.session_id),
                created_at=session.created_at,
                last_activity=session.last_activity,
            )

    except Exception as db_error:
        print(f"[Backend] ⚠ Database lookup failed: {type(db_error).__name__}: {str(db_error)}")
        logger.warning("get_session_db_failed", session_id=session_id, error=str(db_error))

    # Check in-memory store
    if session_id in _in_memory_sessions:
        print(f"[Backend] ✓ Session found in memory: {session_id}")
        session_data = _in_memory_sessions[session_id]
        return SessionResponse(
            session_id=session_data["session_id"],
            created_at=session_data["created_at"],
            last_activity=session_data["last_activity"],
        )

    # Not found in either location
    print(f"[Backend] ✗ Session not found: {session_id}")
    raise HTTPException(
        status_code=404,
        detail=f"Session {session_id} not found"
    )
