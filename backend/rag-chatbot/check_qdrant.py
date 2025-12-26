"""
STEP 1: Check if Qdrant has vectors
Run: python check_qdrant.py
"""
from qdrant_client import QdrantClient
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

print("\n" + "="*70)
print("  QDRANT VECTOR CHECK")
print("="*70 + "\n")

# Get credentials
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "textbook_chunks")

print(f"URL: {QDRANT_URL}")
print(f"Collection: {COLLECTION_NAME}")
print()

# Initialize client
try:
    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY
    )
    print("✅ Qdrant client initialized\n")
except Exception as e:
    print(f"❌ Failed to connect to Qdrant: {e}")
    exit(1)

# Check collections
try:
    collections = client.get_collections()
    collection_names = [c.name for c in collections.collections]
    print(f"Available collections: {collection_names}\n")

    if COLLECTION_NAME not in collection_names:
        print(f"❌ CRITICAL: Collection '{COLLECTION_NAME}' does NOT exist!")
        print(f"   Available: {collection_names}")
        print("\n→ NEXT STEP: Run ingestion script to create collection")
        exit(1)

    print(f"✅ Collection '{COLLECTION_NAME}' exists\n")

except Exception as e:
    print(f"❌ Error getting collections: {e}")
    exit(1)

# Check vector count
try:
    collection_info = client.get_collection(COLLECTION_NAME)
    points_count = collection_info.points_count
    vector_size = collection_info.config.params.vectors.size

    print(f"📊 Collection Info:")
    print(f"  Points count: {points_count}")
    print(f"  Vector size: {vector_size}\n")

    if points_count == 0:
        print("❌ CRITICAL: Collection is EMPTY! No vectors to search.")
        print("\n→ NEXT STEP: Run ingestion script to add vectors")
        exit(1)

    print(f"✅ {points_count} vectors exist\n")

except Exception as e:
    print(f"❌ Error getting collection info: {e}")
    exit(1)

# Sample a vector
try:
    sample = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=3,
        with_payload=True,
        with_vectors=False
    )

    print(f"📝 Sample vectors:\n")
    for i, point in enumerate(sample[0][:3]):
        payload = point.payload
        text_preview = payload.get("text_content", "")[:80]
        chapter = payload.get("chapter_path", "N/A")
        section = payload.get("section_title", "N/A")

        print(f"{i+1}. ID: {point.id}")
        print(f"   Chapter: {chapter}")
        print(f"   Section: {section}")
        print(f"   Text: {text_preview}...")
        print()

    print("✅ Vectors are accessible\n")

except Exception as e:
    print(f"❌ Error sampling vectors: {e}")
    exit(1)

# Test search with sample query
try:
    from sentence_transformers import SentenceTransformer

    print("🔍 Testing vector search...\n")

    # Load embedding model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    query = "What is ROS 2?"
    print(f"Query: '{query}'")

    # Generate embedding
    query_embedding = model.encode(query).tolist()
    print(f"Embedding: {len(query_embedding)} dimensions\n")

    # Search with different thresholds
    for threshold in [0.7, 0.5, 0.4, 0.3, 0.0]:
        response = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding,
            limit=5,
            score_threshold=threshold
        )
        # Extract points from QueryResponse
        results = response.points if hasattr(response, 'points') else response

        print(f"Threshold {threshold}: {len(results)} results", end="")
        if results:
            scores = [r.score for r in results]
            print(f" (scores: {[round(s, 3) for s in scores[:3]]})")
        else:
            print(" (no results)")

    print()

    # Check if any results at all
    response_any = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=5,
        score_threshold=0.0
    )
    results_any = response_any.points if hasattr(response_any, 'points') else response_any

    if not results_any:
        print("❌ CRITICAL: No results even with threshold=0.0!")
        print("   Possible causes:")
        print("   1. Embedding model mismatch (vectors created with different model)")
        print("   2. Corrupt vectors")
        print("\n→ NEXT STEP: Re-ingest vectors with correct embedding model")
    elif len(results_any) >= 3 and all(r.score >= 0.4 for r in results_any[:3]):
        print("✅ Search working! Top 3 results have scores >= 0.4")
        print("\n→ ISSUE: Backend code not using search correctly")
        print("→ NEXT STEP: Run debug_vector_search.py")
    elif len(results_any) >= 3 and any(r.score < 0.5 for r in results_any[:3]):
        print("⚠️  Search returns results but scores are low")
        print(f"   Top scores: {[round(r.score, 3) for r in results_any[:3]]}")
        print("\n→ ISSUE: Score threshold too high in backend")
        print("→ FIX: Lower threshold to 0.35 in vector_search.py")
    else:
        print("⚠️  Search returns some results")
        print("\n→ NEXT STEP: Run debug_vector_search.py")

except Exception as e:
    print(f"❌ Error testing search: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("  CHECK COMPLETE")
print("="*70 + "\n")
