"""
Qdrant client wrapper for vector search operations.
Handles connection to Qdrant Cloud and collection management.
"""
import asyncio
from typing import List, Optional

from qdrant_client import QdrantClient as QdrantClientSDK
from qdrant_client.models import Distance, PointStruct, ScoredPoint, VectorParams

from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


class QdrantClient:
    """Async Qdrant client for vector operations."""

    def __init__(self):
        self.client: Optional[QdrantClientSDK] = None
        self.collection_name = settings.QDRANT_COLLECTION_NAME

    async def initialize(self) -> None:
        """Initialize Qdrant client and verify connection."""
        try:
            # Initialize Qdrant client
            self.client = QdrantClientSDK(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
            )

            # Verify connection by listing collections
            collections = await asyncio.to_thread(self.client.get_collections)
            collection_names = [c.name for c in collections.collections]

            logger.info(
                "qdrant_client_initialized",
                url=settings.QDRANT_URL,
                collection=self.collection_name,
                collections_found=len(collection_names),
            )

            # Check if our collection exists
            if self.collection_name not in collection_names:
                logger.warning(
                    "qdrant_collection_not_found",
                    collection=self.collection_name,
                    message="Collection does not exist. Run scripts/init_qdrant.py to create it.",
                )
            else:
                # Get collection info
                info = await asyncio.to_thread(
                    self.client.get_collection, self.collection_name
                )
                logger.info(
                    "qdrant_collection_verified",
                    collection=self.collection_name,
                    points_count=info.points_count,
                    vector_size=info.config.params.vectors.size,
                )

        except Exception as e:
            logger.error("qdrant_client_init_failed", error=str(e))
            raise

    async def close(self) -> None:
        """Close Qdrant client connection."""
        if self.client:
            # Qdrant client doesn't require explicit cleanup
            self.client = None
            logger.info("qdrant_client_closed")

    async def collection_exists(self) -> bool:
        """Check if the collection exists."""
        try:
            collections = await asyncio.to_thread(self.client.get_collections)
            collection_names = [c.name for c in collections.collections]
            return self.collection_name in collection_names
        except Exception as e:
            logger.error("qdrant_collection_check_failed", error=str(e))
            return False

    async def get_collection_info(self):
        """Get collection information."""
        try:
            info = await asyncio.to_thread(
                self.client.get_collection, self.collection_name
            )
            return info
        except Exception as e:
            logger.error("qdrant_get_collection_info_failed", error=str(e))
            raise

    async def search_similar(
        self,
        query_vector: List[float],
        limit: int = 8,
        score_threshold: float = 0.70,
    ) -> List[ScoredPoint]:
        """
        Search for similar vectors in Qdrant.

        Args:
            query_vector: Embedding vector to search for
            limit: Maximum number of results
            score_threshold: Minimum similarity score (0-1)

        Returns:
            List of ScoredPoint objects with payloads
        """
        try:
            results = await asyncio.to_thread(
                self.client.search,
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
            )

            logger.debug(
                "qdrant_search_complete",
                results_count=len(results),
                limit=limit,
                threshold=score_threshold,
            )

            return results

        except Exception as e:
            logger.error("qdrant_search_failed", error=str(e))
            raise

    async def upsert_points(self, points: List[PointStruct]) -> None:
        """
        Upsert points into Qdrant collection.

        Args:
            points: List of PointStruct objects to upsert
        """
        try:
            await asyncio.to_thread(
                self.client.upsert,
                collection_name=self.collection_name,
                points=points,
            )

            logger.debug(
                "qdrant_upsert_complete",
                points_count=len(points),
                collection=self.collection_name,
            )

        except Exception as e:
            logger.error("qdrant_upsert_failed", error=str(e))
            raise


# Global instance
qdrant_client = QdrantClient()
