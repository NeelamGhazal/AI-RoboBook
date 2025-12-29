# File Modification Checklist: OpenAI Agents SDK Migration

**Feature**: 001-openai-agents-migration
**Date**: 2025-12-25
**Branch**: 001-openai-agents-migration
**Migration Type**: OpenRouter + Mistral Devstral via Agents SDK

---

## Overview

This checklist provides a **step-by-step guide** for modifying all necessary files to migrate from direct Gemini integration to OpenAI Agents SDK with OpenRouter backend. Follow the phases in order to ensure proper dependency management and minimal disruption.

**Total Files to Modify**: 6
**Total Files to Create**: 2 (test files)
**Total Files to Delete**: 0 (gemini_client.py deprecated but kept for rollback)

---

## Phase 1: Setup and Dependencies

### 1.1 Update Package Dependencies

**File**: `backend/rag-chatbot/requirements.txt`
**Action**: Add OpenAI Agents SDK package
**Priority**: CRITICAL - Must be done first

**Changes**:
```diff
+ openai-agents>=0.1.0
```

**Validation**:
```bash
cd backend/rag-chatbot
pip install -r requirements.txt
python -c "from agents import Agent, Runner, set_default_openai_client; print('✅ Agents SDK installed')"
```

**Estimated LOC**: +1 line

---

### 1.2 Configure Environment Variables

**File**: `backend/rag-chatbot/.env`
**Action**: Add OpenRouter configuration
**Priority**: CRITICAL - Required for client initialization

**Changes**:
```diff
+ # OpenRouter Configuration (for Agents SDK)
+ OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
+ OPENROUTER_MODEL=mistralai/devstral-2512:free
+ BASE_URL=https://openrouter.ai/api/v1
```

**Notes**:
- Replace `sk-or-v1-xxx...` with actual OpenRouter API key
- Model must match OpenRouter's free Devstral model name exactly
- Base URL must include `/api/v1` suffix

**Validation**:
```bash
# Check env vars are set
grep OPENROUTER_API_KEY .env
grep OPENROUTER_MODEL .env
grep BASE_URL .env
```

**Estimated LOC**: +4 lines (with comments)

---

### 1.3 Update Settings Schema

**File**: `backend/rag-chatbot/app/config.py`
**Action**: Add OpenRouter environment variables to Settings model
**Priority**: HIGH - Required before main.py can access settings

**Current Code** (approximate location):
```python
class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    NEON_DATABASE_URL: str | None = None

    # Qdrant
    QDRANT_URL: str
    QDRANT_API_KEY: str | None = None

    # Google/Gemini (deprecated but kept for rollback)
    GOOGLE_API_KEY: str | None = None

    # ... other settings
```

**Changes**:
```diff
class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    NEON_DATABASE_URL: str | None = None

    # Qdrant
    QDRANT_URL: str
    QDRANT_API_KEY: str | None = None

    # Google/Gemini (deprecated but kept for rollback)
    GOOGLE_API_KEY: str | None = None

+   # OpenRouter Configuration (for OpenAI Agents SDK)
+   OPENROUTER_API_KEY: str
+   OPENROUTER_MODEL: str = "mistralai/devstral-2512:free"
+   BASE_URL: str = "https://openrouter.ai/api/v1"

    # ... other settings
```

**Validation**:
```python
from app.config import settings
assert hasattr(settings, 'OPENROUTER_API_KEY')
assert settings.OPENROUTER_MODEL == "mistralai/devstral-2512:free"
assert settings.BASE_URL == "https://openrouter.ai/api/v1"
print("✅ Settings schema updated")
```

**Estimated LOC**: +3 lines

---

## Phase 2: Client Configuration

### 2.1 Configure Global OpenAI Client

**File**: `backend/rag-chatbot/app/main.py`
**Action**: Initialize AsyncOpenAI client with OpenRouter base_url in lifespan startup
**Priority**: CRITICAL - Must be called before any Agent is created
**Line Range**: Approximately lines 25-60 (lifespan context manager)

**Current Code** (lifespan startup section):
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("startup", message="Starting RAG Chatbot API")

    # Initialize Gemini client (deprecated)
    from app.clients.gemini_client import gemini_client
    await gemini_client.initialize()

    # ... other initialization

    yield

    # Shutdown
    logger.info("shutdown", message="Shutting down RAG Chatbot API")
    await gemini_client.close()
```

**Changes**:
```diff
+ from openai import AsyncOpenAI
+ from agents import set_default_openai_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("startup", message="Starting RAG Chatbot API")

+   # Configure OpenAI Agents SDK to use OpenRouter
+   openrouter_client = AsyncOpenAI(
+       api_key=settings.OPENROUTER_API_KEY,
+       base_url=settings.BASE_URL  # Routes to https://openrouter.ai/api/v1
+   )
+   set_default_openai_client(openrouter_client)
+
+   logger.info(
+       "agents_sdk_configured",
+       model=settings.OPENROUTER_MODEL,
+       base_url=settings.BASE_URL,
+       provider="OpenRouter"
+   )

    # Initialize Gemini client (deprecated - kept for emergency rollback)
    from app.clients.gemini_client import gemini_client
    await gemini_client.initialize()

    # ... other initialization

    yield

    # Shutdown
    logger.info("shutdown", message="Shutting down RAG Chatbot API")
    await gemini_client.close()
```

**Notes**:
- `set_default_openai_client()` MUST be called during startup before any Agent is instantiated
- Keep gemini_client initialization but mark as deprecated (enables rollback)
- Log configuration details for observability

**Validation**:
```bash
# Start server and check logs
uvicorn app.main:app --reload
# Expected log: "agents_sdk_configured" with model="mistralai/devstral-2512:free"
```

**Estimated LOC**: +13 lines

---

### 2.2 Switch API Routing

**File**: `backend/rag-chatbot/app/main.py`
**Action**: Change routing from chat_minimal (mock) to chat (real RAG)
**Priority**: CRITICAL - Activates real Agents SDK integration
**Line**: Approximately line 178

**Current Code**:
```python
# Include routers
app.include_router(chat_minimal.router, prefix="/api/v1/chat", tags=["chat"])
# app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])  # Real RAG (disabled)
```

**Changes**:
```diff
# Include routers
- app.include_router(chat_minimal.router, prefix="/api/v1/chat", tags=["chat"])
- # app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])  # Real RAG (disabled)
+ # app.include_router(chat_minimal.router, prefix="/api/v1/chat", tags=["chat"])  # Mock (disabled)
+ app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])  # Real RAG with Agents SDK
```

**Notes**:
- This is the final "switch flip" that activates the Agents SDK integration
- Keep chat_minimal import for easy rollback
- Perform this change LAST after all other files are updated

**Validation**:
```bash
curl -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "What is ROS 2?", "session_id": "test-session"}'
# Expected: Real Qdrant retrieval + Agents SDK response (not mock)
```

**Estimated LOC**: 2 lines changed (comment swap)

---

## Phase 3: RAG Integration with Agents SDK

### 3.1 Create Agent and Update LLM Service

**File**: `backend/rag-chatbot/app/services/llm.py`
**Action**: Replace gemini_client usage with Agents SDK (Agent + Runner)
**Priority**: CRITICAL - Core migration work
**Line Range**: Lines 15-237 (entire file)

**Current Code Structure**:
```python
from app.clients.gemini_client import gemini_client

# System prompt with {context} placeholder
SYSTEM_PROMPT = """You are an expert assistant for the "Physical AI & Humanoid Robotics" textbook.
...
**Textbook Excerpts:**

{context}

Answer the user's question based on these excerpts."""

async def generate_response_stream(...):
    # Format context
    context = format_context(chunks)

    # Build messages
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(context=context)},
        *conversation_history,
        {"role": "user", "content": question}
    ]

    # Stream from Gemini
    async for token in gemini_client.generate_chat_completion_stream(messages, temperature=0.7):
        yield token
```

**Changes**:
```diff
- from app.clients.gemini_client import gemini_client
+ from agents import Agent, Runner
+ from app.config import settings

# System prompt (REMOVE {context} placeholder - context will be in user message)
- SYSTEM_PROMPT = """You are an expert assistant for the "Physical AI & Humanoid Robotics" textbook.
- ...
- **Textbook Excerpts:**
-
- {context}
-
- Answer the user's question based on these excerpts."""

+ SYSTEM_PROMPT = """You are an expert assistant for the "Physical AI & Humanoid Robotics" textbook.
+
+ Your task is to answer questions accurately based ONLY on the textbook excerpts I provide in my messages.
+
+ **Guidelines:**
+ 1. Provide clear, accurate answers citing the textbook content
+ 2. If the answer is not in the provided excerpts, say "This topic is not covered in the available textbook sections."
+ 3. Do not make up information or use knowledge outside the textbook
+ 4. Be concise but thorough
+ 5. Use technical terminology appropriately"""

+ # Create RAG Agent (reusable instance)
+ RAG_AGENT = Agent(
+     name="TextbookRAGAgent",
+     model=settings.OPENROUTER_MODEL,  # "mistralai/devstral-2512:free"
+     instructions=SYSTEM_PROMPT,
+     tools=[]  # No function calling for basic RAG
+ )

async def generate_response_stream(...):
    # Format context
    context = format_context(chunks)

-   # Build messages
-   messages = [
-       {"role": "system", "content": SYSTEM_PROMPT.format(context=context)},
-       *conversation_history,
-       {"role": "user", "content": question}
-   ]

+   # Build user input with context embedded
+   user_input = f"""**Textbook Excerpts:**
+
+ {context}
+
+ **Question:** {question}"""

-   # Stream from Gemini
-   async for token in gemini_client.generate_chat_completion_stream(messages, temperature=0.7):
-       yield token

+   # Stream from Agents SDK
+   try:
+       async for event in Runner.run_stream(
+           agent=RAG_AGENT,
+           input=user_input,
+           context_variables={}  # Not needed for single-agent RAG
+       ):
+           if event.type == "content_delta":
+               yield event.content
+           elif event.type == "error":
+               logger.error("streaming_error", error=event.error)
+               raise RuntimeError(f"Agent streaming error: {event.error}")
+   except Exception as e:
+       logger.error("agent_error", error=str(e), model=settings.OPENROUTER_MODEL)
+       raise
```

**Key Changes**:
1. **Import changes**: Replace gemini_client with agents module imports
2. **System prompt**: Remove `{context}` placeholder (static instruction instead)
3. **Agent creation**: Create RAG_AGENT once at module level (reusable)
4. **Context injection**: Embed context in user message instead of system prompt
5. **Streaming**: Use `Runner.run_stream()` instead of `gemini_client.generate_chat_completion_stream()`
6. **Event handling**: Map `content_delta` events to token yields
7. **Error handling**: Catch and log agent errors with fail-fast behavior

**Validation**:
```python
# Test agent creation
from app.services.llm import RAG_AGENT
assert RAG_AGENT.name == "TextbookRAGAgent"
assert RAG_AGENT.model == "mistralai/devstral-2512:free"
print("✅ Agent created successfully")
```

**Estimated LOC**: ~40 lines changed (system prompt rewrite + streaming logic refactor)

---

### 3.2 Verify Chat Endpoint Compatibility

**File**: `backend/rag-chatbot/app/api/endpoints/chat.py`
**Action**: Verify endpoint uses updated llm.py (minimal/no changes expected)
**Priority**: MEDIUM - Should work with updated llm.py without changes

**Current Code** (approximate):
```python
from app.services.llm import generate_response_stream

@router.post("/stream")
async def stream_chat(...):
    # Retrieve chunks from Qdrant
    chunks = await retrieve_chunks(...)

    # Stream response
    async for token in generate_response_stream(question=message, chunks=chunks, ...):
        yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
```

**Expected Changes**: **NONE** (interface unchanged)

**Validation**:
- `generate_response_stream()` signature remains the same
- Return type (async generator yielding strings) unchanged
- Frontend event format compatibility preserved

**Notes**:
- If chat.py uses hardcoded message history limits, verify it's set to 12 (per clarifications)
- Verify Qdrant top_k retrieval is set to 3 (per FR-006)

**Estimated LOC**: 0 lines changed (validation only)

---

## Phase 4: Testing and Validation

### 4.1 Create Unit Tests for Agents SDK

**File**: `backend/rag-chatbot/tests/test_llm_agents.py` (NEW)
**Action**: Create unit tests mocking Agents SDK
**Priority**: HIGH - Required for CI/CD

**Content**:
```python
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from agents import Runner

@pytest.mark.asyncio
async def test_rag_agent_creation():
    """Test RAG agent is created with correct configuration."""
    from app.services.llm import RAG_AGENT

    assert RAG_AGENT.name == "TextbookRAGAgent"
    assert RAG_AGENT.model == "mistralai/devstral-2512:free"
    assert len(RAG_AGENT.tools) == 0  # No function calling


@pytest.mark.asyncio
async def test_generate_response_stream_with_agents():
    """Test streaming response generation with mocked Agents SDK."""
    from app.services.llm import generate_response_stream

    # Mock Runner.run_stream
    mock_events = [
        MagicMock(type="content_delta", content="Test "),
        MagicMock(type="content_delta", content="response"),
        MagicMock(type="content_done")
    ]

    async def mock_stream(*args, **kwargs):
        for event in mock_events:
            yield event

    with patch.object(Runner, 'run_stream', side_effect=mock_stream):
        chunks = [{"text": "Test chunk", "chapter": "1", "section": "1.1"}]
        tokens = []

        async for token in generate_response_stream(
            question="Test question",
            chunks=chunks,
            conversation_history=[],
            session_id="test-session"
        ):
            tokens.append(token)

        assert "".join(tokens) == "Test response"


@pytest.mark.asyncio
async def test_agents_sdk_error_handling():
    """Test error handling when Agents SDK fails."""
    from app.services.llm import generate_response_stream

    # Mock error event
    mock_error = MagicMock(type="error", error="OpenRouter API error")

    async def mock_stream_error(*args, **kwargs):
        yield mock_error

    with patch.object(Runner, 'run_stream', side_effect=mock_stream_error):
        chunks = [{"text": "Test chunk", "chapter": "1", "section": "1.1"}]

        with pytest.raises(RuntimeError, match="Agent streaming error"):
            async for _ in generate_response_stream(
                question="Test question",
                chunks=chunks,
                conversation_history=[],
                session_id="test-session"
            ):
                pass
```

**Validation**:
```bash
pytest tests/test_llm_agents.py -v
# Expected: All tests pass
```

**Estimated LOC**: +60 lines (new file)

---

### 4.2 Create Integration Tests with Real OpenRouter

**File**: `backend/rag-chatbot/tests/test_integration_openrouter.py` (NEW)
**Action**: Create integration tests using real OpenRouter API
**Priority**: MEDIUM - For local dev validation only

**Content**:
```python
import pytest
from app.services.llm import generate_response_stream

@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_rag_pipeline_with_openrouter():
    """
    Integration test for full RAG pipeline with real OpenRouter API.
    Requires OPENROUTER_API_KEY in environment.
    """
    # Test query
    question = "What is ROS 2?"

    # Mock Qdrant chunks (in real integration test, would retrieve from Qdrant)
    chunks = [
        {
            "text": "ROS 2 (Robot Operating System 2) is a modern robotics middleware...",
            "chapter": "2",
            "section": "2.1",
            "score": 0.95
        },
        {
            "text": "ROS 2 uses DDS (Data Distribution Service) for communication...",
            "chapter": "2",
            "section": "2.2",
            "score": 0.89
        },
        {
            "text": "The ROS 2 architecture supports real-time systems...",
            "chapter": "2",
            "section": "2.3",
            "score": 0.84
        }
    ]

    # Stream response
    response_tokens = []
    async for token in generate_response_stream(
        question=question,
        chunks=chunks,
        conversation_history=[],
        session_id="integration-test"
    ):
        response_tokens.append(token)

    response = "".join(response_tokens)

    # Assertions
    assert len(response) > 50, "Response should be substantial"
    assert "ROS" in response or "Robot Operating System" in response, "Response should mention ROS"

    print(f"\n✅ Integration test passed\nResponse: {response[:200]}...")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_openrouter_quota_handling():
    """Test behavior when OpenRouter quota is exceeded (if applicable)."""
    # This test would require intentionally hitting quota limits
    # For now, just verify error handling structure exists
    pass
```

**Validation**:
```bash
# Run integration tests (requires OPENROUTER_API_KEY)
pytest tests/test_integration_openrouter.py -v -m integration
```

**Estimated LOC**: +50 lines (new file)

---

## Summary Checklist

### Files Modified (6 total)

| File | Phase | Changes | LOC | Priority | Status |
|------|-------|---------|-----|----------|--------|
| `requirements.txt` | 1.1 | Add openai-agents package | +1 | CRITICAL | ☐ |
| `.env` | 1.2 | Add OpenRouter env vars | +4 | CRITICAL | ☐ |
| `app/config.py` | 1.3 | Add Settings fields | +3 | HIGH | ☐ |
| `app/main.py` (lifespan) | 2.1 | Configure AsyncOpenAI client | +13 | CRITICAL | ☐ |
| `app/main.py` (routing) | 2.2 | Switch to chat.router | ±2 | CRITICAL | ☐ |
| `app/services/llm.py` | 3.1 | Replace gemini_client with Agents SDK | ~40 | CRITICAL | ☐ |
| `app/api/endpoints/chat.py` | 3.2 | Verify compatibility (no changes expected) | 0 | MEDIUM | ☐ |

### Files Created (2 total)

| File | Phase | Purpose | LOC | Priority | Status |
|------|-------|---------|-----|----------|--------|
| `tests/test_llm_agents.py` | 4.1 | Unit tests with mocked Agents SDK | +60 | HIGH | ☐ |
| `tests/test_integration_openrouter.py` | 4.2 | Integration tests with real API | +50 | MEDIUM | ☐ |

### Files Deprecated (1 total)

| File | Action | Reason |
|------|--------|--------|
| `app/clients/gemini_client.py` | Keep but mark deprecated | Emergency rollback capability |

---

## Execution Order (Recommended)

Follow this exact order to minimize errors:

1. **Phase 1**: Dependencies and Configuration
   - ☐ 1.1 Update `requirements.txt`
   - ☐ 1.2 Update `.env`
   - ☐ 1.3 Update `app/config.py`
   - ☐ Run `pip install -r requirements.txt`

2. **Phase 2**: Client Configuration
   - ☐ 2.1 Update `app/main.py` lifespan (configure OpenRouter client)
   - ☐ Verify server starts: `uvicorn app.main:app --reload`
   - ☐ Check logs for "agents_sdk_configured" message

3. **Phase 3**: RAG Integration
   - ☐ 3.1 Update `app/services/llm.py` (replace gemini_client)
   - ☐ 3.2 Verify `app/api/endpoints/chat.py` (no changes expected)

4. **Phase 4**: Testing
   - ☐ 4.1 Create `tests/test_llm_agents.py`
   - ☐ 4.2 Create `tests/test_integration_openrouter.py`
   - ☐ Run unit tests: `pytest tests/test_llm_agents.py -v`
   - ☐ Run integration tests: `pytest tests/test_integration_openrouter.py -v -m integration`

5. **Phase 2 (Final)**: Activate Integration
   - ☐ 2.2 Update `app/main.py` routing (switch to chat.router)
   - ☐ Restart server
   - ☐ Test endpoint with curl/Postman

---

## Validation Checklist

After completing all changes, verify:

### Functional Requirements
- ☐ Server starts without errors
- ☐ "agents_sdk_configured" log appears with correct model and base_url
- ☐ POST /api/v1/chat/stream returns real responses (not mock)
- ☐ Responses cite textbook content from Qdrant chunks
- ☐ Streaming works (tokens arrive progressively, not buffered)
- ☐ Qdrant retrieval returns exactly 3 chunks (top_k=3)
- ☐ Conversation history includes last 12 messages (if available)

### Performance Requirements
- ☐ Response time < 5 seconds for typical queries
- ☐ First token arrives within 3 seconds (p90)
- ☐ No visible latency increase vs. direct Gemini (Agents SDK overhead <100ms)

### Error Handling
- ☐ Invalid OPENROUTER_API_KEY causes server startup failure with clear error
- ☐ Network errors to OpenRouter return HTTP 503 with user-friendly message
- ☐ Quota errors (if any) return HTTP 429 with "Service temporarily unavailable"

### Code Quality
- ☐ All unit tests pass
- ☐ Integration tests pass (with valid OPENROUTER_API_KEY)
- ☐ No linting errors
- ☐ No deprecated warnings from Agents SDK

### Rollback Capability
- ☐ `gemini_client.py` still exists (not deleted)
- ☐ Can revert routing to `chat_minimal.router` in <5 minutes
- ☐ .env contains both OPENROUTER_API_KEY and GOOGLE_API_KEY (for emergency fallback)

---

## Troubleshooting Guide

### Issue: Server fails to start with "OPENROUTER_API_KEY not found"
**Solution**:
- Verify `.env` contains `OPENROUTER_API_KEY=sk-or-v1-...`
- Check `app/config.py` has `OPENROUTER_API_KEY: str` field
- Restart server after updating .env

### Issue: "No module named 'agents'"
**Solution**:
- Verify `requirements.txt` has `openai-agents>=0.1.0` (not `openai-agents-sdk`)
- Run `pip install -r requirements.txt`
- Check Python environment: `pip list | grep openai-agents`

### Issue: Responses are still mock data
**Solution**:
- Check `app/main.py` line ~178 uses `chat.router` (not `chat_minimal.router`)
- Restart server after changing routing
- Verify with: `curl -X POST http://localhost:8000/api/v1/chat/stream -d '{"message":"test"}'`

### Issue: "Agent streaming error" in logs
**Solution**:
- Check OPENROUTER_API_KEY is valid (test with curl to OpenRouter directly)
- Verify BASE_URL is exactly `https://openrouter.ai/api/v1` (with `/api/v1` suffix)
- Check network connectivity to openrouter.ai
- Review OpenRouter dashboard for quota/billing issues

### Issue: Responses don't cite textbook content
**Solution**:
- Verify Qdrant retrieval is working: check logs for retrieved chunks
- Confirm `top_k=3` in Qdrant search call
- Check context is embedded in user_input (llm.py)
- Test Qdrant directly with sample query

---

## References

- **Architecture Diagram**: `specs/001-openai-agents-migration/architecture-diagram.md`
- **API Contracts**: `specs/001-openai-agents-migration/contracts/agents_sdk_interface.md`
- **Quickstart Guide**: `specs/001-openai-agents-migration/quickstart.md`
- **Clarifications**: `specs/001-openai-agents-migration/CLARIFICATIONS.md`
- **Research Findings**: `specs/001-openai-agents-migration/research.md`

---

**Checklist Status**: Ready for implementation
**Estimated Total LOC**: ~173 lines changed/added across 8 files
**Estimated Time**: 2-3 hours for experienced developer
**Risk Level**: LOW (simple configuration changes, minimal refactoring)
