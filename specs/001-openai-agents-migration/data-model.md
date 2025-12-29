# Data Model: OpenAI Agents SDK Migration

**Feature**: 001-openai-agents-migration
**Phase**: Phase 1 - Design
**Date**: 2025-12-25
**Status**: Complete

## Overview

**Key Finding**: This migration requires **ZERO changes** to existing data models.

This is a pure service layer refactoring that swaps the LLM client implementation while preserving all data structures, database schemas, and API contracts. The Agents SDK operates at the orchestration layer and does not introduce new data entities.

## Existing Data Models (Unchanged)

### 1. Session Model

**File**: `app/models/session.py`
**Purpose**: Track chat sessions for conversation continuity
**Schema**: Neon Postgres `sessions` table

```python
class Session:
    id: UUID
    created_at: datetime
    last_activity_at: datetime
```

**Migration Impact**: ✅ None - session management remains identical

---

### 2. Message Model

**File**: `app/models/message.py`
**Purpose**: Store individual chat messages (user questions + assistant responses)
**Schema**: Neon Postgres `messages` table

```python
class Message:
    id: UUID
    session_id: UUID (foreign key to sessions)
    role: str ("user" | "assistant")
    content: str
    created_at: datetime
```

**Migration Impact**: ✅ None - message format (role + content) is compatible with Agents SDK (uses same OpenAI Chat Completions format)

---

### 3. Request/Response Schemas

**File**: `app/models/schemas.py`
**Purpose**: Pydantic models for API validation

```python
class ChatRequest(BaseModel):
    question: str
    session_id: Optional[UUID]
    selected_text: Optional[str]

class Citation(BaseModel):
    source: str
    chapter: str
    section: str
    page: Optional[int]
    text: str
    confidence_score: float

class StreamEvent(BaseModel):
    type: str  # "token" | "citations" | "metadata" | "done" | "error"
    content: Optional[str]
    citations: Optional[List[Citation]]
    metadata: Optional[dict]
```

**Migration Impact**: ✅ None - streaming event format must remain unchanged for frontend compatibility (spec FR-012)

---

### 4. Qdrant Vector Schema

**Collection**: `textbook_chunks` (Qdrant Cloud)
**Purpose**: Semantic search over textbook content

```python
# Vector point payload
{
    "text": str,            # Chunk content
    "chapter": str,         # Chapter title
    "section": str,         # Section title
    "page": Optional[int],  # Page number
    "embedding": List[float]  # 384-dim vector (sentence-transformers)
}
```

**Migration Impact**: ✅ None - vector search and retrieval remain unchanged (spec FR-011)

---

## Non-Data Changes (Service Layer Only)

While there are no data model changes, the migration affects these service components:

### 1. Agent Configuration (New Concept)

**File**: `app/services/llm.py` (refactored)
**Purpose**: Define the RAG agent for OpenAI Agents SDK

```python
from agents import Agent

# Agent is a configuration object, not a persisted data model
rag_agent = Agent(
    name="TextbookRAG",
    instructions=SYSTEM_PROMPT,  # Existing template from llm.py:16
    model="gemini-1.5-flash",
    tools=[]  # No tools needed for basic RAG
)
```

**Note**: This is a **runtime configuration object**, not a database entity. It does not require schema migrations or new tables.

### 2. LLM Client Configuration

**File**: `app/main.py` (lifespan startup)
**Purpose**: Configure global OpenAI client for Gemini endpoint

```python
from openai import AsyncOpenAI
from agents import set_default_openai_client

# This is application config, not a data model
gemini_client = AsyncOpenAI(
    api_key=settings.GOOGLE_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
set_default_openai_client(gemini_client)
```

**Note**: This is **startup configuration**, analogous to database connection pooling. No new env vars needed (reuses `GOOGLE_API_KEY`).

---

## Migration Validation Checklist

- [x] No new database tables required
- [x] No schema migrations needed (Postgres or Qdrant)
- [x] Existing Message model compatible with Agents SDK (role + content format)
- [x] Session model unchanged (no new fields)
- [x] API request/response schemas preserved (frontend compatibility)
- [x] Vector embeddings unchanged (sentence-transformers, 384-dim)
- [x] Citation format unchanged
- [x] No new environment variables (reuse GOOGLE_API_KEY)

---

## Summary

This migration is **data-model-transparent**. All changes occur in the service layer (how we call the LLM), not in data persistence or schemas. This minimizes risk and ensures zero downtime for deployment.

**Rationale**: The Agents SDK is an orchestration framework, not a data persistence layer. It consumes existing message formats (OpenAI Chat Completions API) and produces text responses. Our existing SQLAlchemy models and Qdrant schemas remain valid.

**Next Phase**: Proceed to contracts/ directory to document the Agents SDK interface expectations.
