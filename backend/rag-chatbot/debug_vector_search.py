"""
STEP 2B: Debug Vector Search in Backend Code
Run: python debug_vector_search.py
Then send a test message and watch output
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

print("\n" + "="*70)
print("  BACKEND VECTOR SEARCH DEBUG")
print("="*70 + "\n")

# Monkey-patch vector_search.py to add debug output
original_file = Path(__file__).parent / "app" / "services" / "vector_search.py"
backup_file = Path(__file__).parent / "app" / "services" / "vector_search.py.backup"

# Read original
with open(original_file, 'r') as f:
    original_content = f.read()

# Check if already patched
if '[DEBUG-PATCH]' in original_content:
    print("⚠️  Already patched. Skipping.\n")
else:
    # Backup
    with open(backup_file, 'w') as f:
        f.write(original_content)
    print(f"✅ Backed up to: {backup_file}\n")

    # Add debug prints
    patched_content = original_content.replace(
        '    with RETRIEVAL_DURATION.time():',
        '''    # [DEBUG-PATCH] Enhanced debugging
    print(f"[DEBUG-PATCH] search_similar_chunks called")
    print(f"[DEBUG-PATCH] Query: '{query}'")
    print(f"[DEBUG-PATCH] top_k: {top_k}, score_threshold: {score_threshold}")

    with RETRIEVAL_DURATION.time():'''
    )

    patched_content = patched_content.replace(
        '            query_embedding = await local_embedding_client.generate_embedding(query)',
        '''            query_embedding = await local_embedding_client.generate_embedding(query)
            print(f"[DEBUG-PATCH] ✓ Embedding generated: {len(query_embedding)} dims")
            print(f"[DEBUG-PATCH] Sample: {query_embedding[:3]}")'''
    )

    patched_content = patched_content.replace(
        '                results = await qdrant_client.search_similar(',
        '''                print(f"[DEBUG-PATCH] Calling qdrant_client.search_similar with threshold={score_threshold}")
                results = await qdrant_client.search_similar('''
    )

    patched_content = patched_content.replace(
        '                logger.info(\n                    "semantic_search_complete",',
        '''                print(f"[DEBUG-PATCH] ✓ Qdrant returned {len(results)} results")
                if results:
                    scores = [r.score for r in results]
                    print(f"[DEBUG-PATCH] Scores: {[round(s, 3) for s in scores[:5]]}")
                else:
                    print(f"[DEBUG-PATCH] ❌ NO RESULTS - This triggers fallback!")

                logger.info(
                    "semantic_search_complete",'''
    )

    # Write patched version
    with open(original_file, 'w') as f:
        f.write(patched_content)

    print(f"✅ Patched: {original_file}")
    print("   Added [DEBUG-PATCH] print statements\n")

print("="*70)
print("  INSTRUCTIONS")
print("="*70)
print("""
1. Restart backend:
   cd E:\\phyai-humanoid-textbook\\backend\\rag-chatbot
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

2. Send test message from frontend or curl:
   curl -X POST "http://localhost:8000/api/v1/chat/stream" \\
     -H "Content-Type: application/json" \\
     -d '{"session_id": "test", "question": "What is ROS 2?"}'

3. Watch backend terminal for [DEBUG-PATCH] output

4. Share ALL [DEBUG-PATCH] lines

Expected output:
  [DEBUG-PATCH] search_similar_chunks called
  [DEBUG-PATCH] Query: 'What is ROS 2?'
  [DEBUG-PATCH] ✓ Embedding generated: 384 dims
  [DEBUG-PATCH] Calling qdrant_client.search_similar with threshold=0.5
  [DEBUG-PATCH] ✓ Qdrant returned 5 results
  [DEBUG-PATCH] Scores: [0.707, 0.686, 0.615, 0.582, 0.561]

If you see "❌ NO RESULTS", the issue is threshold too high.
Fix: Edit app/services/vector_search.py line 19, change 0.50 → 0.35

To remove patch:
  cp app/services/vector_search.py.backup app/services/vector_search.py
""")
print("="*70 + "\n")
