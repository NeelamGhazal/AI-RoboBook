# Architecture Diagram: OpenAI Agents SDK Integration with OpenRouter

**Feature**: 001-openai-agents-migration
**Date**: 2025-12-25
**Status**: Implementation Ready

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Frontend Chatbot Widget                      │
│                    (NO CHANGES - Existing Interface)                 │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ POST /api/v1/chat/stream
                             │ { question, session_id, selected_text }
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       FastAPI Backend (main.py)                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    Lifespan Startup (NEW)                      │  │
│  │  ┌─────────────────────────────────────────────────────────┐  │  │
│  │  │  openrouter_client = AsyncOpenAI(                       │  │  │
│  │  │      api_key=settings.OPENROUTER_API_KEY,               │  │  │
│  │  │      base_url="https://openrouter.ai/api/v1"            │  │  │
│  │  │  )                                                       │  │  │
│  │  │  set_default_openai_client(openrouter_client)  ◄────────┼──┼──┼─── CRITICAL CONFIG
│  │  └─────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │         Router: chat.router (ACTIVATED - was inactive)        │  │
│  │              /api/v1/chat/stream endpoint                     │  │
│  └────────────────────────────┬──────────────────────────────────┘  │
└─────────────────────────────────┼────────────────────────────────────┘
                                  │
                                  │ calls
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    RAG Pipeline (services/rag.py)                    │
│                          (MINIMAL CHANGES)                           │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  1. Retrieve Context                                          │  │
│  │     ├─► vector_search.search_similar_chunks(                 │  │
│  │     │       query=question,                                   │  │
│  │     │       selected_text=selected_text,                      │  │
│  │     │       top_k=3  ◄─────────────────── HARDCODED          │  │
│  │     │   )                                                     │  │
│  │     └─► Returns: List[chunk] (top 3 chunks from Qdrant)      │  │
│  │                                                               │  │
│  │  2. Build Citations                                           │  │
│  │     └─► citation_builder.build_citations(chunks)             │  │
│  │                                                               │  │
│  │  3. Format Conversation History                              │  │
│  │     └─► llm.build_conversation_history(                      │  │
│  │             messages, max_messages=12  ◄──── HARDCODED       │  │
│  │         )                                                     │  │
│  │                                                               │  │
│  │  4. Generate Response (REFACTORED - NEW)                     │  │
│  │     └─► llm.generate_response_stream(                        │  │
│  │             question, chunks, history                         │  │
│  │         )  ──────────────────────────────────►                │  │
│  └───────────────────────────────────────────────┼───────────────┘  │
└─────────────────────────────────────────────────┼────────────────────┘
                                                   │
                                                   │ calls
                                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│               LLM Service (services/llm.py) - REFACTORED            │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  FROM (Old - Direct Gemini):                                  │  │
│  │  ─────────────────────────────────────────────────────────    │  │
│  │  from app.clients.gemini_client import gemini_client  ✗      │  │
│  │  response = await gemini_client.generate_chat_completion_stream()│
│  │                                                               │  │
│  │  TO (New - Agents SDK):                                       │  │
│  │  ─────────────────────────────────────────────────────────    │  │
│  │  from agents import Agent, Runner                            │  │
│  │                                                               │  │
│  │  RAG_AGENT = Agent(                                           │  │
│  │      name="TextbookRAGAgent",                                 │  │
│  │      model="mistralai/devstral-2512:free",  ◄──── FREE MODEL │  │
│  │      instructions=SYSTEM_PROMPT,                              │  │
│  │      tools=[]                                                 │  │
│  │  )                                                            │  │
│  │                                                               │  │
│  │  async def generate_response_stream(...):                     │  │
│  │      # Build input with context + question                    │  │
│  │      user_input = f"""                                        │  │
│  │      **Textbook Excerpts:**                                   │  │
│  │      {context}                                                │  │
│  │                                                               │  │
│  │      **Question:** {question}                                 │  │
│  │      """                                                      │  │
│  │                                                               │  │
│  │      # Stream via Agents SDK Runner                           │  │
│  │      async for event in Runner.run_stream(                    │  │
│  │          agent=RAG_AGENT,                                     │  │
│  │          input=user_input                                     │  │
│  │      ):                                                       │  │
│  │          if event.type == "content_delta":                    │  │
│  │              yield {"type": "token", "content": event.content}│  │
│  └───────────────────────────────────────┬───────────────────────┘  │
└─────────────────────────────────────────┼────────────────────────────┘
                                           │
                                           │ uses global client
                                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 OpenAI Agents SDK (openai.agents)                    │
│               (Package: openai-agents, installed via pip)            │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Runner.run_stream(agent, input) ──────────────────►          │  │
│  │      │                                                         │  │
│  │      └─► Uses: AsyncOpenAI client (configured at startup)     │  │
│  │             └─► base_url: https://openrouter.ai/api/v1        │  │
│  │                 api_key: OPENROUTER_API_KEY                   │  │
│  └───────────────────────────────────────┬───────────────────────┘  │
└─────────────────────────────────────────┼────────────────────────────┘
                                           │
                                           │ HTTP POST
                                           │ (OpenAI Chat Completions format)
                                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 OpenRouter API (https://openrouter.ai/api/v1)       │
│                     (OpenAI-Compatible Endpoint)                    │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  POST /chat/completions                                       │  │
│  │  {                                                            │  │
│  │    "model": "mistralai/devstral-2512:free",                   │  │
│  │    "messages": [...],                                         │  │
│  │    "stream": true                                             │  │
│  │  }                                                            │  │
│  └───────────────────────────────────────┬───────────────────────┘  │
└─────────────────────────────────────────┼────────────────────────────┘
                                           │
                                           │ Routes to
                                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│              Mistral Devstral (mistralai/devstral-2512:free)        │
│                  (Free Model - Coding/Reasoning Specialist)         │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  ✓ Fully free (no quota limits for demos)                    │  │
│  │  ✓ Specialized for coding, reasoning, agentic tasks          │  │
│  │  ✓ Strong tool calling support (not used in this RAG)        │  │
│  │  ✓ Streaming support                                         │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│                     Generates tokens ─────►                          │
└──────────────────────────────────────────────────────────────────────┘
                                           │
                                           │ SSE Stream
                                           │
            ┌──────────────────────────────┘
            │
            │ (bubbles back up through Agents SDK → FastAPI → Frontend)
            ▼
    data: {"type":"token","content":"ROS"}
    data: {"type":"token","content":" 2"}
    data: {"type":"citations","citations":[...]}
    data: {"type":"done"}

```

---

## Supporting Infrastructure (Unchanged)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Qdrant Cloud (Vector Database)                   │
│                         (NO CHANGES)                                │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Collection: textbook_chunks                                  │  │
│  │  Embedding: sentence-transformers (384-dim)                   │  │
│  │  Query: semantic search (cosine similarity)                   │  │
│  │  Returns: top 3 chunks with metadata                          │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                Neon Serverless Postgres (Database)                  │
│                         (NO CHANGES)                                │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Tables:                                                      │  │
│  │    - sessions (id, created_at, last_activity_at)             │  │
│  │    - messages (id, session_id, role, content, created_at)    │  │
│  │  Query: SELECT last 12 messages WHERE session_id = ...       │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Sequence

### Request Flow (User → Response)

```
1. User asks: "What is ROS 2?"
   │
   ├─► Frontend sends POST /api/v1/chat/stream
   │   { question: "What is ROS 2?", session_id: "..." }
   │
2. FastAPI chat.py endpoint receives request
   │
   ├─► rag.execute_rag_pipeline_stream(question, session_id)
   │
3. RAG Pipeline Stage 1: Retrieval
   │
   ├─► vector_search.search_similar_chunks(query="What is ROS 2?", top_k=3)
   │   └─► Qdrant returns: [chunk1, chunk2, chunk3]
   │
4. RAG Pipeline Stage 2: Context Building
   │
   ├─► citation_builder.build_citations([chunk1, chunk2, chunk3])
   │   └─► Returns: [citation1, citation2, citation3]
   │
   ├─► db.fetch_recent_messages(session_id, limit=12)
   │   └─► Neon Postgres returns: last 12 messages
   │
   ├─► llm.build_context_from_chunks(chunks)
   │   └─► Formats: "**Textbook Excerpts:**\n[chunk1 text]\n[chunk2 text]..."
   │
5. RAG Pipeline Stage 3: LLM Generation (NEW - Agents SDK)
   │
   ├─► llm.generate_response_stream(question, chunks, history)
   │   │
   │   ├─► Creates user_input = f"""
   │   │       **Textbook Excerpts:**
   │   │       {context}
   │   │
   │   │       **Question:** {question}
   │   │   """
   │   │
   │   ├─► Calls: Runner.run_stream(agent=RAG_AGENT, input=user_input)
   │   │   │
   │   │   ├─► Agents SDK uses global AsyncOpenAI client (OpenRouter configured)
   │   │   │
   │   │   ├─► POST https://openrouter.ai/api/v1/chat/completions
   │   │   │   {
   │   │   │     "model": "mistralai/devstral-2512:free",
   │   │   │     "messages": [
   │   │   │       {"role": "system", "content": SYSTEM_PROMPT},
   │   │   │       {"role": "user", "content": user_input}
   │   │   │     ],
   │   │   │     "stream": true
   │   │   │   }
   │   │   │
   │   │   ├─► OpenRouter routes to Mistral Devstral
   │   │   │
   │   │   └─► Streams back: event.type="content_delta", event.content="ROS"
   │   │
   │   └─► Yields: {"type": "token", "content": "ROS"}
   │
6. FastAPI Streaming Response
   │
   ├─► Wraps in SSE format: data: {"type":"token","content":"ROS"}
   │
   └─► Sends to Frontend
   │
7. Frontend receives and displays tokens in real-time
```

---

## Key Architecture Changes

### Before Migration (Direct Gemini)

```
FastAPI → chat_minimal.py (mock responses) ✗
       → gemini_client.generate_chat_completion_stream() ✗
       → POST https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:streamGenerateContent ✗
```

### After Migration (Agents SDK + OpenRouter)

```
FastAPI → chat.py (real RAG) ✓
       → llm.generate_response_stream()
       → Runner.run_stream(agent=RAG_AGENT) ✓
       → AsyncOpenAI client (configured with OpenRouter base_url) ✓
       → POST https://openrouter.ai/api/v1/chat/completions ✓
       → Mistral Devstral (free model) ✓
```

---

## Configuration Points

### Environment Variables (.env)

```env
# OpenRouter Configuration (NEW)
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxx
OPENROUTER_MODEL=mistralai/devstral-2512:free
BASE_URL=https://openrouter.ai/api/v1

# Existing (Unchanged)
QDRANT_URL=https://xxxxx.qdrant.io
QDRANT_API_KEY=xxxxx
NEON_DATABASE_URL=postgresql://user:pass@host/db
```

### Startup Configuration (main.py lifespan)

```python
from openai import AsyncOpenAI
from agents import set_default_openai_client

openrouter_client = AsyncOpenAI(
    api_key=settings.OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)
set_default_openai_client(openrouter_client)  # ◄── GLOBAL CONFIG
```

### Agent Definition (llm.py module level)

```python
from agents import Agent

RAG_AGENT = Agent(
    name="TextbookRAGAgent",
    model="mistralai/devstral-2512:free",
    instructions=SYSTEM_PROMPT,  # Static system prompt
    tools=[]  # No function calling for RAG
)
```

---

## Error Handling Flow

```
User Request
    │
    ├─► Qdrant connection fails
    │   └─► Return 503: "Unable to search textbook content"
    │
    ├─► Neon Postgres unavailable
    │   └─► Continue without history (in-memory fallback)
    │
    ├─► OpenRouter API error
    │   ├─► RateLimitError → 429: "Service temporarily unavailable"
    │   ├─► AuthenticationError → 500: "Configuration error"
    │   └─► APIConnectionError → 503: "Unable to connect to chatbot service"
    │
    └─► Agents SDK error
        └─► Log error, return 500: "An error occurred while generating the response"
```

---

## Performance Characteristics

| Stage | Latency | Notes |
|-------|---------|-------|
| FastAPI routing | <10ms | Minimal overhead |
| Qdrant retrieval | 150-300ms | Cloud query (3 chunks) |
| Context building | <50ms | String formatting |
| Agents SDK overhead | <50ms | Lightweight wrapper |
| OpenRouter routing | 50-100ms | Proxy to Mistral |
| Mistral Devstral TTFT | 800-1500ms | Time to first token |
| **Total (p90)** | **<2.5s** | Well within <3s requirement |

---

## Compliance Verification Points

Hackathon judges will verify:

1. **SDK Import** in `app/services/llm.py`:
   ```python
   from agents import Agent, Runner  # ✓ Uses Agents SDK
   ```

2. **No Direct Gemini**:
   ```python
   from app.clients.gemini_client import gemini_client  # ✗ NOT PRESENT
   ```

3. **OpenRouter Configuration** in `app/main.py`:
   ```python
   openrouter_client = AsyncOpenAI(base_url="https://openrouter.ai/api/v1")
   set_default_openai_client(openrouter_client)  # ✓ Configured
   ```

4. **Real RAG Pipeline** active:
   ```python
   app.include_router(chat.router)  # ✓ Not chat_minimal
   ```

5. **No Mock Responses** - All answers include Qdrant citations
