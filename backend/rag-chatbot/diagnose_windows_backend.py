"""
Diagnose Windows Backend - Why Retrieval Returns Empty
Run this on Windows: python diagnose_windows_backend.py
"""
import asyncio
import sys
import os
from pathlib import Path

# Ensure we're in the right directory
backend_dir = Path(__file__).parent
os.chdir(backend_dir)

# Load environment variables
from dotenv import load_dotenv
load_dotenv(backend_dir / ".env")

print("\n" + "="*70)
print("  WINDOWS BACKEND DIAGNOSTIC - Why No Chunks Retrieved?")
print("="*70 + "\n")

# Check environment variables
print("1️⃣  Checking Environment Variables...")
print("-" * 70)

required_vars = [
    "QDRANT_URL",
    "QDRANT_API_KEY",
    "QDRANT_COLLECTION_NAME",
    "OPENROUTER_API_KEY",
]

missing_vars = []
for var in required_vars:
    value = os.getenv(var)
    if value:
        # Mask API keys
        if "KEY" in var or "API" in var:
            display = value[:20] + "..." if len(value) > 20 else value[:10] + "..."
        else:
            display = value
        print(f"✅ {var}: {display}")
    else:
        print(f"❌ {var}: NOT SET")
        missing_vars.append(var)

if missing_vars:
    print(f"\n⚠️  Missing environment variables: {missing_vars}")
    print("   Check your .env file!")
    sys.exit(1)

print("\n✅ All environment variables set\n")

# Test Qdrant connection
print("2️⃣  Testing Qdrant Connection...")
print("-" * 70)

async def test_qdrant():
    try:
        from app.clients.qdrant_client import qdrant_client
        await qdrant_client.initialize()

        info = await qdrant_client.get_collection_info()
        print(f"✅ Qdrant connected: {os.getenv('QDRANT_URL')}")
        print(f"✅ Collection: {os.getenv('QDRANT_COLLECTION_NAME')}")
        print(f"✅ Points count: {info.points_count}")
        print(f"✅ Vector size: {info.config.params.vectors.size}")
        return True
    except Exception as e:
        print(f"❌ Qdrant connection failed: {e}")
        print(f"   URL: {os.getenv('QDRANT_URL')}")
        print(f"   Check network connection and credentials!")
        return False

qdrant_ok = asyncio.run(test_qdrant())
if not qdrant_ok:
    sys.exit(1)

print()

# Test embedding generation
print("3️⃣  Testing Embedding Generation...")
print("-" * 70)

async def test_embeddings():
    try:
        from app.clients.local_embedding_client import local_embedding_client
        await local_embedding_client.initialize()

        test_text = "What is ROS 2?"
        embedding = await local_embedding_client.generate_embedding(test_text)

        print(f"✅ Embedding model loaded: all-MiniLM-L6-v2")
        print(f"✅ Embedding dimensions: {len(embedding)}")
        print(f"✅ Sample values: {[round(x, 3) for x in embedding[:5]]}")
        return embedding
    except Exception as e:
        print(f"❌ Embedding generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

embedding = asyncio.run(test_embeddings())
if embedding is None:
    sys.exit(1)

print()

# Test Qdrant search
print("4️⃣  Testing Qdrant Vector Search...")
print("-" * 70)

async def test_search():
    try:
        from app.clients.qdrant_client import qdrant_client
        from app.clients.local_embedding_client import local_embedding_client

        # Ensure initialized
        await local_embedding_client.initialize()
        await qdrant_client.initialize()

        query = "What is ROS 2?"
        print(f"Query: '{query}'")

        # Generate embedding
        query_embedding = await local_embedding_client.generate_embedding(query)
        print(f"✅ Embedding generated: {len(query_embedding)} dimensions\n")

        # Test with different thresholds
        for threshold in [0.0, 0.3, 0.5, 0.7]:
            results = await qdrant_client.search_similar(
                query_vector=query_embedding,
                limit=5,
                score_threshold=threshold,
            )

            print(f"Threshold {threshold}: {len(results)} results")
            if results:
                for i, r in enumerate(results[:2]):
                    print(f"  {i+1}. Score: {r.score:.3f} | {r.payload.get('text_content', '')[:60]}...")
            else:
                print(f"  ❌ No results")
            print()

        if not any([len(results) > 0 for threshold in [0.0, 0.3, 0.5]]):
            print("❌ CRITICAL: No results even with threshold=0.0")
            print("   Possible causes:")
            print("   1. Embedding model mismatch")
            print("   2. Collection is empty (but points_count shows 913...)")
            print("   3. Query embedding is corrupt")
            return False

        return True
    except Exception as e:
        print(f"❌ Search failed: {e}")
        import traceback
        traceback.print_exc()
        return False

search_ok = asyncio.run(test_search())
if not search_ok:
    sys.exit(1)

# Test full RAG pipeline
print("5️⃣  Testing Full Vector Search Service...")
print("-" * 70)

async def test_vector_search_service():
    try:
        from app.services.vector_search import search_similar_chunks
        from app.clients.local_embedding_client import local_embedding_client
        from app.clients.qdrant_client import qdrant_client

        # Ensure initialized
        await local_embedding_client.initialize()
        await qdrant_client.initialize()

        query = "What is ROS 2?"
        print(f"Query: '{query}'\n")

        chunks = await search_similar_chunks(
            query=query,
            top_k=5,
            score_threshold=0.50,
        )

        print(f"Results: {len(chunks)} chunks")
        if chunks:
            print("\nTop results:")
            for i, chunk in enumerate(chunks[:3]):
                print(f"\n{i+1}. Score: {chunk['confidence_score']:.3f}")
                print(f"   Chapter: {chunk['chapter']}")
                print(f"   Section: {chunk['section']}")
                print(f"   Text: {chunk['text'][:80]}...")
            return True
        else:
            print("\n❌ PROBLEM: No chunks returned from vector_search service")
            print("   This is why you see 'couldn't find relevant information'")

            # Try with lower threshold
            print("\n   Testing with lower threshold (0.30)...")
            chunks_low = await search_similar_chunks(
                query=query,
                top_k=5,
                score_threshold=0.30,
            )

            if chunks_low:
                print(f"   ✅ With threshold=0.30: {len(chunks_low)} chunks found")
                print("\n   🔧 FIX: Lower score_threshold in vector_search.py line 19")
                print("      FROM: score_threshold: float = 0.50")
                print("      TO:   score_threshold: float = 0.40")
            else:
                print(f"   ❌ Still no chunks with threshold=0.30")

            return False
    except Exception as e:
        print(f"❌ Vector search service failed: {e}")
        import traceback
        traceback.print_exc()
        return False

service_ok = asyncio.run(test_vector_search_service())

print("\n" + "="*70)
print("  DIAGNOSTIC COMPLETE")
print("="*70 + "\n")

if service_ok:
    print("✅ All tests passed! Retrieval should work.")
    print("\n📋 Next steps:")
    print("   1. Restart Windows backend")
    print("   2. Test chat widget with 'What is ROS 2?'")
    print("   3. Should get textbook response with citations")
else:
    print("❌ Retrieval is failing. See errors above for fix.")
    print("\n📋 Common fixes:")
    print("   1. Check .env file has correct Qdrant credentials")
    print("   2. Lower score_threshold in app/services/vector_search.py")
    print("   3. Restart backend after making changes")
