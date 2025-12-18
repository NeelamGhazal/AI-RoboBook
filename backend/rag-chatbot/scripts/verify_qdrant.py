"""
Qdrant collection verification script.
Checks collection exists, counts vectors, and verifies indexed status.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.clients.qdrant_client import qdrant_client
from app.utils.logging import get_logger

logger = get_logger(__name__)


async def verify_collection():
    """Verify Qdrant collection status."""
    try:
        await qdrant_client.initialize()
        logger.info("Qdrant client initialized")

        # Check if collection exists
        exists = await qdrant_client.collection_exists()

        if not exists:
            print(f"\n✗ Collection '{qdrant_client.collection_name}' does not exist")
            print("  Run 'python scripts/init_qdrant.py' to create it")
            return

        # Get collection information
        info = await qdrant_client.get_collection_info()

        print(f"\n✓ Collection: {qdrant_client.collection_name}")
        print(f"  Status: {info['status']}")
        print(f"  Total vectors: {info['vectors_count']}")
        print(f"  Indexed vectors: {info['indexed_vectors_count']}")
        print(f"  Points count: {info['points_count']}")

        if info['vectors_count'] == 0:
            print("\n⚠ No vectors in collection")
            print("  Run ingestion script to load textbook content:")
            print("  python scripts/ingest_textbook.py --source ../../frontend/docs")
        elif info['indexed_vectors_count'] < info['vectors_count']:
            print(f"\n⚠ Indexing in progress: {info['indexed_vectors_count']}/{info['vectors_count']}")
        else:
            print(f"\n✓ Collection ready for queries")

        logger.info("collection_verified", **info)

    except Exception as e:
        logger.error("collection_verification_failed", error=str(e))
        print(f"\n✗ Verification failed: {e}")
        raise

    finally:
        await qdrant_client.close()


if __name__ == "__main__":
    asyncio.run(verify_collection())
