"""
Database migration script to create sessions and messages tables.
Run this script to initialize the database schema.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.clients.db_client import db_client
from app.utils.logging import get_logger

logger = get_logger(__name__)

# SQL for creating sessions table
CREATE_SESSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255),
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted')),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_last_activity ON sessions(last_activity);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
"""

# SQL for creating messages table
CREATE_MESSAGES_TABLE = """
CREATE TABLE IF NOT EXISTS messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL CHECK (char_length(content) <= 10000),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    token_count INTEGER NOT NULL CHECK (token_count > 0),
    selected_text TEXT,
    citations JSONB,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_messages_session_timestamp ON messages(session_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_messages_role ON messages(role);
"""


async def run_migrations():
    """Run database migrations."""
    try:
        await db_client.connect()
        logger.info("Running database migrations...")

        # Create sessions table
        await db_client.execute(CREATE_SESSIONS_TABLE)
        logger.info("Sessions table created successfully")

        # Create messages table
        await db_client.execute(CREATE_MESSAGES_TABLE)
        logger.info("Messages table created successfully")

        logger.info("All migrations completed successfully")

    except Exception as e:
        logger.error("Migration failed", error=str(e))
        raise
    finally:
        await db_client.disconnect()


if __name__ == "__main__":
    asyncio.run(run_migrations())
