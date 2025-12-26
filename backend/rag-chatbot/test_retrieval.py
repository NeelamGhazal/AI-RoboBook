"""Test retrieval pipeline end-to-end to diagnose 'no chunks found' issue"""
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

sys.path.insert(0, str(Path(__file__).parent))

from app.clients.local_embedding_client import local_embedding_client
from app.clients.qdrant_client import qdrant_client
from app.services.vector_search import search_similar_chunks

async def test_retrieval():
    print("\n" + "="*60)
    print("  RETRIEVAL PIPELINE DIAGNOSTIC TEST")
    print("="*60 + "\n")

    # Initialize clients
    print("🔄 Initializing clients...")
    await local_embedding_client.initialize()
    await qdrant_client.initialize()
    print("✅ Clients initialized\n")

    # Test queries
    queries = [
        "What is ROS 2?",
        "Explain physics simulation",
        "hello",
        "",
    ]

    for query in queries:
        print(f"\n{'='*60}")
        print(f"📝 Query: '{query}'")
        print(f"{'='*60}\n")

        if not query:
            print("⚠️  Empty query - skipping\n")
            continue

        try:
            # Test embedding
            print("1️⃣  Testing embedding generation...")
            embedding = await local_embedding_client.generate_embedding(query)
            print(f"   ✅ Embedding: {len(embedding)} dimensions")
            print(f"   📊 Sample values: {[round(x, 3) for x in embedding[:5]]}\n")

            # Test Qdrant direct search with different thresholds
            print("2️⃣  Testing Qdrant search with different thresholds...")

            for threshold in [0.70, 0.50, 0.30]:
                results = await qdrant_client.search_similar(
                    query_vector=embedding,
                    limit=5,
                    score_threshold=threshold,
                )
                print(f"\n   Threshold={threshold}:")
                print(f"   ✅ Results: {len(results)} chunks found")

                if results:
                    for i, r in enumerate(results[:3]):
                        text_preview = r.payload.get('text_content', '')[:60]
                        print(f"      {i+1}. Score: {r.score:.3f} | {text_preview}...")
                else:
                    print(f"      ❌ No results at threshold {threshold}")

            # Test full vector search service
            print(f"\n3️⃣  Testing vector_search service (default threshold=0.50)...")
            chunks = await search_similar_chunks(
                query=query,
                top_k=5,
                score_threshold=0.50,
            )
            print(f"   ✅ Chunks returned: {len(chunks)}")

            if chunks:
                print(f"\n   📚 Top results:")
                for i, c in enumerate(chunks[:3]):
                    print(f"      {i+1}. Score: {c['confidence_score']:.3f}")
                    print(f"         Chapter: {c['chapter']}")
                    print(f"         Section: {c['section']}")
                    print(f"         Text: {c['text'][:80]}...")
                    print()
            else:
                print(f"\n   ❌ NO CHUNKS RETURNED!")
                print(f"   ⚠️  This is why you see 'couldn't find relevant information'\n")

                # Diagnose
                print("   🔍 Diagnosis:")
                print("      - Embeddings generated successfully ✅")
                print("      - Qdrant connection working ✅")

                # Try lower threshold
                chunks_low = await search_similar_chunks(
                    query=query,
                    top_k=5,
                    score_threshold=0.30,
                )

                if chunks_low:
                    print(f"      - With threshold=0.30: {len(chunks_low)} chunks found")
                    print(f"      ⚠️  RECOMMENDATION: Lower score_threshold from 0.50 to 0.40")
                else:
                    print(f"      - Even with threshold=0.30: No chunks")
                    print(f"      ❌ Possible issues:")
                    print(f"         1. Embedding model mismatch (check collection vectors)")
                    print(f"         2. Query too short/generic")
                    print(f"         3. Qdrant collection empty")

        except Exception as e:
            print(f"\n❌ ERROR during retrieval test:")
            print(f"   {type(e).__name__}: {e}\n")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*60}")
    print("  TEST COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(test_retrieval())
