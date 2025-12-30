# database-config

Configure Neon Postgres and Qdrant Cloud for production deployment.

## Purpose
Setup and configure database connections for chat history and vector embeddings.

## Tasks
1. Configure Neon Serverless Postgres connection
2. Setup Qdrant Cloud vector database
3. Create database schemas
4. Setup connection pooling
5. Configure environment variables
6. Implement error handling and retries

## Neon Postgres Setup

### Connection Configuration
- Connection string format: `postgresql://user:password@host/database`
- SSL/TLS settings (required for Neon)
- Connection pooling with pgBouncer
- Timeout configurations

### Database Schema
```sql
CREATE TABLE chat_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) REFERENCES chat_sessions(session_id),
    role VARCHAR(50),
    content TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);
```

## Qdrant Cloud Setup

### Collection Configuration
- Vector dimension: 1536 (for OpenAI embeddings)
- Distance metric: Cosine similarity
- Indexing parameters
- Payload schema for metadata

### Collection Creation
```python
client.create_collection(
    collection_name="book_content",
    vectors_config={
        "size": 1536,
        "distance": "Cosine"
    }
)
```

## Security Best Practices
- Use environment variables for all credentials
- Enable SSL connections
- Configure access controls and IP allowlisting
- Setup connection timeouts
- Implement rate limiting

## Error Handling
- Connection retry logic with exponential backoff
- Fallback mechanisms
- Comprehensive logging
- Health check endpoints
- Graceful degradation

## Environment Variables Required
```
NEON_DATABASE_URL=postgresql://...
QDRANT_URL=https://...
QDRANT_API_KEY=...
QDRANT_COLLECTION_NAME=book_content
```

## Output
Production-ready database configurations with secure, reliable connections