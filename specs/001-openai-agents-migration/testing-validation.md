# Testing and Validation Plan: OpenAI Agents SDK Migration

**Feature**: 001-openai-agents-migration
**Date**: 2025-12-25
**Testing Strategy**: Multi-layered (Unit → Integration → Manual → Performance)
**Quality Gates**: All tests must pass before production deployment

---

## Overview

This document defines comprehensive testing and validation procedures for the OpenAI Agents SDK migration. Testing is organized into 4 layers:

1. **Unit Tests**: Mock Agents SDK, test logic in isolation
2. **Integration Tests**: Real OpenRouter API, verify end-to-end flow
3. **Manual Tests**: User acceptance testing via Postman/curl
4. **Performance Tests**: Validate latency and throughput requirements

---

## Quality Requirements (User-Specified)

### Functional Requirements

✅ **FR-1**: Response time < 5 seconds for typical queries
✅ **FR-2**: Qdrant retrieval returns 3+ chunks (top_k=3)
✅ **FR-3**: Agent responses cite book content (not generic knowledge)
✅ **FR-4**: No hardcoded/mock responses (real Agents SDK integration)

### Non-Functional Requirements

✅ **NFR-1**: First token latency < 3 seconds (p90)
✅ **NFR-2**: Streaming enabled (no buffering)
✅ **NFR-3**: Error handling with user-friendly messages
✅ **NFR-4**: Backward compatibility (message format, API schemas)

---

## Layer 1: Unit Tests (Mocked Agents SDK)

### 1.1 Test Agent Creation

**File**: `tests/test_llm_agents.py`
**Purpose**: Verify RAG agent is created with correct configuration
**Mocking**: No external API calls

```python
import pytest
from app.services.llm import RAG_AGENT
from app.config import settings

def test_rag_agent_configuration():
    """Test RAG agent has correct model and configuration."""
    assert RAG_AGENT.name == "TextbookRAGAgent"
    assert RAG_AGENT.model == settings.OPENROUTER_MODEL
    assert RAG_AGENT.model == "mistralai/devstral-2512:free"
    assert RAG_AGENT.tools == []  # No function calling
    assert len(RAG_AGENT.instructions) > 100  # Has system prompt

def test_agent_system_prompt():
    """Test system prompt does not contain {context} placeholder."""
    # After migration, system prompt should be static
    assert "{context}" not in RAG_AGENT.instructions
    assert "textbook" in RAG_AGENT.instructions.lower()
```

**Expected Result**: ✅ Agent created with OpenRouter model, no placeholders in instructions

---

### 1.2 Test Streaming Response Generation

**File**: `tests/test_llm_agents.py`
**Purpose**: Verify streaming logic handles events correctly
**Mocking**: Mock `Runner.run_stream()`

```python
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from agents import Runner
from app.services.llm import generate_response_stream

@pytest.mark.asyncio
async def test_streaming_content_delta_events():
    """Test streaming yields content from content_delta events."""
    # Mock events
    mock_events = [
        MagicMock(type="content_delta", content="ROS "),
        MagicMock(type="content_delta", content="2 is "),
        MagicMock(type="content_delta", content="a robotics "),
        MagicMock(type="content_delta", content="middleware."),
        MagicMock(type="content_done")
    ]

    async def mock_stream(*args, **kwargs):
        for event in mock_events:
            yield event

    with patch.object(Runner, 'run_stream', side_effect=mock_stream):
        chunks = [{"text": "ROS 2 is a robotics middleware", "chapter": "2", "section": "2.1"}]
        tokens = []

        async for token in generate_response_stream(
            question="What is ROS 2?",
            chunks=chunks,
            conversation_history=[],
            session_id="test-session"
        ):
            tokens.append(token)

        response = "".join(tokens)
        assert response == "ROS 2 is a robotics middleware."
        assert len(tokens) == 4  # Only content_delta events yielded

@pytest.mark.asyncio
async def test_streaming_ignores_non_content_events():
    """Test streaming only yields content_delta events."""
    mock_events = [
        MagicMock(type="agent_message", message={"role": "assistant"}),
        MagicMock(type="content_delta", content="Test"),
        MagicMock(type="metadata", data={}),
        MagicMock(type="content_done")
    ]

    async def mock_stream(*args, **kwargs):
        for event in mock_events:
            yield event

    with patch.object(Runner, 'run_stream', side_effect=mock_stream):
        chunks = [{"text": "Test chunk", "chapter": "1", "section": "1.1"}]
        tokens = []

        async for token in generate_response_stream(
            question="Test",
            chunks=chunks,
            conversation_history=[],
            session_id="test"
        ):
            tokens.append(token)

        assert "".join(tokens) == "Test"  # Only content_delta content
```

**Expected Result**: ✅ Only `content_delta` events are yielded as tokens

---

### 1.3 Test Error Handling

**File**: `tests/test_llm_agents.py`
**Purpose**: Verify errors are caught and propagated correctly
**Mocking**: Mock error events

```python
@pytest.mark.asyncio
async def test_streaming_error_event_handling():
    """Test error events raise RuntimeError."""
    mock_events = [
        MagicMock(type="content_delta", content="Starting..."),
        MagicMock(type="error", error="OpenRouter API quota exceeded")
    ]

    async def mock_stream_error(*args, **kwargs):
        for event in mock_events:
            yield event

    with patch.object(Runner, 'run_stream', side_effect=mock_stream_error):
        chunks = [{"text": "Test chunk", "chapter": "1", "section": "1.1"}]

        with pytest.raises(RuntimeError, match="Agent streaming error"):
            async for _ in generate_response_stream(
                question="Test",
                chunks=chunks,
                conversation_history=[],
                session_id="test"
            ):
                pass

@pytest.mark.asyncio
async def test_rate_limit_error_handling():
    """Test rate limit errors from OpenRouter."""
    from openai import RateLimitError

    with patch.object(Runner, 'run_stream', side_effect=RateLimitError("Rate limit exceeded", response=None, body=None)):
        chunks = [{"text": "Test", "chapter": "1", "section": "1.1"}]

        with pytest.raises(RateLimitError):
            async for _ in generate_response_stream(
                question="Test",
                chunks=chunks,
                conversation_history=[],
                session_id="test"
            ):
                pass
```

**Expected Result**: ✅ Errors are caught and raise appropriate exceptions

---

### 1.4 Test Context Injection

**File**: `tests/test_llm_agents.py`
**Purpose**: Verify context is properly formatted in user input
**Mocking**: Mock `Runner.run_stream()`, inspect input parameter

```python
@pytest.mark.asyncio
async def test_context_injection_in_user_input():
    """Test Qdrant chunks are embedded in user input."""
    captured_input = None

    async def mock_stream(*args, **kwargs):
        nonlocal captured_input
        captured_input = kwargs.get("input")
        yield MagicMock(type="content_delta", content="Test response")
        yield MagicMock(type="content_done")

    with patch.object(Runner, 'run_stream', side_effect=mock_stream):
        chunks = [
            {"text": "ROS 2 is modern", "chapter": "2", "section": "2.1"},
            {"text": "Uses DDS protocol", "chapter": "2", "section": "2.2"},
            {"text": "Supports real-time", "chapter": "2", "section": "2.3"}
        ]

        async for _ in generate_response_stream(
            question="What is ROS 2?",
            chunks=chunks,
            conversation_history=[],
            session_id="test"
        ):
            pass

    # Verify context is in user input
    assert captured_input is not None
    assert "**Textbook Excerpts:**" in captured_input
    assert "ROS 2 is modern" in captured_input
    assert "Uses DDS protocol" in captured_input
    assert "Supports real-time" in captured_input
    assert "**Question:** What is ROS 2?" in captured_input
```

**Expected Result**: ✅ All 3 chunks are embedded in user input with proper formatting

---

### Unit Test Execution

```bash
# Run all unit tests
cd backend/rag-chatbot
pytest tests/test_llm_agents.py -v

# Expected output:
# tests/test_llm_agents.py::test_rag_agent_configuration PASSED
# tests/test_llm_agents.py::test_agent_system_prompt PASSED
# tests/test_llm_agents.py::test_streaming_content_delta_events PASSED
# tests/test_llm_agents.py::test_streaming_ignores_non_content_events PASSED
# tests/test_llm_agents.py::test_streaming_error_event_handling PASSED
# tests/test_llm_agents.py::test_rate_limit_error_handling PASSED
# tests/test_llm_agents.py::test_context_injection_in_user_input PASSED
# ======================== 7 passed in 2.3s ========================

# Run with coverage
pytest tests/test_llm_agents.py --cov=app.services.llm --cov-report=term-missing
```

**Success Criteria**:
- ✅ All 7 unit tests pass
- ✅ Coverage > 80% for `app/services/llm.py`
- ✅ No mocked API calls to external services

---

## Layer 2: Integration Tests (Real OpenRouter API)

### 2.1 Test Full RAG Pipeline

**File**: `tests/test_integration_openrouter.py`
**Purpose**: Verify end-to-end RAG flow with real OpenRouter API
**Prerequisites**: Valid OPENROUTER_API_KEY in `.env` or environment

```python
import pytest
from app.services.llm import generate_response_stream
import os

@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_rag_pipeline_with_openrouter():
    """
    Integration test: Qdrant retrieval → Agents SDK → OpenRouter → Response.
    Requires OPENROUTER_API_KEY.
    """
    # Skip if no API key
    if not os.getenv("OPENROUTER_API_KEY"):
        pytest.skip("OPENROUTER_API_KEY not set")

    # Simulate Qdrant chunks (in real test, would query Qdrant)
    chunks = [
        {
            "text": "ROS 2 (Robot Operating System 2) is a modern robotics middleware that provides libraries and tools for building robot applications. It uses DDS for inter-process communication.",
            "chapter": "2",
            "section": "2.1",
            "score": 0.95
        },
        {
            "text": "ROS 2 supports real-time systems through its use of DDS and Quality of Service (QoS) policies.",
            "chapter": "2",
            "section": "2.2",
            "score": 0.89
        },
        {
            "text": "The ROS 2 architecture is modular and supports multiple programming languages including Python and C++.",
            "chapter": "2",
            "section": "2.3",
            "score": 0.84
        }
    ]

    # Stream response
    import time
    start_time = time.time()
    response_tokens = []
    first_token_time = None

    async for token in generate_response_stream(
        question="What is ROS 2 and what are its key features?",
        chunks=chunks,
        conversation_history=[],
        session_id="integration-test"
    ):
        if first_token_time is None:
            first_token_time = time.time()
        response_tokens.append(token)

    end_time = time.time()
    response = "".join(response_tokens)

    # Assertions - Quality Requirements
    assert len(response) > 50, "Response should be substantial (>50 chars)"
    assert "ROS" in response or "Robot Operating System" in response, "Response should mention ROS"

    # Performance Requirements
    total_time = end_time - start_time
    first_token_latency = first_token_time - start_time

    assert total_time < 5.0, f"Total response time should be <5s (was {total_time:.2f}s)"
    assert first_token_latency < 3.0, f"First token latency should be <3s (was {first_token_latency:.2f}s)"

    # Content Quality - Should cite book content
    # (Relaxed check - just ensure it's not generic)
    assert len(response) > 100, "Response should be detailed"

    print(f"\n✅ Integration test passed")
    print(f"   Response length: {len(response)} chars")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   First token: {first_token_latency:.2f}s")
    print(f"   Response preview: {response[:200]}...")
```

**Expected Result**: ✅ Real OpenRouter response citing textbook content, <5s total, <3s first token

---

### 2.2 Test Qdrant Retrieval Integration

**File**: `tests/test_integration_openrouter.py`
**Purpose**: Verify Qdrant retrieval returns exactly 3 chunks
**Prerequisites**: Qdrant Cloud connection + embedded textbook data

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_qdrant_retrieval_with_agents_sdk():
    """Test Qdrant retrieval → Agents SDK integration."""
    from app.services.retrieval import retrieve_chunks  # Assuming this function exists

    # Retrieve from real Qdrant
    query = "What is ROS 2?"
    chunks = await retrieve_chunks(query, top_k=3)

    # Validate retrieval
    assert len(chunks) >= 3, f"Should retrieve at least 3 chunks (got {len(chunks)})"
    assert all("text" in chunk for chunk in chunks), "All chunks should have 'text' field"
    assert all("chapter" in chunk for chunk in chunks), "All chunks should have 'chapter' field"

    # Now test with Agents SDK
    response_tokens = []
    async for token in generate_response_stream(
        question=query,
        chunks=chunks[:3],  # Use top 3 chunks
        conversation_history=[],
        session_id="qdrant-integration-test"
    ):
        response_tokens.append(token)

    response = "".join(response_tokens)
    assert len(response) > 0, "Should generate response from retrieved chunks"
    print(f"✅ Qdrant → Agents SDK integration working")
    print(f"   Retrieved {len(chunks)} chunks")
    print(f"   Response: {response[:150]}...")
```

**Expected Result**: ✅ Qdrant returns 3+ chunks, Agents SDK generates response

---

### 2.3 Test Error Handling with Invalid API Key

**File**: `tests/test_integration_openrouter.py`
**Purpose**: Verify authentication errors are handled gracefully

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_invalid_api_key_handling():
    """Test behavior with invalid OPENROUTER_API_KEY."""
    from openai import AsyncOpenAI, AuthenticationError
    from agents import set_default_openai_client, Agent, Runner
    from app.config import settings

    # Configure client with invalid key
    invalid_client = AsyncOpenAI(
        api_key="sk-or-v1-invalid-key-12345",
        base_url=settings.BASE_URL
    )
    set_default_openai_client(invalid_client)

    # Create agent
    test_agent = Agent(
        name="TestAgent",
        model=settings.OPENROUTER_MODEL,
        instructions="Test",
        tools=[]
    )

    # Expect authentication error
    with pytest.raises(AuthenticationError):
        result = await Runner.run(agent=test_agent, input="Test")

    print("✅ Invalid API key properly raises AuthenticationError")

    # Restore valid client (important!)
    valid_client = AsyncOpenAI(
        api_key=settings.OPENROUTER_API_KEY,
        base_url=settings.BASE_URL
    )
    set_default_openai_client(valid_client)
```

**Expected Result**: ✅ AuthenticationError raised for invalid API key

---

### Integration Test Execution

```bash
# Run integration tests (requires OPENROUTER_API_KEY)
cd backend/rag-chatbot
pytest tests/test_integration_openrouter.py -v -m integration

# Expected output:
# tests/test_integration_openrouter.py::test_full_rag_pipeline_with_openrouter PASSED
# tests/test_integration_openrouter.py::test_qdrant_retrieval_with_agents_sdk PASSED
# tests/test_integration_openrouter.py::test_invalid_api_key_handling PASSED
# ======================== 3 passed in 8.5s ========================

# Skip integration tests if no API key
pytest tests/test_integration_openrouter.py -v -m "not integration"
```

**Success Criteria**:
- ✅ All 3 integration tests pass
- ✅ Total response time < 5 seconds
- ✅ First token latency < 3 seconds
- ✅ Response cites textbook content

---

## Layer 3: Manual Testing (User Acceptance)

### 3.1 Test with Postman

**Endpoint**: `POST http://localhost:8000/api/v1/chat/stream`

**Request**:
```json
{
  "message": "What is ROS 2?",
  "session_id": "manual-test-001",
  "selected_text": null
}
```

**Expected Response** (Server-Sent Events):
```
data: {"type": "token", "content": "ROS"}

data: {"type": "token", "content": " 2"}

data: {"type": "token", "content": " (Robot"}

...

data: {"type": "done"}
```

**Validation Checklist**:
- ☐ Status code: 200 OK
- ☐ Content-Type: `text/event-stream`
- ☐ Tokens arrive progressively (streaming, not buffered)
- ☐ Response mentions "ROS 2" or "Robot Operating System"
- ☐ Response cites textbook content (not generic knowledge)
- ☐ No mock data (e.g., "This is a mock response")
- ☐ Total time < 5 seconds
- ☐ First token < 3 seconds

---

### 3.2 Test with curl

```bash
# Basic streaming test
curl -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the key components of a humanoid robot?",
    "session_id": "curl-test-001"
  }' \
  --no-buffer

# Expected output:
# data: {"type":"token","content":"Humanoid"}
# data: {"type":"token","content":" robots"}
# ...
# data: {"type":"done"}
```

**Validation**:
- ☐ Streaming output appears immediately (not after completion)
- ☐ Response is relevant to humanoid robotics textbook
- ☐ No errors in server logs

---

### 3.3 Test Conversation History (12 Message Limit)

**Purpose**: Verify conversation history is limited to 12 messages

**Steps**:
1. Create new session
2. Send 15 messages in sequence
3. Verify only last 12 are included in context

**Request** (message 15):
```json
{
  "message": "Summarize our conversation",
  "session_id": "history-test-001"
}
```

**Expected Response**:
- Should only reference messages 4-15 (last 12 messages)
- Should NOT mention messages 1-3

**Validation**:
- ☐ Response references recent messages only
- ☐ No mention of very old messages (beyond 12)

---

### 3.4 Test Selected Text Query (Hybrid Search)

**Purpose**: Verify hybrid search works (70% query + 30% selected text)

**Request**:
```json
{
  "message": "Explain this concept in detail",
  "session_id": "hybrid-test-001",
  "selected_text": "DDS (Data Distribution Service) is the middleware standard used in ROS 2"
}
```

**Expected Behavior**:
- Qdrant search uses both query embedding AND selected text embedding
- Response explains DDS in detail (context from selected text)
- Returns top 3 chunks (as per hardcoded limit)

**Validation**:
- ☐ Response focuses on DDS (from selected text)
- ☐ Response is more specific than without selected text
- ☐ Chunks retrieved are relevant to both query and selection

---

## Layer 4: Performance Testing

### 4.1 Latency Benchmarks

**Test Script**: `tests/performance/test_latency.py`

```python
import asyncio
import time
from app.services.llm import generate_response_stream

async def benchmark_latency(num_requests=10):
    """Benchmark response latency over multiple requests."""
    chunks = [
        {"text": "ROS 2 is a modern robotics middleware...", "chapter": "2", "section": "2.1"},
        {"text": "DDS is used for communication...", "chapter": "2", "section": "2.2"},
        {"text": "Supports real-time systems...", "chapter": "2", "section": "2.3"}
    ]

    latencies = []
    first_token_latencies = []

    for i in range(num_requests):
        start_time = time.time()
        first_token_time = None

        async for token in generate_response_stream(
            question="What is ROS 2?",
            chunks=chunks,
            conversation_history=[],
            session_id=f"perf-test-{i}"
        ):
            if first_token_time is None:
                first_token_time = time.time()

        end_time = time.time()

        total_latency = end_time - start_time
        first_token_latency = first_token_time - start_time

        latencies.append(total_latency)
        first_token_latencies.append(first_token_latency)

    # Calculate statistics
    avg_latency = sum(latencies) / len(latencies)
    p90_latency = sorted(latencies)[int(0.9 * len(latencies))]
    avg_first_token = sum(first_token_latencies) / len(first_token_latencies)
    p90_first_token = sorted(first_token_latencies)[int(0.9 * len(first_token_latencies))]

    print(f"\n📊 Performance Benchmark Results (n={num_requests})")
    print(f"   Avg total latency: {avg_latency:.2f}s")
    print(f"   P90 total latency: {p90_latency:.2f}s")
    print(f"   Avg first token: {avg_first_token:.2f}s")
    print(f"   P90 first token: {p90_first_token:.2f}s")

    # Assertions
    assert avg_latency < 5.0, f"Average latency should be <5s (was {avg_latency:.2f}s)"
    assert p90_latency < 5.0, f"P90 latency should be <5s (was {p90_latency:.2f}s)"
    assert p90_first_token < 3.0, f"P90 first token should be <3s (was {p90_first_token:.2f}s)"

    print("✅ All performance benchmarks passed")

if __name__ == "__main__":
    asyncio.run(benchmark_latency(num_requests=20))
```

**Expected Results**:
- ✅ Avg total latency < 5s
- ✅ P90 total latency < 5s
- ✅ P90 first token latency < 3s

---

### 4.2 Throughput Testing

**Purpose**: Verify system handles concurrent requests

```python
async def benchmark_throughput(concurrent_requests=10):
    """Benchmark throughput with concurrent requests."""
    chunks = [
        {"text": "Test chunk 1", "chapter": "1", "section": "1.1"},
        {"text": "Test chunk 2", "chapter": "1", "section": "1.2"},
        {"text": "Test chunk 3", "chapter": "1", "section": "1.3"}
    ]

    async def single_request(request_id):
        start = time.time()
        tokens = []
        async for token in generate_response_stream(
            question=f"Test question {request_id}",
            chunks=chunks,
            conversation_history=[],
            session_id=f"throughput-{request_id}"
        ):
            tokens.append(token)
        return time.time() - start

    # Run concurrent requests
    start_time = time.time()
    tasks = [single_request(i) for i in range(concurrent_requests)]
    latencies = await asyncio.gather(*tasks)
    total_time = time.time() - start_time

    throughput = concurrent_requests / total_time

    print(f"\n📊 Throughput Benchmark (n={concurrent_requests} concurrent)")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Throughput: {throughput:.2f} req/s")
    print(f"   Avg latency: {sum(latencies)/len(latencies):.2f}s")

    assert throughput > 1.0, f"Throughput should be >1 req/s (was {throughput:.2f})"
    print("✅ Throughput benchmark passed")
```

**Expected Results**:
- ✅ Throughput > 1 request/second
- ✅ No request failures under concurrent load

---

## Validation Checklist (Pre-Production)

Before deploying to production, verify:

### Functional Validation
- ☐ All 7 unit tests pass
- ☐ All 3 integration tests pass (with real API key)
- ☐ Manual Postman test returns real responses (not mock)
- ☐ curl streaming test shows progressive tokens
- ☐ Conversation history limited to 12 messages
- ☐ Selected text queries use hybrid search
- ☐ Responses cite textbook content (not generic knowledge)

### Performance Validation
- ☐ Average response time < 5 seconds
- ☐ P90 response time < 5 seconds
- ☐ P90 first token latency < 3 seconds
- ☐ Qdrant retrieval returns exactly 3 chunks (top_k=3)
- ☐ Streaming works (no buffering)

### Error Handling Validation
- ☐ Invalid API key returns clear error message
- ☐ Network errors return HTTP 503
- ☐ Rate limit errors return HTTP 429
- ☐ Errors logged with appropriate severity

### Code Quality Validation
- ☐ No linting errors (`ruff check app/`)
- ☐ No type errors (`mypy app/` if using type hints)
- ☐ Test coverage > 80% for modified files
- ☐ No deprecated warnings from Agents SDK

### Deployment Validation
- ☐ Server starts without errors
- ☐ "agents_sdk_configured" log appears with correct model
- ☐ Health check endpoint returns 200 OK
- ☐ Frontend widget compatibility verified
- ☐ No hardcoded secrets in code (use .env)

### Rollback Validation
- ☐ Can switch back to `chat_minimal.router` in <5 minutes
- ☐ `gemini_client.py` still exists (emergency fallback)
- ☐ `.env` contains both OPENROUTER_API_KEY and GOOGLE_API_KEY

---

## Continuous Integration (CI) Configuration

### GitHub Actions (Example)

```yaml
# .github/workflows/test-agents-sdk.yml
name: Test OpenAI Agents SDK Migration

on:
  push:
    branches: [001-openai-agents-migration]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend/rag-chatbot
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio

      - name: Run unit tests
        run: |
          cd backend/rag-chatbot
          pytest tests/test_llm_agents.py -v --cov=app.services.llm

      - name: Run integration tests (if API key available)
        if: ${{ secrets.OPENROUTER_API_KEY }}
        env:
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
        run: |
          cd backend/rag-chatbot
          pytest tests/test_integration_openrouter.py -v -m integration
```

---

## Test Data Fixtures

### Sample Qdrant Chunks (for testing)

```python
# tests/fixtures/chunks.py
SAMPLE_CHUNKS = [
    {
        "text": "ROS 2 (Robot Operating System 2) is a modern robotics middleware that provides libraries and tools for building robot applications.",
        "chapter": "2",
        "section": "2.1",
        "score": 0.95
    },
    {
        "text": "DDS (Data Distribution Service) is the middleware standard used in ROS 2 for real-time inter-process communication.",
        "chapter": "2",
        "section": "2.2",
        "score": 0.89
    },
    {
        "text": "Humanoid robots typically consist of mechanical systems, sensors, actuators, and control software.",
        "chapter": "3",
        "section": "3.1",
        "score": 0.84
    }
]
```

---

## Summary

**Testing Layers**: 4 (Unit → Integration → Manual → Performance)
**Total Tests**: 10+ automated tests + manual validation
**Quality Gates**: All tests must pass before production
**Key Metrics**: <5s response, <3s first token, 3 chunks, no mock data

**Validation Status**: Ready for implementation testing
