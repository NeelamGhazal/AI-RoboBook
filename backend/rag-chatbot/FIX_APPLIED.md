# Fix Applied: Score Threshold Adjustment

## Date: 2025-12-26

## Problem
RAG chatbot was returning "I couldn't find relevant information in the textbook to answer your question" for ALL queries, despite:
- Backend running correctly (FastAPI + Uvicorn)
- 913 vectors loaded in Qdrant Cloud collection `textbook_chunks`
- All connections working (Qdrant, OpenRouter, embedding model)
- Debug logging showing query processing

## Root Cause
**Score threshold too high**: The similarity score threshold was set to 0.50 in `app/services/vector_search.py`, which filtered out valid matches. Queries typically score between 0.40-0.65, so a threshold of 0.50 was too restrictive.

## Fix Applied
**File**: `app/services/vector_search.py`
**Lines Changed**: 19, 28

### Change 1: Function Parameter (Line 19)
```python
# BEFORE
score_threshold: float = 0.50,

# AFTER
score_threshold: float = 0.40,
```

### Change 2: Docstring (Line 28)
```python
# BEFORE
score_threshold: Minimum similarity score (default 0.50)

# AFTER
score_threshold: Minimum similarity score (default 0.40)
```

## Expected Impact
- Lowering threshold from 0.50 → 0.40 allows more results through
- Queries scoring 0.40-0.65 will now retrieve relevant chunks
- Should fix the empty retrieval issue causing fallback messages

## Testing Instructions

### 1. Restart Backend
The backend must be restarted to load the changes. From Windows PowerShell:

```powershell
# Stop current backend (Ctrl+C if running)

# Navigate to backend directory
cd E:\phyai-humanoid-textbook\backend\rag-chatbot

# Start backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Wait for startup logs:**
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Test with Live Script
Open a NEW PowerShell window (keep backend running in the first):

```powershell
cd E:\phyai-humanoid-textbook\backend\rag-chatbot
python test_live_retrieval.py
```

**Expected output for "What is ROS 2?" query:**
```
✅ Testing Query: 'What is ROS 2?'
✅ Session created: [session_id]
✅ Stream started (status 200)

📊 Results:
  Chunks retrieved: 5
  Avg confidence: 0.67
✅ TEXTBOOK CONTENT RETURNED!
  Response preview: ROS 2 (Robot Operating System 2) is a next-generation...
  Top citations:
   1. Module1 - Chapter 1: ROS 2 Architecture (0.71)
   2. Module3 - Chapter 1: Introduction to ROS 2 (0.62)
```

### 3. Monitor Backend Logs
While testing, watch backend terminal for `[VECTOR_SEARCH]` debug output:

```
[VECTOR_SEARCH] Generating embedding for query: 'What is ROS 2?'
[VECTOR_SEARCH] ✓ Embedding generated: 384 dimensions
[VECTOR_SEARCH] Searching Qdrant with threshold=0.4, limit=8
[VECTOR_SEARCH] ✓ Qdrant returned 5 results
[VECTOR_SEARCH] Top scores: [0.707, 0.686, 0.615]
```

### 4. Test in Browser
Frontend at `http://localhost:3000`:

1. Open chat widget
2. Send: "What is ROS 2?"
3. **Expected**: Full textbook response with citations
4. **NOT Expected**: "I couldn't find relevant information..."

## Verification Checklist

- [ ] Backend restarted successfully
- [ ] `test_live_retrieval.py` shows "Chunks retrieved: 5" for "What is ROS 2?"
- [ ] Backend logs show `[VECTOR_SEARCH]` output with results
- [ ] Frontend chat widget returns textbook content (not fallback message)
- [ ] Citations appear at bottom of response

## If Still Not Working

### Scenario 1: Backend logs show NO results with threshold=0.4
```
[VECTOR_SEARCH] ✓ Qdrant returned 0 results
[VECTOR_SEARCH] ⚠️ WARNING: No results! Trying with threshold=0.3...
[VECTOR_SEARCH] With threshold=0.3: 5 results
```

**Action**: Lower threshold further to 0.35:
```python
# app/services/vector_search.py line 19
score_threshold: float = 0.35,
```

### Scenario 2: No [VECTOR_SEARCH] logs appear
**Cause**: Backend didn't reload changes

**Action**:
1. Completely stop backend (Ctrl+C)
2. Clear cache: `Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force`
3. Restart: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

### Scenario 3: Results returned but still get fallback
**Cause**: Issue downstream in RAG pipeline

**Action**: Check `app/services/rag.py` for context passing to LLM

## Rollback Instructions
If this fix causes issues, revert to original threshold:

```python
# app/services/vector_search.py line 19
score_threshold: float = 0.50,
```

## Technical Details
- **Collection**: `textbook_chunks`
- **Vectors**: 913 points
- **Embedding Model**: all-MiniLM-L6-v2 (384 dimensions)
- **Qdrant**: Cloud instance at us-east4-0.gcp.cloud.qdrant.io
- **LLM**: mistralai/devstral-2-2512 via OpenRouter
- **Previous Threshold**: 0.50
- **New Threshold**: 0.40
- **Typical Score Range**: 0.40-0.70 for relevant matches

## Related Files
- `app/services/vector_search.py` - Contains the fix
- `app/services/rag.py` - RAG pipeline (fallback trigger at lines 154-160)
- `app/clients/qdrant_client.py` - Qdrant connection
- `test_live_retrieval.py` - Testing script
- `check_qdrant.py` - Qdrant diagnostic script
- `URGENT_FIX.md` - Original diagnosis documentation

## Notes
- Python cache cleared after fix
- Backend MUST be restarted to pick up changes
- Debug logging already in place to monitor retrieval
- If threshold 0.40 still too high, can safely lower to 0.35 or 0.30
