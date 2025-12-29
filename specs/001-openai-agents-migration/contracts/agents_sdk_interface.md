# Contract: OpenAI Agents SDK Interface

**Feature**: 001-openai-agents-migration
**Phase**: Phase 1 - Contracts
**Date**: 2025-12-25
**Purpose**: Define the interface contract between our RAG service and the OpenAI Agents SDK

## Contract Overview

This document specifies how the RAG chatbot service will interact with the OpenAI Agents SDK. It serves as the "API contract" between our application layer (`app/services/llm.py`) and the Agents SDK orchestration layer.

---

## 1. Client Configuration Contract

### 1.1 Global OpenAI Client Setup

**Location**: `app/main.py` (lifespan startup)
**Responsibility**: Configure AsyncOpenAI client to use OpenRouter's OpenAI-compatible endpoint

```python
from openai import AsyncOpenAI
from agents import set_default_openai_client
from app.config import settings

# Contract: This MUST be called during app startup before any Agent is created
openrouter_client = AsyncOpenAI(
    api_key=settings.OPENROUTER_API_KEY,  # REQUIRED: Valid OpenRouter API key
    base_url="https://openrouter.ai/api/v1"  # REQUIRED: OpenRouter base URL
)

set_default_openai_client(openrouter_client)
```

**Preconditions**:
- `OPENROUTER_API_KEY` environment variable is set and valid
- `openai` package version >=1.51.0 installed
- `openai-agents` package version >=0.1.0 installed

**Postconditions**:
- All Agent instances created after this call will use the OpenRouter endpoint
- No OpenAI API key or credits required
- Requests routed to Mistral Devstral free model

**Error Handling**:
- If `OPENROUTER_API_KEY` is missing or invalid, startup MUST fail with clear error message
- If base_url is unreachable, startup SHOULD warn but MAY proceed (degrade gracefully)

---

## 2. Agent Definition Contract

### 2.1 RAG Agent Configuration

**Location**: `app/services/llm.py`
**Responsibility**: Define the textbook RAG agent with system prompt and model

```python
from agents import Agent

# Contract: This agent MUST be created once and reused across requests
RAG_AGENT = Agent(
    name="TextbookRAGAgent",  # REQUIRED: Unique identifier for logs
    instructions=SYSTEM_PROMPT,  # REQUIRED: System prompt template (see 2.2)
    model="gemini-1.5-flash",  # REQUIRED: Must match Gemini model name
    tools=[]  # REQUIRED: Empty list (no function calling for basic RAG)
)
```

**Preconditions**:
- `set_default_openai_client()` has been called (see 1.1)
- `SYSTEM_PROMPT` is a non-empty string (see 2.2)

**Postconditions**:
- Agent is ready to process requests via `Runner.run()` or `Runner.run_stream()`
- Agent will use the Gemini endpoint configured in 1.1

**Performance**: Agent creation is lightweight (~1ms). Can be created once at module import time.

### 2.2 System Prompt Template

**Contract**: The `instructions` field MUST contain the RAG system prompt with placeholders for context injection.

```python
# Current system prompt (app/services/llm.py:15-31)
SYSTEM_PROMPT = """You are an expert assistant for the "Physical AI & Humanoid Robotics" textbook.

Your task is to answer questions accurately based ONLY on the provided textbook excerpts below.

**Guidelines:**
1. Provide clear, accurate answers citing the textbook content
2. If the answer is not in the provided excerpts, say "This topic is not covered in the available textbook sections."
3. Do not make up information or use knowledge outside the textbook
4. Be concise but thorough
5. Use technical terminology appropriately

**Textbook Excerpts:**

{context}

Answer the user's question based on these excerpts."""
```

**Migration Note**: This template will be **modified** to remove `{context}` placeholder since Agents SDK expects a static instruction. Context will be passed as a user message instead (see 3.2).

**Revised System Prompt** (post-migration):
```python
SYSTEM_PROMPT = """You are an expert assistant for the "Physical AI & Humanoid Robotics" textbook.

Your task is to answer questions accurately based ONLY on the textbook excerpts I provide in my messages.

**Guidelines:**
1. Provide clear, accurate answers citing the textbook content
2. If the answer is not in the provided excerpts, say "This topic is not covered in the available textbook sections."
3. Do not make up information or use knowledge outside the textbook
4. Be concise but thorough
5. Use technical terminology appropriately"""
```

---

## 3. Invocation Contract (Non-Streaming)

### 3.1 Basic RAG Request

**Function**: `generate_response()` in `app/services/llm.py:112-173`

**Before (Direct Gemini)**:
```python
response = await gemini_client.generate_chat_completion(
    messages=messages,
    temperature=0.7
)
```

**After (Agents SDK)**:
```python
from agents import Runner

# Build input message with context + question
user_input = f"""**Textbook Excerpts:**

{context}

**Question:** {question}"""

# Run agent
result = await Runner.run(
    agent=RAG_AGENT,
    input=user_input,
    context_variables={}  # Not needed for this use case
)

response = result.final_output
```

**Input Contract**:
- `agent`: Agent instance (created in 2.1)
- `input`: str (formatted user message with context + question)
- `context_variables`: dict (optional, used for multi-agent handoffs - not needed)

**Output Contract**:
- `result.final_output`: str (LLM response text)
- `result.messages`: List[dict] (conversation history, compatible with Message model)

**Error Contract**:
- If Gemini API quota exceeded, raises `openai.RateLimitError`
- If network error, raises `openai.APIConnectionError`
- Errors MUST be caught and logged in `app/services/llm.py`

---

## 4. Invocation Contract (Streaming)

### 4.1 Streaming RAG Request

**Function**: `generate_response_stream()` in `app/services/llm.py:176-237`

**Before (Direct Gemini)**:
```python
async for token in gemini_client.generate_chat_completion_stream(
    messages=messages,
    temperature=0.7
):
    yield token
```

**After (Agents SDK)**:
```python
from agents import Runner

user_input = f"""**Textbook Excerpts:**

{context}

**Question:** {question}"""

async for event in Runner.run_stream(
    agent=RAG_AGENT,
    input=user_input,
    context_variables={}
):
    if event.type == "content_delta":
        yield event.content
    elif event.type == "error":
        logger.error("streaming_error", error=event.error)
        raise RuntimeError(event.error)
```

**Input Contract**:
- Same as 3.1 (agent, input, context_variables)

**Output Contract** (Event Stream):

| Event Type | Fields | Description |
|------------|--------|-------------|
| `content_delta` | `event.content: str` | Token/chunk of response text |
| `content_done` | - | Response generation complete |
| `error` | `event.error: str` | Error occurred during generation |
| `agent_message` | `event.message: dict` | Full assistant message (role + content) |

**Mapping to Frontend Format**:

```python
# Frontend expects: {"type": "token", "content": "..."}
# Agents SDK provides: event.type == "content_delta", event.content == "..."

async for event in Runner.run_stream(...):
    if event.type == "content_delta":
        # Map to frontend format
        yield {"type": "token", "content": event.content}
```

**Performance Contract**:
- First token MUST arrive within 3 seconds (p90) - spec SC-004
- Streaming MUST NOT buffer (immediate forwarding of tokens)

---

## 5. Message Format Contract

### 5.1 Conversation History Compatibility

**Current Format** (stored in Postgres `messages` table):
```python
{
    "role": "user" | "assistant",
    "content": str
}
```

**Agents SDK Format** (OpenAI Chat Completions API):
```python
{
    "role": "user" | "assistant" | "system",
    "content": str
}
```

**Contract**: ✅ 100% compatible. No conversion needed.

**Evidence**: Agents SDK uses standard OpenAI message format, which our Message model already follows.

### 5.2 Context Injection Strategy

**Before**: Context injected into system prompt via `SYSTEM_PROMPT.format(context=context)`

**After**: Context injected as part of user message:

```python
# Option A: Single user message with context + question (SELECTED)
user_input = f"""**Textbook Excerpts:**

{context}

**Question:** {question}"""

# Option B: Separate system message (NOT SELECTED - would require changing Agent.instructions per request)
# This is inefficient since Agent is meant to be reused
```

**Rationale**: Agents SDK expects `instructions` to be static per Agent instance. Dynamic context should be passed in the user input, not system prompt.

---

## 6. Error Handling Contract

### 6.1 Error Types

| Error | Cause | HTTP Status | User Message |
|-------|-------|-------------|--------------|
| `openai.RateLimitError` | OpenRouter rate limiting (rare with free models) | 429 | "Service temporarily unavailable. Please try again in a few minutes." |
| `openai.APIConnectionError` | Network failure to OpenRouter | 503 | "Unable to connect to the chatbot service. Please check your connection." |
| `openai.AuthenticationError` | Invalid OPENROUTER_API_KEY | 500 | "Configuration error. Please contact support." |
| `openai.BadRequestError` | Malformed request or unsupported model parameter | 400 | "Invalid request format." |
| `RuntimeError` (from event.type=="error") | Streaming generation error | 500 | "An error occurred while generating the response." |

### 6.2 Error Propagation

```python
try:
    result = await Runner.run(agent=RAG_AGENT, input=user_input)
except openai.RateLimitError as e:
    logger.warning("gemini_rate_limit", error=str(e))
    raise HTTPException(status_code=429, detail="Service temporarily unavailable")
except openai.APIConnectionError as e:
    logger.error("gemini_connection_error", error=str(e))
    raise HTTPException(status_code=503, detail="Unable to connect to service")
except Exception as e:
    logger.error("unexpected_agent_error", error=str(e))
    raise HTTPException(status_code=500, detail="Internal server error")
```

---

## 7. Logging Contract

### 7.1 Required Logs

**Agent Initialization**:
```python
logger.info(
    "agents_sdk_configured",
    model="mistralai/devstral-2512:free",
    base_url="https://openrouter.ai/api/v1",
    agent_name="TextbookRAGAgent",
    provider="OpenRouter"
)
```

**Request Processing**:
```python
logger.info(
    "agent_request_started",
    question_length=len(question),
    context_length=len(context),
    stream=True
)
```

**Response Completion**:
```python
logger.info(
    "agent_response_complete",
    response_length=len(response),
    estimated_tokens=count_tokens(response),
    duration_ms=int((time.time() - start_time) * 1000)
)
```

**Error Logging**:
```python
logger.error(
    "agent_error",
    error_type=type(e).__name__,
    error_message=str(e),
    question_length=len(question),
    provider="OpenRouter",
    model="mistralai/devstral-2512:free"
)
```

### 7.2 Metrics Contract

**Preserve Existing Metrics** (Prometheus):
- `GENERATION_DURATION` - Histogram of response generation time
- `REQUEST_DURATION` - Total request latency
- `ERROR_COUNTER` - Count of errors by type

**Add New Metric** (optional):
- `AGENTS_SDK_OVERHEAD` - Gauge tracking Agents SDK vs. direct LLM overhead (for debugging)

---

## 8. Testing Contract

### 8.1 Unit Test Contract

**Mock the Agents SDK Runner**:
```python
import pytest
from unittest.mock import AsyncMock, patch
from agents import Runner

@pytest.mark.asyncio
async def test_generate_response_with_agents():
    # Mock Runner.run
    mock_result = AsyncMock()
    mock_result.final_output = "Test response"
    mock_result.messages = [
        {"role": "user", "content": "Test question"},
        {"role": "assistant", "content": "Test response"}
    ]

    with patch.object(Runner, 'run', return_value=mock_result):
        response, tokens = await generate_response(
            question="Test question",
            chunks=[{"text": "Test chunk", "chapter": "1", "section": "1.1"}]
        )

    assert response == "Test response"
    assert tokens > 0
```

### 8.2 Integration Test Contract

**Test with Real OpenRouter Endpoint** (local dev only):
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_rag_pipeline_with_real_openrouter():
    # Requires OPENROUTER_API_KEY in .env.test
    # Verifies full RAG flow: retrieve → context → Agent (OpenRouter) → stream → citations
    result = await execute_rag_pipeline(
        question="What is ROS 2?",
        top_k=3,  # Hardcoded: retrieve top 3 chunks
        stream=False
    )

    response, citations, metadata = result
    assert len(response) > 0
    assert len(citations) > 0
    assert len(citations) <= 3  # Max 3 chunks
    assert metadata["total_time_ms"] < 3000  # <3 sec requirement
```

---

## 9. Migration Path Contract

### 9.1 Backward Compatibility

**Requirement**: The migration MUST NOT break existing functionality.

**Validation Checklist**:
- [x] Message model format unchanged (role + content)
- [x] API request/response schemas unchanged
- [x] Streaming event format compatible (map content_delta → token)
- [x] Error responses unchanged (same HTTP status codes)
- [x] Logging structure preserved (same fields + new Agents SDK fields)

### 9.2 Rollback Plan

If Agents SDK integration fails in production:

1. **Immediate Rollback**: Switch `main.py` routing back to `chat_minimal.py`
2. **Full Rollback**: Revert `llm.py` changes, restore direct `gemini_client` usage (deprecated but kept)
3. **Validation**: Run health check endpoint to verify direct Gemini client works

**Rollback SLA**: <5 minutes (simple routing change in `main.py:178`)

**Note**: Post-migration, `gemini_client.py` remains in codebase but unused. Can be re-enabled for emergency rollback if OpenRouter experiences downtime.

---

## 10. Compliance Checklist

This contract ensures compliance with feature spec requirements:

- [x] **FR-001**: Uses openai.agents module exclusively ✅
- [x] **FR-002**: Custom LLM adapter pattern via set_default_openai_client ✅
- [x] **FR-003**: No legacy openai.OpenAI client usage ✅
- [x] **FR-004**: RAG pipeline flow maintained ✅
- [x] **FR-007**: Streaming support via Runner.run_stream ✅
- [x] **FR-012**: Frontend compatibility preserved (event format mapping) ✅
- [x] **SC-004**: <3 second response time (Gemini endpoint overhead minimal) ✅

---

## Summary

This contract defines the **minimal interface changes** needed to integrate the Agents SDK while preserving all existing functionality. The key insight is that Gemini's OpenAI-compatible endpoint + `set_default_openai_client()` provides seamless SDK compliance without requiring custom adapter classes.

**Next**: Proceed to `quickstart.md` to document developer setup steps.
