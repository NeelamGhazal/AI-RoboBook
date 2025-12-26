"""
Test Live Retrieval - Run while backend is running
This will show EXACTLY why retrieval is failing
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("\n" + "="*70)
print("  LIVE RETRIEVAL TEST - Why Always Fallback Message?")
print("="*70 + "\n")

# Test queries
queries = [
    "What is ROS 2?",           # Should definitely work
    "explain it",               # Too vague, probably fails
    "Explain physics simulation",  # Should work
    "hello",                    # Should fail
]

for query in queries:
    print(f"\n{'='*70}")
    print(f"📝 Testing Query: '{query}'")
    print(f"{'='*70}\n")

    # Create session
    session_response = requests.post(f"{BASE_URL}/api/v1/sessions", json={})

    if session_response.status_code != 201:
        print(f"❌ Session creation failed: {session_response.status_code}")
        continue

    session_id = session_response.json()["session_id"]
    print(f"✅ Session created: {session_id}\n")

    # Send query
    payload = {
        "session_id": session_id,
        "question": query
    }

    print(f"Sending to: POST {BASE_URL}/api/v1/chat/stream")
    print(f"Payload: {json.dumps(payload, indent=2)}\n")

    response = requests.post(
        f"{BASE_URL}/api/v1/chat/stream",
        json=payload,
        stream=True,
        timeout=30
    )

    if response.status_code != 200:
        print(f"❌ Stream request failed: {response.status_code}")
        print(f"Response: {response.text}")
        continue

    print(f"✅ Stream started (status {response.status_code})\n")

    # Parse streaming response
    tokens = []
    citations = []
    metadata = {}

    for line in response.iter_lines():
        if not line:
            continue

        line_str = line.decode('utf-8')
        if line_str.startswith('data: '):
            data_str = line_str[6:]  # Remove 'data: '
            try:
                event = json.loads(data_str)

                if event.get("type") == "token":
                    tokens.append(event.get("content", ""))
                elif event.get("type") == "citations":
                    citations = event.get("citations", [])
                elif event.get("type") == "metadata":
                    metadata = event.get("metadata", {})
                elif event.get("type") == "done":
                    break
            except json.JSONDecodeError:
                pass

    # Analyze response
    full_response = "".join(tokens)

    print(f"📊 Results:")
    print(f"  Response length: {len(full_response)} chars")
    print(f"  Citations: {len(citations)}")
    print(f"  Chunks retrieved: {metadata.get('chunks_retrieved', 'N/A')}")
    print(f"  Avg confidence: {metadata.get('avg_confidence', 'N/A')}")

    if full_response == "I couldn't find relevant information in the textbook to answer your question.":
        print(f"\n❌ FALLBACK MESSAGE RETURNED!")
        print(f"   Chunks retrieved: {metadata.get('chunks_retrieved', 0)}")
        print(f"   → This means search_similar_chunks() returned empty list")
        print(f"   → Check backend logs for [VECTOR_SEARCH] messages")
    else:
        print(f"\n✅ TEXTBOOK CONTENT RETURNED!")
        print(f"   Response preview: {full_response[:100]}...")
        if citations:
            print(f"\n   Top citations:")
            for i, c in enumerate(citations[:2]):
                print(f"   {i+1}. {c.get('chapter')} - {c.get('section')} ({c.get('confidence_score', 0):.2f})")

print("\n" + "="*70)
print("  TEST COMPLETE")
print("="*70)
print("\n💡 Next Steps:")
print("   1. Check backend terminal for [VECTOR_SEARCH] debug logs")
print("   2. If threshold issue, lower from 0.50 to 0.40 in vector_search.py")
print("   3. If no logs appear, backend didn't process request - check backend is running")
print()
