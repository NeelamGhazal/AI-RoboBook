# Data Model: RAG Chatbot Backend

**Feature**: 003-rag-chatbot-backend
**Created**: 2025-12-17
**Purpose**: Define data structures for chat sessions, message history, vector embeddings, and citations

---

## Core Entities

### 1. Session

Represents a user's conversation thread with the chatbot.

**Attributes**:
- `session_id` (UUID, primary key): Unique identifier for the conversation
- `created_at` (timestamp): When the session was initiated
- `last_activity` (timestamp): Last message timestamp (for cleanup)
- `user_id` (string, optional): External user identifier from frontend auth
- `status` (enum): `active`, `archived`, `deleted`
- `metadata` (JSONB): Flexible storage for future extensions (user preferences, context)

**Validation Rules**:
- `session_id` must be unique and immutable
- `last_activity` must be updated on every message
- `status` transitions: `active` → `archived` (after 90 days) → `deleted` (after 1 year)

**State Transitions**:
```
[Created] → active → archived (90 days inactivity) → deleted (1 year total)
                ↓
           deleted (user request)
```

**Relationships**:
- One session has many messages (1:N)
- Session can have zero or more messages

**Indexes**:
- Primary: `session_id`
- Secondary: `user_id` (for user history queries)
- Secondary: `last_activity` (for cleanup jobs)

---

### 2. Message

Individual question or answer within a conversation.

**Attributes**:
- `message_id` (UUID, primary key): Unique identifier
- `session_id` (UUID, foreign key): Links to session
- `role` (enum): `user`, `assistant`, `system`
- `content` (text): Message text (question or answer)
- `timestamp` (timestamp): When message was created
- `token_count` (integer): Tokens used (for context window management)
- `selected_text` (text, nullable): User-highlighted text for contextual queries
- `citations` (JSONB): Array of citation objects (for assistant messages)
- `metadata` (JSONB): Search params, confidence scores, retrieval time

**Validation Rules**:
- `role` must be one of: `user`, `assistant`, `system`
- `token_count` must be positive
- `citations` only valid for `assistant` role messages
- `selected_text` only valid for `user` role messages
- `content` max length: 10,000 characters

**Relationships**:
- Many messages belong to one session (N:1)
- Messages ordered chronologically within session

**Indexes**:
- Primary: `message_id`
- Secondary: `session_id, timestamp` (for history retrieval)
- Secondary: `role` (for filtering)

**Example Citation Structure** (JSONB):
```json
{
  "citations": [
    {
      "chunk_id": "uuid-of-chunk",
      "chapter": "module1/chapter1",
      "section": "ROS 2 Architecture",
      "url": "/docs/module1/chapter1#ros-2-architecture",
      "confidence_score": 0.89,
      "text_snippet": "ROS 2 uses a Data Distribution Service..."
    }
  ],
  "retrieval_time_ms": 245,
  "top_k": 5,
  "avg_confidence": 0.82
}
```

---

### 3. TextChunk

Indexed content unit stored in Qdrant vector database.

**Attributes**:
- `chunk_id` (UUID, primary key): Unique identifier
- `embedding_vector` (float array[1536]): OpenAI text-embedding-3-small vector
- `text_content` (text): Original text (500-1000 tokens)
- `chapter_path` (string): File path (e.g., `module1/chapter1`)
- `chapter_number` (integer): Module and chapter for sorting
- `section_title` (string): Heading/section name
- `subsection_title` (string, nullable): Nested heading if exists
- `url_path` (string): Docusaurus URL (e.g., `/docs/module1/chapter1#section`)
- `token_count` (integer): Actual token count of text
- `metadata` (JSONB): Markdown metadata, code block indicators, image refs

**Validation Rules**:
- `chunk_id` must be unique and immutable
- `embedding_vector` must be exactly 1536 dimensions (text-embedding-3-small)
- `text_content` must be 500-1000 tokens (validated during ingestion)
- `chapter_path` must follow pattern: `module{N}/chapter{M}`
- `url_path` must be valid Docusaurus URL

**Storage Location**: Qdrant Cloud collection `textbook_chunks`

**Qdrant Schema**:
```python
{
    "vectors": {
        "size": 1536,
        "distance": "Cosine"
    },
    "payload_schema": {
        "chunk_id": "keyword",
        "chapter_path": "keyword",
        "chapter_number": "integer",
        "section_title": "text",
        "url_path": "keyword",
        "token_count": "integer",
        "text_content": "text"
    }
}
```

**Indexes**:
- Primary: Vector index (HNSW for similarity search)
- Secondary: `chapter_path` (for filtering by chapter)
- Secondary: `chapter_number` (for ordered retrieval)

---

### 4. Citation

Reference to a textbook source returned with assistant responses.

**Attributes** (embedded in Message.citations JSONB):
- `chunk_id` (UUID): Links to TextChunk
- `chapter` (string): Chapter path (e.g., `module2/chapter3`)
- `section` (string): Section heading
- `url` (string): Clickable Docusaurus link
- `confidence_score` (float): Relevance score from vector search (0.0-1.0)
- `text_snippet` (string): Preview of source text (first 200 chars)

**Validation Rules**:
- `confidence_score` must be between 0.0 and 1.0
- `url` must be validated against existing Docusaurus pages
- `text_snippet` must be truncated to 200 characters max
- Citations must be sorted by `confidence_score` descending

**Ranking Logic**:
- Top 3-5 citations displayed to user
- Minimum confidence threshold: 0.70
- Deduplicate by `chapter` (show highest scoring chunk per chapter)

---

### 5. EmbeddingRequest

Temporary query embedding for vector search (not persisted).

**Attributes** (in-memory only):
- `query_text` (string): User's question
- `selected_text` (string, nullable): User-highlighted context
- `embedding_vector` (float array[1536]): Generated query embedding
- `search_params` (dict): Top-k, filters, score threshold

**Lifecycle**:
1. Create from user question
2. Generate embedding via OpenAI API
3. Execute Qdrant search
4. Discard after retrieval (not stored)

**Example Search Params**:
```python
{
    "top_k": 5,
    "score_threshold": 0.70,
    "filter": {
        "chapter_path": "module1/chapter1"  # If selected text mode
    }
}
```

---

## Relationships Diagram

```
Session (1) ──< Messages (N)
                    │
                    │ contains citations
                    ↓
                Citations ──→ TextChunks (in Qdrant)
```

**Key Points**:
- Sessions persist in Postgres (long-term storage)
- Messages persist in Postgres with JSONB citations
- TextChunks persist in Qdrant (vector database)
- Citations are denormalized JSONB in messages (no separate table)
- EmbeddingRequests are ephemeral (request-scoped)

---

## Database Schema (PostgreSQL)

### Table: sessions

```sql
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255),
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted')),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Indexes
    CONSTRAINT sessions_pkey PRIMARY KEY (session_id)
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_last_activity ON sessions(last_activity);
CREATE INDEX idx_sessions_status ON sessions(status);
```

### Table: messages

```sql
CREATE TABLE messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL CHECK (char_length(content) <= 10000),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    token_count INTEGER NOT NULL CHECK (token_count > 0),
    selected_text TEXT,
    citations JSONB,
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Indexes
    CONSTRAINT messages_pkey PRIMARY KEY (message_id)
);

CREATE INDEX idx_messages_session_timestamp ON messages(session_id, timestamp DESC);
CREATE INDEX idx_messages_role ON messages(role);
```

### Migration Notes

- Use `gen_random_uuid()` for UUID generation (native Postgres)
- JSONB for flexible schema evolution
- Cascade delete: deleting session removes all messages
- Timestamp with time zone for consistency across regions
- Check constraints for data integrity

---

## Qdrant Collection Configuration

### Collection: textbook_chunks

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

client.create_collection(
    collection_name="textbook_chunks",
    vectors_config=VectorParams(
        size=1536,  # text-embedding-3-small dimension
        distance=Distance.COSINE
    ),
    optimizers_config={
        "indexing_threshold": 10000,  # Start indexing after 10k vectors
        "memmap_threshold": 20000
    },
    hnsw_config={
        "m": 16,  # Number of edges per node (balance speed/accuracy)
        "ef_construct": 100  # Construction time accuracy
    }
)
```

### Point Structure

```python
PointStruct(
    id=chunk_id,  # UUID
    vector=embedding_vector,  # [float] * 1536
    payload={
        "chunk_id": str(chunk_id),
        "chapter_path": "module1/chapter1",
        "chapter_number": 101,  # 100*module + chapter
        "section_title": "ROS 2 Architecture",
        "subsection_title": "DDS Layer",
        "url_path": "/docs/module1/chapter1#ros-2-architecture",
        "token_count": 742,
        "text_content": "Full text of chunk...",
        "metadata": {
            "has_code": True,
            "language": "python",
            "heading_level": 2
        }
    }
)
```

---

## Data Constraints Summary

| Entity | Max Size | Retention | Cleanup Policy |
|--------|----------|-----------|----------------|
| Session | ~1KB | 1 year | Archive after 90 days, delete after 1 year |
| Message | ~10KB | 1 year | Cascade delete with session |
| TextChunk | ~4KB | Permanent | Re-index on content updates |
| Citation | ~500B | Embedded in message | N/A (denormalized) |

**Estimated Storage** (MVP):
- 1000 active users × 10 sessions × 20 messages = 200K messages
- 23 chapters × 20 chunks/chapter × 4KB = ~2MB vectors
- Postgres: ~50MB (messages + sessions)
- Qdrant: ~3MB (vectors + metadata)

**Scalability Notes**:
- Neon Serverless Postgres free tier: 512MB (sufficient for MVP)
- Qdrant Cloud free tier: 1GB, 100K vectors (sufficient for 23 chapters)
- Session cleanup job runs daily (archives old sessions)
- Message pruning optional (keep indefinitely or prune after 1 year)
