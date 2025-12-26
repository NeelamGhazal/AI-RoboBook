import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

load_dotenv()

print("🔍 RAG Retrieval Diagnostics\n" + "="*60)

# Initialize
model = SentenceTransformer('all-MiniLM-L6-v2')
qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

# Test query
test_query = "What is ROS 2?"
print(f"\n1️⃣ Test Query: '{test_query}'")

# Generate embedding
query_embedding = model.encode(test_query).tolist()
print(f"   Embedding dims: {len(query_embedding)}")
print(f"   First 5 values: {query_embedding[:5]}")

# Test with VERY LOW threshold
thresholds = [0.0, 0.3, 0.4, 0.5]

for threshold in thresholds:
    print(f"\n2️⃣ Testing threshold: {threshold}")

    try:
        results = qdrant.query_points(
            collection_name="textbook_chunks",
            query=query_embedding,
            limit=5,
            score_threshold=threshold
        )

        # Extract points from response
        points = results.points if hasattr(results, 'points') else results

        print(f"   Results found: {len(points)}")

        if points:
            print(f"   Top 3 scores: {[round(r.score, 3) for r in points[:3]]}")
            print(f"   Sample text: {points[0].payload.get('text_content', 'N/A')[:100]}...")
        else:
            print(f"   ❌ NO RESULTS at threshold {threshold}")

    except Exception as e:
        print(f"   ❌ ERROR: {e}")

# Test scrolling (get ANY document)
print(f"\n3️⃣ Testing scroll (get any document):")
try:
    sample = qdrant.scroll(
        collection_name="textbook_chunks",
        limit=1,
        with_vectors=True
    )
    if sample[0]:
        doc = sample[0][0]
        print(f"   ✅ Sample document ID: {doc.id}")
        print(f"   Vector dims: {len(doc.vector) if doc.vector else 'No vector'}")
        print(f"   Payload keys: {list(doc.payload.keys())}")
        print(f"   Text preview: {doc.payload.get('text_content', 'N/A')[:100]}")
    else:
        print(f"   ❌ Collection is empty!")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

print("\n" + "="*60)
