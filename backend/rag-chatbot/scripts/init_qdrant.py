"""
Qdrant collection initialization script.
Creates the textbook_chunks collection with proper vector configuration for local embeddings (384 dimensions).
Uses sentence-transformers/all-MiniLM-L6-v2 model (completely free, no API key needed).
"""

import os
import sys
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Load configuration from environment
QDRANT_URL = os.getenv("QDRANT_URL", "https://9927c3c7-270d-4bf1-8fe6-0c2ceb37ac38.us-east4-0.gcp.cloud.qdrant.io:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "textbook_chunks")

# Vector configuration for all-MiniLM-L6-v2
VECTOR_SIZE = 384  # sentence-transformers/all-MiniLM-L6-v2 output dimension


def initialize_collection():
    """Initialize Qdrant collection for textbook chunks."""
    print("=" * 70)
    print("QDRANT COLLECTION INITIALIZATION")
    print("=" * 70)
    print(f"\nCollection name: {COLLECTION_NAME}")
    print(f"Vector size: {VECTOR_SIZE} (sentence-transformers/all-MiniLM-L6-v2)")
    print(f"Distance metric: Cosine")
    print(f"Qdrant URL: {QDRANT_URL}")
    print()

    try:
        # Connect to Qdrant
        print("Connecting to Qdrant...")
        client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
        )
        print("✓ Connected to Qdrant\n")

        # Check if collection already exists
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]

        if COLLECTION_NAME in collection_names:
            print(f"✓ Collection '{COLLECTION_NAME}' already exists!")

            # Get collection info
            info = client.get_collection(COLLECTION_NAME)
            print(f"  Vector size: {info.config.params.vectors.size}")
            print(f"  Points count: {info.points_count}")
            print(f"  Status: {info.status}")

            # Warn if dimensions don't match
            if info.config.params.vectors.size != VECTOR_SIZE:
                print(f"\n⚠ WARNING: Existing collection has {info.config.params.vectors.size} dimensions!")
                print(f"⚠ Expected: {VECTOR_SIZE} dimensions for all-MiniLM-L6-v2")
                print(f"⚠ You may need to delete and recreate the collection")
                print(f"\nTo delete: Run this in Python:")
                print(f"  from qdrant_client import QdrantClient")
                print(f"  client = QdrantClient(url='{QDRANT_URL}', api_key='...')")
                print(f"  client.delete_collection('{COLLECTION_NAME}')")
                print(f"  # Then run this script again")

            return

        # Create new collection
        print(f"Creating collection '{COLLECTION_NAME}'...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )
        print("✓ Collection created successfully!\n")

        # Verify creation
        info = client.get_collection(COLLECTION_NAME)
        print(f"Collection Info:")
        print(f"  Name: {COLLECTION_NAME}")
        print(f"  Vector size: {info.config.params.vectors.size}")
        print(f"  Distance metric: {info.config.params.vectors.distance}")
        print(f"  Points count: {info.points_count}")
        print(f"  Status: {info.status}")

        print(f"\n{'=' * 70}")
        print("SUCCESS! Collection ready for ingestion.")
        print("=" * 70)
        print(f"\nNext step: Run ingestion script")
        print(f"  python scripts/ingest_book.py")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise


def recreate_collection():
    """Delete existing collection and recreate with correct dimensions."""
    print("=" * 70)
    print("QDRANT COLLECTION RECREATION")
    print("=" * 70)
    print(f"\n⚠ This will DELETE all existing data in '{COLLECTION_NAME}'")
    print(f"⚠ And recreate it with {VECTOR_SIZE} dimensions\n")

    try:
        # Connect to Qdrant
        print("Connecting to Qdrant...")
        client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
        )
        print("✓ Connected to Qdrant\n")

        # Check if collection exists
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]

        if COLLECTION_NAME in collection_names:
            print(f"Deleting existing collection '{COLLECTION_NAME}'...")
            client.delete_collection(COLLECTION_NAME)
            print("✓ Collection deleted\n")
        else:
            print(f"Collection '{COLLECTION_NAME}' does not exist\n")

        # Create new collection
        print(f"Creating collection '{COLLECTION_NAME}' with {VECTOR_SIZE} dimensions...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )
        print("✓ Collection created successfully!\n")

        # Verify creation
        info = client.get_collection(COLLECTION_NAME)
        print(f"Collection Info:")
        print(f"  Name: {COLLECTION_NAME}")
        print(f"  Vector size: {info.config.params.vectors.size}")
        print(f"  Distance metric: {info.config.params.vectors.distance}")
        print(f"  Points count: {info.points_count}")
        print(f"  Status: {info.status}")

        print(f"\n{'=' * 70}")
        print("SUCCESS! Collection ready for ingestion.")
        print("=" * 70)
        print(f"\nNext step: Run ingestion script")
        print(f"  python scripts/ingest_book.py\n")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--recreate":
        recreate_collection()
    else:
        initialize_collection()
