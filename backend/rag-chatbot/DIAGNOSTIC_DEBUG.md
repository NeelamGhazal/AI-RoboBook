# 🔍 DIAGNOSTIC DEBUG - "Couldn't Find Relevant Information"

## Problem
Backend retrieval works in curl tests but frontend always gets "couldn't find relevant information."

## Root Cause Analysis

The message "I couldn't find relevant information" is returned when **`chunks = []`** (no chunks retrieved).

This happens at: `app/services/rag.py` lines 54-60

## Possible Causes

1. **Frontend connecting to wrong backend** (Windows backend vs WSL backend)
2. **Session validation failing** (session_id invalid, blocking retrieval)
3. **Query text corrupted/empty** (frontend sending malformed request)
4. **Embedding generation failing** (returns empty vector)
5. **Qdrant connection timeout** (can't reach vector DB from Windows backend)
6. **Score threshold too high** (filters out all results)

---

## 🧪 STEP-BY-STEP DIAGNOSIS

### **Step 1: Verify Which Backend Frontend is Connecting To**

**From Windows PowerShell**, test BOTH backends:

```powershell
# Test WSL backend (should work)
curl http://172.25.218.26:8000/health

# Test Windows localhost (might be different backend)
curl http://localhost:8000/health
```

**Check responses**:
- If BOTH return different timestamps, **you have TWO backends running**
- If only WSL works, frontend must use WSL IP
- If only localhost works, you have a Windows backend (not the WSL one)

### **Step 2: Capture Actual Frontend Request**

**Open Browser Console (F12)** and run:

```javascript
// Intercept and log the actual request
const originalFetch = window.fetch;
window.fetch = function(...args) {
  console.log('🔍 FETCH REQUEST:', args[0], args[1]);
  return originalFetch.apply(this, args)
    .then(response => {
      console.log('📥 FETCH RESPONSE:', response.status, response.url);
      return response;
    });
};

// Now send a chat message and watch the logs
```

**Expected logs**:
```
🔍 FETCH REQUEST: http://172.25.218.26:8000/api/v1/sessions {method: "POST", ...}
📥 FETCH RESPONSE: 201 http://172.25.218.26:8000/api/v1/sessions
🔍 FETCH REQUEST: http://172.25.218.26:8000/api/v1/chat/stream {method: "POST", body: '{"session_id":"...","question":"What is ROS 2?"}'}
📥 FETCH RESPONSE: 200 http://172.25.218.26:8000/api/v1/chat/stream
```

**Check**:
- Is it calling `172.25.218.26:8000` (WSL) or `localhost:8000` (Windows)?
- Is the `question` field populated correctly?

### **Step 3: Add Detailed Backend Logging**

I'll create an enhanced logging version to track the exact failure point.

### **Step 4: Test Direct API Call from Windows**

**From Windows PowerShell**, replicate exact frontend request:

```powershell
# Create session first
$session = curl -X POST "http://172.25.218.26:8000/api/v1/sessions" `
  -H "Content-Type: application/json" `
  -d '{}' | ConvertFrom-Json

Write-Host "Session ID: $($session.session_id)"

# Use that session to test stream
curl -X POST "http://172.25.218.26:8000/api/v1/chat/stream" `
  -H "Content-Type: application/json" `
  -d "{`"session_id`": `"$($session.session_id)`", `"question`": `"What is ROS 2?`"}"
```

**Expected**: Streaming response with citations

**If this fails**, the issue is backend-side. If this works, issue is frontend-side.

---

## 🔧 FIXES FOR EACH SCENARIO

### **Scenario 1: Frontend Using Wrong Backend URL**

**Symptom**: Browser console shows `localhost:8000` in requests

**Fix**: Update `frontend/src/components/ChatWidget/config.ts` line 20:

```typescript
return 'http://172.25.218.26:8000';  // WSL backend IP
```

Then rebuild:
```bash
cd /mnt/e/phyai-humanoid-textbook/frontend
rm -rf .docusaurus build
npm run build
npm run start
```

---

### **Scenario 2: Session Validation Blocking Retrieval**

**Symptom**: Backend logs show `Session not found` or `Session validation failed`

**Fix**: The streaming endpoint already has session validation relaxed (lines 186-194 in `chat.py`).

Check if the issue is here:

```python
# In app/api/v1/chat.py, lines 186-194
session_exists = await validate_session(request.session_id)
if not session_exists:
    print(f"[Backend] ⚠ Session validation failed: {request.session_id} - proceeding anyway")
    # DON'T raise 404 - frontend will detect this and recreate session
```

If you're seeing 404 errors, this isn't triggering. Check if `chat_stream` function is actually being called.

---

### **Scenario 3: Embedding Generation Failing**

**Symptom**: Backend logs show embedding errors or empty embeddings

**Diagnosis Script**:

```python
# Test embedding generation
import asyncio
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path("/mnt/e/phyai-humanoid-textbook/backend/rag-chatbot/.env"))

import sys
sys.path.insert(0, "/mnt/e/phyai-humanoid-textbook/backend/rag-chatbot")

from app.clients.local_embedding_client import local_embedding_client

async def test():
    await local_embedding_client.initialize()

    queries = ["What is ROS 2?", "hello", ""]
    for q in queries:
        try:
            emb = await local_embedding_client.generate_embedding(q)
            print(f"✅ Query: '{q}' → Embedding: {len(emb)} dims, first 3: {emb[:3]}")
        except Exception as e:
            print(f"❌ Query: '{q}' → ERROR: {e}")

asyncio.run(test())
```

**Expected**: All queries return 384-dimensional embeddings

---

### **Scenario 4: Qdrant Connection Failing**

**Symptom**: Backend logs show Qdrant timeout or connection errors

**Check**:
```bash
# From backend logs
grep -i "qdrant\|timeout\|connection" /tmp/backend.log
```

**Fix**: Ensure Qdrant credentials are correct in `.env`:
```bash
QDRANT_URL=https://9927c3c7-270d-4bf1-8fe6-0c2ceb37ac38.us-east4-0.gcp.cloud.qdrant.io:6333
QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.X75yBfdsNJ7IR17LJsc0SbGryezXNvPO0LQJC4dNKSw
QDRANT_COLLECTION_NAME=textbook_chunks
```

---

### **Scenario 5: Score Threshold Too High**

**Current Threshold**: 0.50 (in `vector_search.py` line 19)

**Test with Lower Threshold**:

Edit `app/services/vector_search.py` line 19:

```python
# BEFORE
score_threshold: float = 0.50,

# AFTER (for testing)
score_threshold: float = 0.30,
```

Restart backend and test. If this fixes it, the issue is low similarity scores.

**Permanent Fix**: Keep threshold at 0.50 but improve query processing (see below).

---

### **Scenario 6: Empty/Malformed Query**

**Symptom**: Backend logs show `question_length=0` or very short queries

**Check Backend Logs**:
```bash
tail -100 /tmp/backend.log | grep "question_length\|streaming_chat_request"
```

**Expected**:
```
streaming_chat_request    question_length=14    has_selected_text=False
```

If `question_length=0` or `question_length=2`, frontend is sending empty/corrupted queries.

**Fix Frontend**: Check `ChatWidget` component's message sending logic.

---

## 🛠️ ENHANCED DEBUG LOGGING

Add this to `app/services/vector_search.py` after line 37:

```python
# Generate embedding for query using local model
query_embedding = await local_embedding_client.generate_embedding(query)

# ADD THIS DEBUG LOGGING
logger.info(
    "embedding_generated",
    query=query,
    query_length=len(query),
    embedding_dim=len(query_embedding),
    embedding_sample=query_embedding[:3] if query_embedding else None,
)
```

Add this to `app/services/vector_search.py` after line 70:

```python
results = await qdrant_client.search_similar(
    query_vector=query_embedding,
    limit=top_k,
    score_threshold=score_threshold,
)

# ADD THIS DEBUG LOGGING
logger.info(
    "qdrant_search_complete",
    results_count=len(results),
    query_length=len(query),
    threshold=score_threshold,
    top_scores=[r.score for r in results[:3]] if results else [],
)
```

Restart backend and check logs after sending a query.

---

## 🎯 MOST LIKELY CAUSE

Based on the symptoms, the **most likely issue** is:

### **Frontend is connecting to `localhost:8000` (Windows backend) instead of `172.25.218.26:8000` (WSL backend)**

**Why This Happens**:
- Frontend config still has `localhost:8000`
- OR frontend built with old config (cache not cleared)
- OR Windows has a separate backend running that's NOT the WSL one

**Definitive Test**:

1. **Stop ALL backends everywhere**:
   ```bash
   # In WSL
   pkill -f "uvicorn app.main:app"

   # In Windows PowerShell
   Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
   ```

2. **Start ONLY WSL backend**:
   ```bash
   cd /mnt/e/phyai-humanoid-textbook/backend/rag-chatbot
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Verify frontend config**:
   ```bash
   grep -n "172.25.218.26" /mnt/e/phyai-humanoid-textbook/frontend/src/components/ChatWidget/config.ts
   ```

   **Expected**: Line 20 should have `return 'http://172.25.218.26:8000';`

4. **Rebuild frontend completely**:
   ```bash
   cd /mnt/e/phyai-humanoid-textbook/frontend
   rm -rf .docusaurus build node_modules/.cache
   npm run build
   npm run start
   ```

5. **Test in browser** with fetch intercept (see Step 2 above)

If fetch shows `localhost:8000`, the build didn't use the new config.

---

## 📋 VERIFICATION SCRIPT

Save this as `test_retrieval.py` in backend directory:

```python
"""Test retrieval pipeline end-to-end"""
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
    print("\n=== Testing Retrieval Pipeline ===\n")

    # Initialize clients
    await local_embedding_client.initialize()
    await qdrant_client.initialize()

    # Test query
    query = "What is ROS 2?"
    print(f"Query: '{query}'")

    # Test embedding
    print("\n1. Testing embedding generation...")
    embedding = await local_embedding_client.generate_embedding(query)
    print(f"   ✅ Embedding: {len(embedding)} dimensions")
    print(f"   Sample: {embedding[:3]}")

    # Test Qdrant search
    print("\n2. Testing Qdrant search...")
    results = await qdrant_client.search_similar(
        query_vector=embedding,
        limit=5,
        score_threshold=0.50,
    )
    print(f"   ✅ Results: {len(results)} chunks found")
    for i, r in enumerate(results[:3]):
        print(f"   {i+1}. Score: {r.score:.3f}, Text: {r.payload.get('text_content', '')[:80]}...")

    # Test full vector search
    print("\n3. Testing vector_search service...")
    chunks = await search_similar_chunks(
        query=query,
        top_k=5,
        score_threshold=0.50,
    )
    print(f"   ✅ Chunks: {len(chunks)} returned")
    for i, c in enumerate(chunks[:3]):
        print(f"   {i+1}. Score: {c['confidence_score']:.3f}, Chapter: {c['chapter']}, Section: {c['section']}")

    if not chunks:
        print("\n❌ NO CHUNKS RETURNED - This is the problem!")
        print("   Checking thresholds...")

        # Try with lower threshold
        chunks_low = await search_similar_chunks(
            query=query,
            top_k=5,
            score_threshold=0.30,
        )
        print(f"   With threshold=0.30: {len(chunks_low)} chunks")

        if chunks_low:
            print("   ⚠️  ISSUE: Threshold too high. Lower to 0.30 or improve embeddings.")
        else:
            print("   ❌ Still no chunks. Check Qdrant connection or embedding model.")
    else:
        print("\n✅ Retrieval pipeline working correctly!")

if __name__ == "__main__":
    asyncio.run(test_retrieval())
```

**Run**:
```bash
cd /mnt/e/phyai-humanoid-textbook/backend/rag-chatbot
python3 test_retrieval.py
```

This will show EXACTLY where the failure is.

---

## 🎯 FINAL RECOMMENDATION

**Execute these commands in order**:

```bash
# 1. Stop all backends
pkill -f "uvicorn app.main:app"

# 2. Verify frontend config has WSL IP
grep "172.25.218.26" /mnt/e/phyai-humanoid-textbook/frontend/src/components/ChatWidget/config.ts

# 3. If above shows nothing, manually edit line 20 to:
#    return 'http://172.25.218.26:8000';

# 4. Rebuild frontend completely
cd /mnt/e/phyai-humanoid-textbook/frontend
rm -rf .docusaurus build node_modules/.cache
npm run build

# 5. Start WSL backend
cd /mnt/e/phyai-humanoid-textbook/backend/rag-chatbot
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 6. Start frontend
cd /mnt/e/phyai-humanoid-textbook/frontend
npm run start

# 7. Test in browser: http://localhost:3000
# 8. Check fetch logs (see Step 2 above)
```

**The issue is 99% likely**: Frontend still pointing to wrong backend URL.
