"""
CRUD operations for sessions and messages.
Uses asyncpg for async database operations.
"""
import json
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from app.clients.db_client import db_client
from app.models.message import Message
from app.models.session import Session
from app.utils.logging import get_logger
from app.utils.metrics import DB_OPERATION_DURATION

logger = get_logger(__name__)


# Session CRUD operations
async def create_session(user_id: Optional[str] = None, metadata: Optional[dict] = None) -> Session:
    """Create a new chat session."""
    with DB_OPERATION_DURATION.labels(operation="create_session").time():
        query = """
            INSERT INTO sessions (user_id, metadata)
            VALUES ($1, $2)
            RETURNING session_id, user_id, status, created_at, last_activity, metadata
        """
        record = await db_client.fetchrow(
            query, user_id, json.dumps(metadata) if metadata else "{}"
        )
        logger.info("session_created", session_id=str(record["session_id"]))
        return Session.from_record(record)


async def get_session(session_id: UUID) -> Optional[Session]:
    """Get session by ID."""
    with DB_OPERATION_DURATION.labels(operation="get_session").time():
        query = """
            SELECT session_id, user_id, status, created_at, last_activity, metadata
            FROM sessions
            WHERE session_id = $1
        """
        record = await db_client.fetchrow(query, session_id)
        return Session.from_record(record) if record else None


async def update_session_activity(session_id: UUID) -> None:
    """Update last_activity timestamp for session."""
    with DB_OPERATION_DURATION.labels(operation="update_session_activity").time():
        query = """
            UPDATE sessions
            SET last_activity = NOW()
            WHERE session_id = $1
        """
        await db_client.execute(query, session_id)


# Message CRUD operations
async def create_message(
    session_id: UUID,
    role: str,
    content: str,
    token_count: int,
    selected_text: Optional[str] = None,
    citations: Optional[list] = None,
    metadata: Optional[dict] = None,
) -> Message:
    """Create a new message in a session."""
    with DB_OPERATION_DURATION.labels(operation="create_message").time():
        query = """
            INSERT INTO messages (session_id, role, content, token_count, selected_text, citations, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING message_id, session_id, role, content, timestamp, token_count, selected_text, citations, metadata
        """
        record = await db_client.fetchrow(
            query,
            session_id,
            role,
            content,
            token_count,
            selected_text,
            json.dumps(citations) if citations else None,
            json.dumps(metadata) if metadata else "{}",
        )
        logger.info(
            "message_created",
            message_id=str(record["message_id"]),
            session_id=str(session_id),
            role=role,
        )
        return Message.from_record(record)


async def get_messages_by_session(
    session_id: UUID, limit: int = 50, offset: int = 0
) -> tuple[List[Message], int]:
    """Get messages for a session with pagination."""
    with DB_OPERATION_DURATION.labels(operation="get_messages").time():
        # Get total count
        count_query = "SELECT COUNT(*) FROM messages WHERE session_id = $1"
        total = await db_client.fetchval(count_query, session_id)

        # Get messages
        query = """
            SELECT message_id, session_id, role, content, timestamp, token_count, selected_text, citations, metadata
            FROM messages
            WHERE session_id = $1
            ORDER BY timestamp DESC
            LIMIT $2 OFFSET $3
        """
        records = await db_client.fetch(query, session_id, limit, offset)
        messages = [Message.from_record(record) for record in records]

        return messages, total


async def get_recent_messages(session_id: UUID, count: int = 10) -> List[Message]:
    """Get recent messages for context building."""
    query = """
        SELECT message_id, session_id, role, content, timestamp, token_count, selected_text, citations, metadata
        FROM messages
        WHERE session_id = $1
        ORDER BY timestamp DESC
        LIMIT $2
    """
    records = await db_client.fetch(query, session_id, count)
    return [Message.from_record(record) for record in reversed(records)]
