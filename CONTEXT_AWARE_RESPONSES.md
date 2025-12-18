# Context-Aware Responses for Selected Text

**Date**: 2025-12-18
**Status**: ✅ IMPLEMENTED - Selected text mode with context-aware responses

---

## Feature Overview

The chat widget now provides different responses based on whether the user selected text:

- **General Query Mode**: User types question without selecting text → General response
- **Context-Aware Mode**: User selects text + asks question → Response specific to selected text

---

## Implementation Details

### Backend: `app/api/v1/chat_minimal.py`

**Enhanced endpoint logic**:

```python
# Parse request
selected_text = body.get("selected_text", None)

if selected_text:
    print(f"[Backend] ✓ Context-aware mode (selected text provided)")
    print(f"[Backend] Selected text length: {len(selected_text)} chars")

    # Build context-aware response
    response_parts = [
        "Based on the text you selected:\n\n",
        f"--- Selected Text ---\n{selected_text}\n--- End ---\n\n",
        f"You asked: \"{question}\"\n\n",
        "Let me explain this section for you:\n\n",
        # ... context-specific explanation
    ]
else:
    print(f"[Backend] ℹ️ General query mode (no selected text)")

    # Build general response
    response_parts = [
        "Hello! ",
        f"You asked: \"{question}\"\n\n",
        # ... general response
    ]
```

**Key changes**:
1. ✅ Checks for `selected_text` in request body
2. ✅ Logs mode (context-aware vs general)
3. ✅ Different response logic based on mode
4. ✅ Includes selected text in response for context
5. ✅ Citations reference selected text when applicable

### Frontend: `api/chatApi.ts`

**Enhanced logging**:

```typescript
console.log('[ChatApi] Request payload:', {
  session_id: request.session_id,
  question_length: request.question.length,
  has_selected_text: !!request.selected_text,
  selected_text_length: request.selected_text?.length || 0,
});

if (request.selected_text) {
  console.log('[ChatApi] ✓ Selected text mode enabled');
  console.log('[ChatApi] Selected text preview:', request.selected_text.substring(0, 100) + '...');
}
```

**Payload sent**:
```json
{
  "session_id": "abc-123",
  "question": "explain this",
  "selected_text": "Module 2: Simulation (Gazebo/Unity)..."  // Optional
}
```

---

## User Flow

### Scenario 1: General Query (No Selected Text)

**User action**:
1. Opens chat widget
2. Types: "What is ROS 2?"
3. Presses send

**Backend logs**:
```
[Backend] ✓✓✓ POST /stream endpoint called!
[Backend] Session ID: abc-123
[Backend] Question: What is ROS 2?
[Backend] ℹ️ General query mode (no selected text)
[Backend] Starting token generation...
[Backend] Generating general response...
```

**Response includes**:
- General greeting
- Answer to the question
- Suggestion to try selected text mode
- General citations

**Example response**:
```
Hello! You asked: "What is ROS 2?"

This is a general query response. I'm ready to help you understand the Physical AI & Humanoid Robotics textbook!

[In production, the RAG pipeline would search the entire document and provide relevant information based on your question.]

💡 Pro tip: For more specific answers, try selecting text from the documentation and clicking 'Ask about this'. This enables context-aware responses tailored to the exact section you're reading!

Feel free to ask any questions about ROS 2, simulation, hardware, or any other topics covered in the book.
```

---

### Scenario 2: Context-Aware Query (With Selected Text)

**User action**:
1. Selects text: "Module 2: Simulation (Gazebo/Unity)\nThis module covers simulation environments..."
2. Clicks "Ask about this" button
3. Chat opens with selected text pre-loaded
4. Types: "explain this module"
5. Presses send

**Frontend logs**:
```
[ChatApi] ✓ Selected text mode enabled
[ChatApi] Selected text preview: Module 2: Simulation (Gazebo/Unity)...
[ChatApi] Starting stream request to: http://localhost:8000/api/v1/chat/stream
```

**Backend logs**:
```
[Backend] ✓✓✓ POST /stream endpoint called!
[Backend] Session ID: abc-123
[Backend] Question: explain this module
[Backend] ✓ Context-aware mode (selected text provided)
[Backend] Selected text length: 250 chars
[Backend] Selected text preview: Module 2: Simulation (Gazebo/Unity)
This module covers simulation environments...
[Backend] Starting token generation...
[Backend] Generating context-aware response...
```

**Response includes**:
- Acknowledgment of selected text
- Display of selected text
- Context-specific explanation
- References to selected passage
- Contextual citations

**Example response**:
```
Based on the text you selected:

--- Selected Text ---
Module 2: Simulation (Gazebo/Unity)
This module covers simulation environments for testing humanoid robots before deployment...
--- End ---

You asked: "explain this module"

Let me explain this section for you:

This text discusses important concepts related to your question. The selected passage (approximately 250 characters) contains key information.

Here's a detailed explanation:
[In production, the RAG pipeline would analyze the selected text and provide a context-specific answer based on the broader document context.]

The selected text is particularly relevant because it appears in a section covering these topics. Would you like me to explain any specific part in more detail, or discuss how this relates to other sections?

💡 Tip: You can select any text in the documentation and ask specific questions about it for targeted explanations!
```

**Citations**:
```json
[
  {
    "source": "Selected Text Context",
    "page": 0,
    "text": "Module 2: Simulation (Gazebo/Unity)\nThis module covers simulation environments...",
    "confidence_score": 0.95
  },
  {
    "source": "Textbook Context",
    "page": 1,
    "text": "Additional context from the broader document...",
    "confidence_score": 0.85
  }
]
```

---

## Testing Instructions

### Test 1: General Query Mode

**Steps**:
1. Start backend: `uvicorn app.main:app --reload`
2. Start frontend: `npm start`
3. Open chat widget
4. Type: "What is ROS 2?"
5. Send

**Expected backend logs**:
```
[Backend] ℹ️ General query mode (no selected text)
[Backend] Generating general response...
```

**Expected response**:
- General greeting
- Suggestion to try selected text mode
- No selected text display

---

### Test 2: Context-Aware Mode

**Steps**:
1. Backend and frontend running
2. Navigate to documentation page
3. **Select text**: "Module 2: Simulation (Gazebo/Unity)"
4. Click "Ask about this" button (should appear above selection)
5. Chat opens with selected text
6. Type: "explain it"
7. Send

**Expected frontend logs**:
```
[ChatApi] ✓ Selected text mode enabled
[ChatApi] Selected text preview: Module 2: Simulation (Gazebo/Unity)...
```

**Expected backend logs**:
```
[Backend] ✓ Context-aware mode (selected text provided)
[Backend] Selected text length: 37 chars
[Backend] Selected text preview: Module 2: Simulation (Gazebo/Unity)...
[Backend] Generating context-aware response...
```

**Expected response**:
- "Based on the text you selected:"
- Display of selected text
- Context-specific explanation
- Reference to selected passage
- 2 citations (selected text + context)

---

### Test 3: Switching Between Modes

**Steps**:
1. Send general query: "What is ROS?"
2. Select text: "Chapter 3: Hardware"
3. Click "Ask about this"
4. Send: "tell me more"
5. Clear chat
6. Send general query again: "What is Gazebo?"

**Expected**:
- First query: General mode
- Second query: Context-aware mode (shows selected text)
- Third query: General mode again

---

## Manual Testing with curl

### Test General Mode
```bash
curl -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-123",
    "question": "What is ROS 2?"
  }'
```

**Expected in output**:
```
data: {"type":"token","content":"Hello! "}
data: {"type":"token","content":"You asked: \"What is ROS 2?\"\n\n"}
data: {"type":"token","content":"This is a general query response. "}
...
```

### Test Context-Aware Mode
```bash
curl -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-123",
    "question": "explain this",
    "selected_text": "Module 2: Simulation (Gazebo/Unity)"
  }'
```

**Expected in output**:
```
data: {"type":"token","content":"Based on the text you selected:\n\n"}
data: {"type":"token","content":"--- Selected Text ---\nModule 2: Simulation (Gazebo/Unity)\n--- End ---\n\n"}
data: {"type":"token","content":"You asked: \"explain this\"\n\n"}
...
```

**Backend logs should show**:
```
[Backend] ✓ Context-aware mode (selected text provided)
[Backend] Selected text length: 37 chars
```

---

## Code Comparison

### General Mode vs Context-Aware Mode

| Aspect | General Mode | Context-Aware Mode |
|--------|--------------|-------------------|
| **Request** | No `selected_text` | Has `selected_text` field |
| **Backend Log** | "General query mode" | "Context-aware mode" |
| **Response Start** | "Hello! You asked:" | "Based on the text you selected:" |
| **Content** | Generic answer | Selected text + explanation |
| **Citations** | General knowledge | Selected text reference |
| **Length** | Shorter | Longer (includes selected text) |

---

## Expected Console Output Examples

### Frontend Console (Context-Aware)

```
[ChatApi] ✓ Selected text mode enabled
[ChatApi] Selected text preview: Module 2: Simulation (Gazebo/Unity)...
[ChatApi] Starting stream request to: http://localhost:8000/api/v1/chat/stream
[ChatApi] Request payload: {
  session_id: "abc-123",
  question_length: 10,
  has_selected_text: true,
  selected_text_length: 37
}
[ChatApi] Stream response status: 200 OK
[ChatApi] First raw event data: {"type":"token","content":"Based on the text you selected:\n\n"}
[ChatApi] Token #1: Based on the text you selected:

[ChatStream] Received event: token
[ChatStream] Token added, full response length: 37
```

### Backend Console (Context-Aware)

```
==================================================
[Backend] ✓✓✓ POST /stream endpoint called!
==================================================
[Backend] Session ID: abc-123
[Backend] Question: explain it
[Backend] ✓ Context-aware mode (selected text provided)
[Backend] Selected text length: 37 chars
[Backend] Selected text preview: Module 2: Simulation (Gazebo/Unity)...
[Backend] Starting token generation...
[Backend] Generating context-aware response...
[Backend] Sent 1/11 chunks
[Backend] Sent 4/11 chunks
[Backend] Sent 7/11 chunks
[Backend] Sent 10/11 chunks
[Backend] Sent 2 citations
[Backend] ✓ Stream completed successfully!
[Backend] Context-aware response delivered for 37 char selection
==================================================
```

---

## Integration with RAG Pipeline (Future)

The current implementation uses placeholder responses. When integrating with the real RAG pipeline:

```python
if selected_text:
    # Use selected text as context for retrieval
    async for event in execute_rag_pipeline_stream(
        question=question,
        conversation_history=messages,
        selected_text=selected_text,  # Pass to RAG
        top_k=8,
    ):
        yield f'data: {json.dumps(event)}\n\n'
else:
    # Standard RAG retrieval without selected text context
    async for event in execute_rag_pipeline_stream(
        question=question,
        conversation_history=messages,
        top_k=8,
    ):
        yield f'data: {json.dumps(event)}\n\n'
```

---

## Summary

**Changes made**:
- ✅ Backend checks for `selected_text` field
- ✅ Different response logic for context-aware vs general
- ✅ Selected text included in response
- ✅ Enhanced logging for both modes
- ✅ Citations reference selected text
- ✅ Frontend logging shows mode

**User benefits**:
- 📚 General queries get broad answers
- 🎯 Selected text queries get focused, contextual explanations
- 💡 Clear guidance on when to use each mode

**Files modified**:
- `backend/rag-chatbot/app/api/v1/chat_minimal.py`
- `frontend/src/components/ChatWidget/api/chatApi.ts`

**Status**: ✅ Ready to test with selected text feature!
