# Tasks: RAG Chatbot Backend for Physical AI & Humanoid Robotics Textbook

**Input**: Design documents from `/specs/003-rag-chatbot-backend/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/openapi.yaml, research.md, quickstart.md

**Tests**: Test tasks are included as this is a production backend system requiring comprehensive testing.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

Web app structure: `backend/rag-chatbot/` at repository root based on plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

**Estimated Effort**: 2-3 hours

- [X] T001 Create project directory structure per plan.md: backend/rag-chatbot/{app,scripts,tests,logs,monitoring}
- [X] T002 Initialize Python 3.11+ project with pyproject.toml and requirements.txt per quickstart.md
- [X] T003 [P] Create requirements.txt with FastAPI 0.109.0, uvicorn[standard] 0.27.0, pydantic 2.5.0, openai 1.10.0, qdrant-client 1.7.0, asyncpg 0.29.0, httpx 0.26.0, structlog 24.1.0, prometheus-client 0.19.0
- [X] T004 [P] Create requirements-dev.txt with pytest 7.4.0, pytest-asyncio, pytest-cov, black, flake8, mypy
- [X] T005 [P] Create .env.example template with all required environment variables per quickstart.md
- [X] T006 [P] Create .gitignore for Python project (venv/, __pycache__/, .env, logs/, .pytest_cache/)
- [X] T007 [P] Create Docker build context: Dockerfile and .dockerignore per quickstart.md
- [X] T008 [P] Create docker-compose.yml for local development with backend service per quickstart.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

**Estimated Effort**: 6-8 hours

### Configuration & Settings

- [X] T009 Implement Pydantic Settings in backend/rag-chatbot/app/config.py for environment variables (OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY, NEON_DATABASE_URL, DB_POOL_MIN_SIZE, DB_POOL_MAX_SIZE, API_HOST, API_PORT, CORS_ORIGINS, RATE_LIMIT_PER_MINUTE, LOG_LEVEL, LOG_JSON)
- [X] T010 [P] Configure structured logging with structlog in backend/rag-chatbot/app/utils/logging.py (JSON format, console renderer for dev, file handler)
- [X] T011 [P] Setup Prometheus metrics client in backend/rag-chatbot/app/utils/metrics.py (REQUEST_DURATION histogram, ERROR_COUNTER, CONCURRENT_REQUESTS gauge)

### Database Infrastructure

- [X] T012 Create Postgres connection pool with asyncpg in backend/rag-chatbot/app/clients/db_client.py (min_size=5, max_size=20, lifecycle management)
- [X] T013 Create database migration script in backend/rag-chatbot/scripts/migrate.py to create sessions and messages tables per data-model.md
- [X] T014 Create database models in backend/rag-chatbot/app/models/session.py for Session entity (session_id, user_id, status, created_at, last_activity, metadata)
- [X] T015 [P] Create database models in backend/rag-chatbot/app/models/message.py for Message entity (message_id, session_id, role, content, timestamp, token_count, selected_text, citations, metadata)
- [X] T016 Create base CRUD operations in backend/rag-chatbot/app/db/crud.py (create_session, get_session, create_message, get_messages_by_session with pagination)

### External Client Setup

- [X] T017 Create OpenAI httpx async client wrapper in backend/rag-chatbot/app/clients/openai_client.py (connection pooling: max_keepalive=20, max_connections=100, timeout=30s, semaphore for concurrency limiting=10)
- [X] T018 [P] Create Qdrant async client wrapper in backend/rag-chatbot/app/clients/qdrant_client.py (connection handling, error retry logic)
- [X] T019 Create Qdrant collection initialization script in backend/rag-chatbot/scripts/init_qdrant.py (collection: textbook_chunks, vectors: size=1536 distance=Cosine, HNSW config: m=16 ef_construct=100)
- [X] T020 Create Qdrant collection verification script in backend/rag-chatbot/scripts/verify_qdrant.py (check collection exists, count vectors, verify indexed status)

### FastAPI Application Setup

- [X] T021 Create FastAPI application instance in backend/rag-chatbot/app/main.py with lifespan context manager (startup: init DB pool, clients; shutdown: close connections)
- [X] T022 [P] Configure CORS middleware in backend/rag-chatbot/app/main.py using CORS_ORIGINS from config
- [X] T023 [P] Add Prometheus metrics middleware in backend/rag-chatbot/app/main.py (track request duration, endpoint, method)
- [X] T024 [P] Implement global exception handler in backend/rag-chatbot/app/middleware/error_handler.py (catch all exceptions, log with context, return standardized error response)
- [X] T025 [P] Implement request logging middleware in backend/rag-chatbot/app/middleware/request_logger.py (log request ID, method, path, duration, status code)
- [X] T026 Implement health check endpoint GET /health in backend/rag-chatbot/app/api/v1/health.py (check Postgres, Qdrant, OpenAI connectivity)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Ask Questions About Textbook Content (Priority: P1) 🎯 MVP

**Goal**: Enable students to ask natural language questions about any textbook content and receive accurate answers with source citations within 3 seconds

**Independent Test**: Submit question "What is a ROS 2 node?" and verify response includes accurate information with citations to Module 1, response time <3s

**Estimated Effort**: 12-16 hours

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T027 [P] [US1] Create contract test for POST /chat endpoint in backend/rag-chatbot/tests/contract/test_chat_contract.py (validate request schema: session_id UUID, question string 1-1000 chars; response schema: message_id, answer, citations array, metadata)
- [ ] T028 [P] [US1] Create integration test for basic Q&A flow in backend/rag-chatbot/tests/integration/test_basic_qa.py (mock OpenAI and Qdrant, test end-to-end: question → embedding → retrieval → generation → response with citations)
- [ ] T029 [P] [US1] Create performance test for latency requirement in backend/rag-chatbot/tests/performance/test_latency.py (verify 95% of requests complete <3s, test with 10 sample questions)

### Core RAG Components for User Story 1

- [ ] T030 [P] [US1] Implement text chunking utility in backend/rag-chatbot/app/services/chunking.py (chunk_markdown function: split by ## headings, target 500-1000 tokens per chunk, 50 token overlap, preserve chapter/section metadata)
- [ ] T031 [P] [US1] Implement embedding service in backend/rag-chatbot/app/services/embedding.py (generate_embedding async function using OpenAI text-embedding-3-small, handle rate limits with exponential backoff, batch support for ingestion)
- [ ] T032 [US1] Implement vector search service in backend/rag-chatbot/app/services/vector_search.py (search_similar_chunks async function: query Qdrant with top_k=10, score_threshold=0.70, return top-5 after filtering, include chunk metadata)
- [ ] T033 [US1] Implement citation builder in backend/rag-chatbot/app/services/citation_builder.py (build_citations function: extract chapter, section, url, confidence_score, text_snippet from search results, deduplicate by chapter)
- [ ] T034 [US1] Implement LLM service in backend/rag-chatbot/app/services/llm.py (generate_response async function using GPT-4o-mini, system prompt with citation instructions per research.md, context assembly from retrieved chunks, token counting)
- [ ] T035 [US1] Implement core RAG pipeline orchestrator in backend/rag-chatbot/app/services/rag.py (execute_rag_pipeline async function: 1.generate embedding 2.search vectors 3.build context 4.generate response 5.extract citations, comprehensive error handling, per-stage latency logging)

### Session Management for User Story 1

- [ ] T036 [US1] Implement session creation endpoint POST /sessions in backend/rag-chatbot/app/api/v1/sessions.py (generate UUID, store in DB, return session_id and created_at, handle optional user_id)
- [ ] T037 [US1] Implement session validation middleware in backend/rag-chatbot/app/middleware/session_validator.py (verify session_id exists in DB, update last_activity timestamp, rate limiting per session)

### Chat Endpoint for User Story 1

- [ ] T038 [US1] Implement POST /chat endpoint in backend/rag-chatbot/app/api/v1/chat.py (accept ChatRequest with session_id and question, validate inputs, call RAG pipeline, store user message and assistant response in DB, return ChatResponse with message_id, answer, citations, metadata including retrieval_time_ms, generation_time_ms, total_time_ms)
- [ ] T039 [US1] Add request/response models in backend/rag-chatbot/app/models/schemas.py (ChatRequest, ChatResponse, Citation, SessionResponse, ErrorResponse per openapi.yaml)
- [ ] T040 [US1] Implement error handling for POST /chat (handle OpenAI API failures with retry, Qdrant unavailable with degraded service message, invalid session_id with 404, rate limit exceeded with 429)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can ask questions and receive answers with citations

---

## Phase 4: User Story 4 - Receive Streaming Responses (Priority: P2)

**Goal**: Enable real-time streaming of answers token-by-token to reduce perceived wait time and provide progressive disclosure

**Independent Test**: Ask question with stream=true flag and verify tokens appear progressively (first token <500ms, continuous streaming until complete)

**Estimated Effort**: 6-8 hours

### Tests for User Story 4 ⚠️

- [ ] T041 [P] [US4] Create streaming integration test in backend/rag-chatbot/tests/integration/test_streaming.py (verify SSE format, first token <500ms, incremental token delivery, final complete event with citations)
- [ ] T042 [P] [US4] Create streaming disconnect test in backend/rag-chatbot/tests/integration/test_streaming_disconnect.py (simulate client disconnect during streaming, verify graceful cleanup, no resource leaks)

### Streaming Implementation for User Story 4

- [ ] T043 [US4] Implement SSE streaming wrapper in backend/rag-chatbot/app/services/streaming.py (stream_rag_response async generator: yield token events, citation events, complete event per openapi.yaml StreamingChatResponse schema, handle client disconnect)
- [ ] T044 [US4] Add streaming support to LLM service in backend/rag-chatbot/app/services/llm.py (generate_response_stream async generator using OpenAI streaming API, yield tokens as received, accumulate full response for storage)
- [ ] T045 [US4] Update POST /chat endpoint in backend/rag-chatbot/app/api/v1/chat.py to support stream parameter (if stream=true return StreamingResponse with text/event-stream media type, otherwise return JSON, store complete response after streaming finishes)
- [ ] T046 [US4] Add streaming error handling (handle OpenAI stream interruption, emit error event, fallback to non-streaming on failure)

**Checkpoint**: Streaming responses work - users see progressive token delivery for better UX

---

## Phase 5: User Story 2 - Get Contextual Help for Selected Text (Priority: P2)

**Goal**: Enable students to highlight confusing text passages and ask questions focused specifically on that context

**Independent Test**: Select text from Module 2, submit with question "Explain this in simpler terms?", verify response focuses on selected text context

**Estimated Effort**: 4-6 hours

### Tests for User Story 2 ⚠️

- [ ] T047 [P] [US2] Create contract test for POST /chat/selected endpoint in backend/rag-chatbot/tests/contract/test_selected_contract.py (validate request schema: session_id, question, selected_text 10-5000 chars; response matches ChatResponse schema)
- [ ] T048 [P] [US2] Create integration test for selected text mode in backend/rag-chatbot/tests/integration/test_selected_text.py (verify retrieval is filtered/weighted toward selected text, answer focuses on selection context, test with short and long selections)

### Selected Text Implementation for User Story 2

- [ ] T049 [US2] Implement hybrid search strategy in backend/rag-chatbot/app/services/vector_search.py (search_with_context async function: generate embedding for selected_text, boost relevance scores for chunks matching selection context, filter by chapter if determinable from selection)
- [ ] T050 [US2] Update RAG pipeline orchestrator in backend/rag-chatbot/app/services/rag.py to support selected_text mode (modify execute_rag_pipeline to accept optional selected_text, call hybrid search, augment system prompt to indicate focus on selection, pass selected_text to LLM context)
- [ ] T051 [US2] Implement POST /chat/selected endpoint in backend/rag-chatbot/app/api/v1/chat.py (accept SelectedTextChatRequest per openapi.yaml, validate selected_text length 10-5000 chars, call RAG pipeline with selection context, store selected_text in message metadata, return ChatResponse)
- [ ] T052 [US2] Add SelectedTextChatRequest model in backend/rag-chatbot/app/models/schemas.py per openapi.yaml (session_id, question, selected_text, optional stream)

**Checkpoint**: Selected text mode works - users can ask targeted questions about highlighted passages

---

## Phase 6: User Story 3 - Review Chat History Across Sessions (Priority: P3)

**Goal**: Enable students to access their conversation history from previous sessions and continue learning from past interactions

**Independent Test**: Create session, ask 5 questions, retrieve history via GET /chat/history, verify all messages returned chronologically with citations intact

**Estimated Effort**: 4-5 hours

### Tests for User Story 3 ⚠️

- [ ] T053 [P] [US3] Create contract test for GET /chat/history endpoint in backend/rag-chatbot/tests/contract/test_history_contract.py (validate query params: session_id required UUID, limit 1-100 default 50, offset >=0 default 0; response schema: ChatHistoryResponse with messages array)
- [ ] T054 [P] [US3] Create integration test for history retrieval in backend/rag-chatbot/tests/integration/test_history.py (create session with 10 messages, retrieve with pagination, verify chronological order, test session not found 404, verify no data leakage between sessions)

### History Implementation for User Story 3

- [ ] T055 [US3] Implement optimized history query in backend/rag-chatbot/app/db/crud.py (get_conversation_history async function: fetch messages by session_id ordered by timestamp DESC, support limit and offset pagination, include total count, use idx_messages_session_timestamp index)
- [ ] T056 [US3] Implement GET /chat/history endpoint in backend/rag-chatbot/app/api/v1/chat.py (validate session_id exists, call get_conversation_history, return ChatHistoryResponse per openapi.yaml with messages array, total, limit, offset, handle session not found with 404)
- [ ] T057 [US3] Add ChatHistoryResponse and HistoryMessage models in backend/rag-chatbot/app/models/schemas.py per openapi.yaml (session_id, messages list, pagination fields)
- [ ] T058 [US3] Implement session archival script in backend/rag-chatbot/scripts/archive_sessions.py (mark sessions as archived after 90 days inactivity, delete after 1 year, scheduled via cron per data-model.md)

**Checkpoint**: Chat history works - users can review past conversations and continue learning

---

## Phase 7: Content Ingestion Pipeline

**Purpose**: Load all 23 textbook chapters into Qdrant vector database

**Estimated Effort**: 6-8 hours

- [ ] T059 [P] Implement markdown parser in backend/rag-chatbot/app/services/markdown_parser.py (parse_docusaurus_chapter function: extract frontmatter, split by ## headings, preserve section hierarchy, extract chapter/module from file path, handle code blocks and images)
- [ ] T060 Implement batch embedding generation in backend/rag-chatbot/app/services/embedding.py (batch_generate_embeddings async function: process list of text chunks, batch requests to OpenAI API in groups of 100, handle rate limits, progress logging)
- [ ] T061 Implement ingestion orchestrator in backend/rag-chatbot/scripts/ingest_textbook.py (main CLI script: --source path to docs, --batch-size default 250, walk directory tree, parse all .md files, chunk content, generate embeddings, upsert to Qdrant with metadata per data-model.md PointStruct, progress bar, error recovery)
- [ ] T062 [P] Add incremental ingestion support in backend/rag-chatbot/scripts/ingest_textbook.py (--incremental flag: check file modification times, only re-embed changed chapters, update existing points in Qdrant)
- [ ] T063 [P] Create ingestion validation script in backend/rag-chatbot/scripts/validate_ingestion.py (verify all 23 chapters ingested, check expected chunk count ~460, validate metadata completeness, test sample searches)

**Checkpoint**: All textbook content loaded and searchable in Qdrant

---

## Phase 8: Performance Optimization & Monitoring

**Purpose**: Ensure <3 second response time target and production-grade observability

**Estimated Effort**: 4-6 hours

- [ ] T064 [P] Implement connection pooling optimizations in backend/rag-chatbot/app/clients/db_client.py (tune pool parameters: max_queries=50000, max_inactive_connection_lifetime=300s, command_timeout=10s)
- [ ] T065 [P] Implement keep-alive for Neon Postgres in backend/rag-chatbot/app/clients/db_client.py (background task: ping DB every 60s to prevent cold starts)
- [ ] T066 [P] Add per-stage latency tracking in backend/rag-chatbot/app/services/rag.py (instrument RAG pipeline with timers: embedding_time_ms, retrieval_time_ms, context_build_time_ms, generation_time_ms, storage_time_ms, log slow requests >3s)
- [ ] T067 [P] Implement request concurrency limiting in backend/rag-chatbot/app/middleware/rate_limiter.py (per-session rate limiter: 10 requests/minute using sliding window, return 429 when exceeded)
- [ ] T068 [P] Add Prometheus metrics endpoint GET /metrics in backend/rag-chatbot/app/api/v1/metrics.py (expose rag_request_duration_seconds histogram, rag_errors_total counter, process metrics)
- [ ] T069 Create performance benchmark script in backend/rag-chatbot/tests/performance/benchmark.py (test suite: 100 sample questions from all chapters, measure p50, p95, p99 latency, concurrent user simulation, verify <3s p95 target met)

**Checkpoint**: Performance targets met and monitoring in place

---

## Phase 9: Error Handling & Security Hardening

**Purpose**: Production-grade error handling and security measures

**Estimated Effort**: 4-5 hours

- [ ] T070 [P] Implement retry logic with exponential backoff for OpenAI API in backend/rag-chatbot/app/clients/openai_client.py (max 3 retries, backoff: 1s, 2s, 4s, handle rate limit 429, timeout errors, log retry attempts)
- [ ] T071 [P] Implement circuit breaker for external services in backend/rag-chatbot/app/utils/circuit_breaker.py (open circuit after 5 consecutive failures, half-open after 60s, apply to OpenAI and Qdrant clients)
- [ ] T072 [P] Add input validation and sanitization in backend/rag-chatbot/app/middleware/input_validator.py (sanitize question text, validate UUIDs, check string lengths, prevent injection attacks)
- [ ] T073 [P] Implement request/response validation with Pydantic in all endpoints (strict schema validation, clear error messages for validation failures, return 400 with details)
- [ ] T074 [P] Add security headers middleware in backend/rag-chatbot/app/middleware/security_headers.py (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, Content-Security-Policy)
- [ ] T075 Create security audit script in backend/rag-chatbot/scripts/security_audit.py (check: no hardcoded secrets, .env not in git, database credentials secure, API keys in environment only, validate CORS configuration)

**Checkpoint**: Production security hardening complete

---

## Phase 10: Testing & Documentation

**Purpose**: Comprehensive test coverage and developer documentation

**Estimated Effort**: 6-8 hours

### Unit Tests

- [ ] T076 [P] Create unit tests for chunking service in backend/rag-chatbot/tests/unit/test_chunking.py (test: chunk size validation 500-1000 tokens, overlap handling 50 tokens, heading preservation, edge cases: empty content, very short content, very long sections)
- [ ] T077 [P] Create unit tests for embedding service in backend/rag-chatbot/tests/unit/test_embedding.py (mock OpenAI API, test: successful embedding generation, batch processing, rate limit handling, error scenarios)
- [ ] T078 [P] Create unit tests for vector search in backend/rag-chatbot/tests/unit/test_vector_search.py (mock Qdrant client, test: top-k retrieval, score threshold filtering, metadata extraction, empty results handling)
- [ ] T079 [P] Create unit tests for citation builder in backend/rag-chatbot/tests/unit/test_citation_builder.py (test: citation formatting, confidence score mapping, URL validation, deduplication by chapter)
- [ ] T080 [P] Create unit tests for RAG pipeline in backend/rag-chatbot/tests/unit/test_rag_pipeline.py (mock all external services, test: successful pipeline execution, error propagation, latency tracking, context assembly)

### Integration Tests

- [ ] T081 [P] Create end-to-end test for full user journey in backend/rag-chatbot/tests/integration/test_e2e_journey.py (test flow: create session → ask question → verify answer → check history → ask with selected text → verify streaming, use test database and mocked OpenAI/Qdrant)
- [ ] T082 [P] Create database integration tests in backend/rag-chatbot/tests/integration/test_database.py (test: session CRUD, message persistence, history pagination, concurrent access, connection pool behavior)
- [ ] T083 [P] Create health check integration test in backend/rag-chatbot/tests/integration/test_health.py (test: all dependencies up, Postgres down scenario, Qdrant down scenario, OpenAI down scenario)

### Documentation

- [ ] T084 [P] Create API usage guide in backend/rag-chatbot/docs/api-usage.md (document all endpoints with curl examples, authentication, error codes, rate limits, streaming usage)
- [ ] T085 [P] Create development guide in backend/rag-chatbot/docs/development.md (setup instructions, running tests, debugging, common issues, architecture overview diagram)
- [ ] T086 [P] Create deployment guide in backend/rag-chatbot/docs/deployment.md (Docker deployment, environment configuration, monitoring setup, scaling considerations, backup/restore procedures)
- [ ] T087 [P] Update quickstart.md validation in backend/rag-chatbot/docs/ (verify all quickstart.md commands work: setup, database init, ingestion, server start, API tests)

**Checkpoint**: Comprehensive testing and documentation complete

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements affecting multiple user stories

**Estimated Effort**: 3-4 hours

- [ ] T088 [P] Add OpenAPI documentation enhancements in backend/rag-chatbot/app/main.py (custom title, description, version, contact info, example requests/responses, tags for endpoint grouping)
- [ ] T089 [P] Implement graceful shutdown in backend/rag-chatbot/app/main.py (lifespan shutdown: drain pending requests max 30s, close DB pool, close HTTP clients, log shutdown complete)
- [ ] T090 [P] Add request ID tracking in backend/rag-chatbot/app/middleware/request_logger.py (generate UUID for each request, include in all logs, return in X-Request-ID response header for debugging)
- [ ] T091 [P] Create monitoring dashboard configuration in backend/rag-chatbot/monitoring/grafana-dashboard.json (panels: request latency p50/p95/p99, error rate, concurrent requests, OpenAI API latency, Qdrant search latency, database pool utilization)
- [ ] T092 [P] Implement log rotation configuration in backend/rag-chatbot/app/utils/logging.py (rotate logs daily, keep 30 days, compress old logs, separate error.log and app.log)
- [ ] T093 Code cleanup and refactoring (remove unused imports, add type hints to all functions, run black formatter, fix flake8 violations, ensure mypy passes)
- [ ] T094 Run full test suite with coverage in backend/rag-chatbot/ (pytest --cov=app --cov-report=html tests/, target 85% coverage, verify all user stories pass integration tests)
- [ ] T095 Validate quickstart.md end-to-end (follow all setup steps on clean environment, verify server starts, test all API endpoints, check logs and metrics)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately (2-3 hours)
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories (6-8 hours)
- **User Story 1 (Phase 3)**: Depends on Foundational - MVP critical path (12-16 hours)
- **User Story 4 (Phase 4)**: Depends on Foundational + US1 chat endpoint - Adds streaming (6-8 hours)
- **User Story 2 (Phase 5)**: Depends on Foundational + US1 RAG pipeline - Adds selected text (4-6 hours)
- **User Story 3 (Phase 6)**: Depends on Foundational + US1 session management - Adds history (4-5 hours)
- **Content Ingestion (Phase 7)**: Depends on Foundational + US1 vector search - Can run parallel to user stories (6-8 hours)
- **Performance (Phase 8)**: Depends on US1 complete - Optimizes latency (4-6 hours)
- **Security (Phase 9)**: Depends on US1 complete - Can run parallel to other phases (4-5 hours)
- **Testing (Phase 10)**: Depends on corresponding user stories - Tests can be written first (6-8 hours)
- **Polish (Phase 11)**: Depends on all desired user stories complete (3-4 hours)

### User Story Dependencies

- **User Story 1 (P1)**: MVP - No dependencies on other stories after Foundational complete
- **User Story 4 (P2)**: Extends US1 chat endpoint with streaming - Needs US1 complete
- **User Story 2 (P2)**: Extends US1 RAG pipeline with selected text - Needs US1 complete
- **User Story 3 (P3)**: Uses US1 session management - Needs US1 complete

### Within Each User Story

For User Stories with tests:
1. Write tests FIRST (contract, integration, performance)
2. Run tests - verify they FAIL
3. Implement core components (models, services)
4. Implement API endpoints
5. Run tests - verify they PASS
6. Add error handling and logging
7. Story complete

### Parallel Opportunities

**Phase 1 (Setup)**: All tasks T003-T008 can run in parallel (5 tasks)

**Phase 2 (Foundational)**:
- Configuration group: T010, T011 parallel (after T009)
- Database models: T014, T015 parallel (after T013)
- External clients: T018 parallel with T017
- Middleware: T022, T023, T024, T025 all parallel (after T021)

**Phase 3 (User Story 1)**:
- Tests: T027, T028, T029 all parallel
- Core components: T030, T031 parallel before T032
- Session: T036, T037 parallel

**Phase 4 (User Story 4)**:
- Tests: T041, T042 parallel

**Phase 5 (User Story 2)**:
- Tests: T047, T048 parallel

**Phase 6 (User Story 3)**:
- Tests: T053, T054 parallel

**Phase 7 (Ingestion)**:
- T059, T060 parallel before T061
- T062, T063 parallel after T061

**Phase 8-11**: Most tasks marked [P] can run in parallel within their phase

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task T027: "Contract test for POST /chat in tests/contract/test_chat_contract.py"
Task T028: "Integration test for Q&A flow in tests/integration/test_basic_qa.py"
Task T029: "Performance test for latency in tests/performance/test_latency.py"

# Launch all parallelizable core components for User Story 1:
Task T030: "Implement chunking in app/services/chunking.py"
Task T031: "Implement embedding in app/services/embedding.py"

# After T030, T031 complete, sequential dependencies:
Task T032: "Implement vector search in app/services/vector_search.py"
Task T033: "Implement citation builder in app/services/citation_builder.py"
Task T034: "Implement LLM service in app/services/llm.py"
Task T035: "Implement RAG pipeline in app/services/rag.py"

# Launch session management tasks in parallel:
Task T036: "Implement POST /sessions in app/api/v1/sessions.py"
Task T037: "Implement session validator in app/middleware/session_validator.py"
```

---

## Implementation Strategy

### MVP First (Recommended - User Story 1 Only)

**Timeline**: ~20-27 hours total

1. **Phase 1: Setup** (2-3 hours)
   - Create project structure, dependencies, Docker setup

2. **Phase 2: Foundational** (6-8 hours)
   - Configuration, database, clients, FastAPI app
   - ⚠️ CRITICAL: Must complete before US1

3. **Phase 3: User Story 1** (12-16 hours)
   - Tests → RAG components → Endpoints
   - **STOP and VALIDATE**: Test end-to-end Q&A flow

4. **Phase 7: Content Ingestion** (6-8 hours)
   - Load all 23 chapters into Qdrant
   - Validate search quality

5. **Phase 8: Performance** (4-6 hours)
   - Optimize for <3s latency target
   - Add monitoring

**Deliverable**: Working RAG chatbot with basic Q&A, citations, monitoring

---

### Incremental Delivery (All User Stories)

**Timeline**: ~55-70 hours total

1. **Foundation** (8-11 hours): Setup + Foundational
2. **MVP** (12-16 hours): User Story 1 → Test independently → Deploy/Demo
3. **Streaming** (6-8 hours): User Story 4 → Test independently → Deploy/Demo
4. **Selected Text** (4-6 hours): User Story 2 → Test independently → Deploy/Demo
5. **History** (4-5 hours): User Story 3 → Test independently → Deploy/Demo
6. **Content** (6-8 hours): Phase 7 ingestion → Validate
7. **Production Ready** (8-11 hours): Performance + Security + Testing
8. **Polish** (3-4 hours): Documentation + Final cleanup

**Deliverable**: Production-grade RAG chatbot with all features

---

### Parallel Team Strategy

With 3 developers after Foundation complete:

1. **Team completes Setup + Foundational together** (8-11 hours)
2. **Parallel user story development**:
   - Developer A: User Story 1 (P1) - Core Q&A (12-16 hours)
   - Developer B: Phase 7 - Content Ingestion (6-8 hours), then User Story 2 (4-6 hours)
   - Developer C: Performance infrastructure (4-6 hours), then User Story 4 (6-8 hours)
3. **Integration**: User Story 3 + Testing + Security (8-10 hours)
4. **Polish**: Documentation + Cleanup (3-4 hours)

**Timeline**: ~20-25 hours with parallelization (vs ~55-70 hours sequential)

---

## Task Summary

**Total Tasks**: 95 tasks across 11 phases

**Tasks by Phase**:
- Phase 1 (Setup): 8 tasks
- Phase 2 (Foundational): 18 tasks
- Phase 3 (User Story 1 - P1): 14 tasks
- Phase 4 (User Story 4 - P2): 6 tasks
- Phase 5 (User Story 2 - P2): 4 tasks
- Phase 6 (User Story 3 - P3): 4 tasks
- Phase 7 (Ingestion): 5 tasks
- Phase 8 (Performance): 6 tasks
- Phase 9 (Security): 6 tasks
- Phase 10 (Testing): 12 tasks
- Phase 11 (Polish): 8 tasks

**Tasks by User Story**:
- User Story 1 (Ask Questions): 14 tasks - **MVP CRITICAL**
- User Story 2 (Selected Text): 4 tasks
- User Story 3 (History): 4 tasks
- User Story 4 (Streaming): 6 tasks

**Parallelizable Tasks**: 52 tasks marked [P] (55% can run in parallel)

**Estimated Timeline**:
- MVP (US1 only): 20-27 hours
- Full Feature (All user stories): 55-70 hours sequential
- Full Feature (3 developers parallel): 20-25 hours

---

## Next Steps

### Immediate: Start Implementation

```bash
# Option 1: Bootstrap project structure
/sp.bootstrap

# Option 2: Start implementing tasks manually
# Begin with Phase 1: Setup tasks T001-T008
```

### Validation Checkpoints

After each phase, validate:
- **Phase 2 (Foundational)**: Health check endpoint returns 200, all dependencies connected
- **Phase 3 (User Story 1)**: Ask "What is a ROS 2 node?" → Get answer with citations <3s
- **Phase 4 (User Story 4)**: Same question with stream=true → Tokens appear progressively
- **Phase 5 (User Story 2)**: Select text + ask question → Answer focuses on selection
- **Phase 6 (User Story 3)**: Create session, ask questions, retrieve history → All preserved
- **Phase 7 (Ingestion)**: Verify ~460 chunks in Qdrant, test sample searches
- **Phase 8 (Performance)**: Run benchmark → p95 latency <3s
- **Phase 11 (Polish)**: Run full test suite → 85%+ coverage, all tests pass

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Write tests first, verify they fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Foundational phase is CRITICAL - blocks all user stories
- Performance optimization is essential for <3s response time requirement
- Use structured logging extensively for debugging production issues
- Monitor Prometheus metrics to track latency improvements
