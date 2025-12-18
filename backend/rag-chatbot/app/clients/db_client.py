"""
PostgreSQL database client using asyncpg for async operations.
Implements connection pooling for optimal performance.
"""
import asyncpg
from typing import Optional

from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


class DatabaseClient:
    """Async PostgreSQL client with connection pooling."""

    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self) -> None:
        """Initialize database connection pool."""
        try:
            self.pool = await asyncpg.create_pool(
                dsn=settings.NEON_DATABASE_URL,
                min_size=settings.DB_POOL_MIN_SIZE,
                max_size=settings.DB_POOL_MAX_SIZE,
                max_queries=50000,
                max_inactive_connection_lifetime=300,
                command_timeout=10,
            )
            logger.info(
                "database_pool_created",
                min_size=settings.DB_POOL_MIN_SIZE,
                max_size=settings.DB_POOL_MAX_SIZE,
            )
        except Exception as e:
            logger.error("database_connection_failed", error=str(e))
            raise

    async def disconnect(self) -> None:
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("database_pool_closed")

    async def execute(self, query: str, *args) -> str:
        """Execute a query and return status."""
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args) -> list:
        """Fetch multiple rows."""
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args) -> Optional[asyncpg.Record]:
        """Fetch a single row."""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args):
        """Fetch a single value."""
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)


# Global database client instance
db_client = DatabaseClient()
