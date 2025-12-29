# Feature Specification: OpenAI Agents SDK Migration for RAG Chatbot

**Feature Branch**: `001-openai-agents-migration`
**Created**: 2025-12-24
**Updated**: 2025-12-25 (Clarifications incorporated)
**Status**: Specification Complete
**Input**: User description: "Migrate hackathon chatbot backend to OpenAI Agents SDK with free LLM provider"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - RAG-Powered Chat with OpenAI Agents SDK (Priority: P1)

A hackathon judge evaluates the chatbot implementation by asking a question about textbook content. The system retrieves relevant chunks from Qdrant, passes them to an OpenAI Agents SDK wrapper (configured to use OpenRouter with Mistral Devstral as the underlying LLM), and streams back a retrieval-augmented response with citations.

**Why this priority**: This is the core hackathon requirement - demonstrating proper OpenAI Agents SDK integration with a functional RAG pipeline. Without this, the submission fails compliance.

**Independent Test**: Can be fully tested by sending a POST request to `/api/v1/chat/stream` with a question, verifying that the response includes retrieved context from Qdrant and is generated via the OpenAI Agents SDK (not mock/canned responses), and delivers accurate, citation-backed answers.

**Acceptance Scenarios**:

1. **Given** a user sends "What is ROS 2?" to the chatbot, **When** the backend processes the request, **Then** the system retrieves top 3 relevant chunks from Qdrant, passes them through the OpenAI Agents SDK (using OpenRouter/Devstral underneath), and streams back a contextual answer with citations to source sections.

2. **Given** the backend is configured with only a free OpenRouter API key (no OpenAI paid credits), **When** a chat request is processed, **Then** the OpenAI Agents SDK successfully routes the request to OpenRouter via base_url override and returns a valid response using the Mistral Devstral model.

3. **Given** a user asks a question about a topic not in the textbook, **When** Qdrant returns no relevant chunks, **Then** the system responds via the Agents SDK with "I couldn't find relevant information in the textbook" rather than hallucinating.

---

### User Story 2 - Selected Text Context-Aware Responses (Priority: P2)

A user selects text from the published book (e.g., a paragraph about humanoid robotics) and asks "What are the key challenges here?" The chatbot uses hybrid vector search (weighted combination of query + selected text embeddings) to retrieve relevant context and generates a targeted response via the OpenAI Agents SDK.

**Why this priority**: This demonstrates advanced RAG capabilities and is a unique hackathon feature differentiator, but the basic RAG flow (P1) must work first.

**Independent Test**: Can be tested independently by sending a POST request with both `question` and `selected_text` fields, verifying that the response is contextually relevant to the selected text, not just a general answer.

**Acceptance Scenarios**:

1. **Given** a user selects text from Chapter 3 about simulation and asks "How does this work?", **When** the backend processes the request, **Then** the system performs hybrid search (70% query embedding + 30% selected text embedding), retrieves contextually relevant chunks, and generates a response via the Agents SDK that directly addresses the selected passage.

2. **Given** the selected text is 50 characters long, **When** the request is processed, **Then** the system accepts it (minimum threshold) and includes it in the hybrid search.

3. **Given** the selected text exceeds 500 characters, **When** the request is processed, **Then** the system truncates it (maximum threshold) to prevent context overflow while still using it for hybrid retrieval.

---

### User Story 3 - Chat History Persistence (Priority: P3)

A user has a multi-turn conversation with the chatbot. Each question-answer pair is stored in Neon Postgres with session tracking. When the user asks a follow-up question, the system includes the last 12 messages as conversation context in the Agents SDK prompt.

**Why this priority**: This enhances user experience but is not critical for demonstrating core RAG + Agents SDK compliance. The database setup already exists from the previous implementation.

**Independent Test**: Can be tested by creating a session, sending multiple messages, and verifying that subsequent responses show awareness of prior conversation (e.g., "As I mentioned earlier...").

**Acceptance Scenarios**:

1. **Given** a user has a session with 5 prior messages, **When** they ask a follow-up question, **Then** the system includes the last 5 messages in the Agents SDK context and generates a response aware of the conversation history.

2. **Given** a user has a session with 20 prior messages, **When** they ask a new question, **Then** the system includes only the most recent 12 messages (to avoid context overflow) and generates a coherent response.

3. **Given** a new session is created, **When** the first message is sent, **Then** the system generates a response without conversation history and saves both user question and assistant response to Neon Postgres.

---

### Edge Cases

- What happens when the Gemini API key is invalid or quota exceeded? **Expected**: The Agents SDK should raise a clear error that propagates to the frontend with a user-friendly message ("Service temporarily unavailable").

- What happens when Qdrant connection fails? **Expected**: The system logs an error, skips retrieval, and responds via Agents SDK with "Unable to search textbook content at this time" rather than crashing.

- What happens when a user sends an empty question? **Expected**: The API returns a 400 Bad Request with validation error before invoking the Agents SDK.

- What happens when the selected_text is provided but is empty or whitespace-only? **Expected**: The system treats it as a general query (ignores selected_text) and proceeds with standard semantic search.

- What happens when the Neon Postgres database is unavailable? **Expected**: Session creation fails gracefully, but in-memory fallback allows the chat to continue (messages not persisted).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST use the OpenAI Agents SDK (openai.agents module) as the exclusive interface for LLM interactions, replacing all direct Gemini client usage.

- **FR-002**: System MUST configure the OpenAI Agents SDK to use OpenRouter's API endpoint via `set_default_openai_client()` with base_url override, routing all requests to the Mistral Devstral free model (`mistralai/devstral-2512:free`) without requiring a custom adapter class.

- **FR-003**: System MUST NOT use the legacy `openai.OpenAI` client anywhere in the codebase - only `openai.agents` SDK classes and patterns.

- **FR-004**: System MUST maintain the existing RAG pipeline flow: user question → Qdrant vector search → retrieved chunks → Agents SDK prompt with context → streamed response.

- **FR-005**: System MUST register the real RAG endpoint (`app/api/v1/chat.py`) in `main.py` instead of the mock endpoint (`chat_minimal.py`), ensuring all chatbot responses are retrieval-augmented.

- **FR-006**: System MUST support both general queries (standard semantic search retrieving top 3 chunks) and selected-text queries (hybrid search: 70% query embedding + 30% selected text embedding, retrieving top 3 chunks).

- **FR-007**: System MUST stream responses token-by-token using the Agents SDK's async streaming interface, not buffering the entire response before sending.

- **FR-008**: System MUST include retrieved citations (source, page, text snippet, confidence score) in the streamed response alongside the generated answer.

- **FR-009**: System MUST persist all user questions and assistant responses to Neon Postgres with session tracking, maintaining compatibility with the existing database schema.

- **FR-010**: System MUST include the last 12 messages from the current session as conversation history in the Agents SDK prompt context (if available). This limit is hardcoded for simplicity.

- **FR-011**: System MUST use the existing Qdrant vector database without modifications to the collection schema, embeddings, or indexing strategy.

- **FR-012**: System MUST preserve frontend compatibility - no changes to request/response payloads, API endpoints, or streaming event format (data: {type, content/citations/metadata}).

- **FR-013**: System MUST handle errors from the Agents SDK (API quota, network failures, invalid responses) gracefully with immediate failure (no retries), returning user-friendly error messages to the frontend ("Service temporarily unavailable").

- **FR-014**: System MUST log all Agents SDK interactions (prompts, responses, token counts, latency) using the existing structlog infrastructure for debugging and evaluation.

- **FR-015**: System MUST NOT introduce any new paid dependencies or services - the migration must work with only the free OpenRouter API key using the `mistralai/devstral-2512:free` model (no OpenAI credits or paid API usage required).

### Key Entities

- **OpenAI Agent Configuration**: Global configuration via `set_default_openai_client()` that routes Agents SDK requests to OpenRouter's base_url (`https://openrouter.ai/api/v1`) using the Mistral Devstral free model. This replaces the current `gemini_client` in `app/services/llm.py`.

- **RAG Context**: The combination of retrieved chunks, conversation history, and system prompt that gets passed to the Agents SDK. This must be formatted according to the SDK's expected message structure.

- **Stream Event**: The JSON objects yielded during streaming (`{type: "token", content: "..."}`, `{type: "citations", citations: [...]}`, `{type: "done"}`). Format must remain unchanged for frontend compatibility.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Hackathon judges can verify OpenAI Agents SDK usage by inspecting imports in `app/services/llm.py` (must show `from openai.agents import ...` instead of direct Gemini imports).

- **SC-002**: All chatbot responses are retrieval-augmented - 100% of answers include context from Qdrant, verified by the presence of citations in the response payload.

- **SC-003**: The chatbot operates successfully using only a free OpenRouter API key with Mistral Devstral model, with zero OpenAI paid API calls (confirmed by absence of OpenAI API key in environment variables and logs, presence of OpenRouter base_url in configuration).

- **SC-004**: Chat response latency remains under 3 seconds for 90% of queries (measured from API request to first token streamed), ensuring the Agents SDK overhead is minimal.

- **SC-005**: The frontend chatbot widget continues to function without any code changes - requests to `/api/v1/chat/stream` return valid streamed responses in the existing event format.

- **SC-006**: Selected text queries (hybrid search) produce contextually relevant responses 95% of the time when evaluated against a test set of 20 selected passages + questions.

- **SC-007**: The system handles 100 concurrent chat requests without Agents SDK rate limiting errors, demonstrating proper connection pooling and semaphore usage.

- **SC-008**: All unit tests for the RAG pipeline pass after migration, and new integration tests verify Agents SDK behavior (mock Gemini responses in tests).

## Assumptions

1. **Free Tier Availability**: OpenRouter's Mistral Devstral free model supports the query volume expected during hackathon evaluation (100-200 requests) without quota restrictions that plagued the direct Gemini free tier (reduced to ~20-100 RPD in December 2025).

2. **Streaming Compatibility**: We assume the Agents SDK's async streaming interface is compatible with FastAPI's StreamingResponse when using OpenRouter's OpenAI-compatible endpoint. If incompatible, we will buffer chunks and re-stream them.

3. **Message Format**: We assume the Agents SDK expects messages in a similar format to the OpenAI Chat API (role + content arrays). If format differs significantly, we will need a transformation layer.

4. **No Breaking Changes**: We assume the migration will not require database schema changes, frontend updates, or deployment configuration changes beyond adding the openai-agents library to requirements.txt.

5. **Existing Embeddings**: We assume the current Qdrant collection uses sentence-transformers embeddings (384-dim) and these do not need to be regenerated for the Agents SDK migration.

6. **Performance**: We assume the Agents SDK overhead when using OpenRouter's endpoint will not add more than 200ms latency compared to direct API calls. OpenRouter itself adds minimal routing overhead (~50-100ms).

## Out of Scope

- Migrating the embedding generation to the Agents SDK - embeddings will continue to use the existing sentence-transformers local model (free, no API calls).

- Implementing multi-agent workflows or agentic tool use - this is a simple RAG chatbot, not an autonomous agent system.

- Adding new chatbot features beyond what currently exists (e.g., voice input, image generation) - this is strictly a migration, not an enhancement.

- Optimizing the RAG pipeline performance (chunk size, retrieval strategy, prompt engineering) - the focus is on SDK compliance, not RAG improvements.

- Supporting multiple LLM providers simultaneously - we're migrating from direct Gemini to Agents SDK + OpenRouter (Mistral Devstral), not creating a multi-provider abstraction.

- Retraining or fine-tuning the LLM - we're using Mistral Devstral as-is via OpenRouter and the Agents SDK.

- Changing the frontend chat widget UI, features, or behavior - frontend remains completely unchanged.

- Deploying to production or updating CI/CD pipelines - this migration is for hackathon demo purposes, deployment is separate.

## Dependencies

- **OpenAI Agents SDK**: Must add `openai-agents` to `requirements.txt`. Version compatibility with Python 3.11+ required.

- **OpenRouter API Key**: Free API key from OpenRouter (https://openrouter.ai/) must be configured in `.env` as `OPENROUTER_API_KEY`. The Mistral Devstral model (`mistralai/devstral-2512:free`) is fully free with no quota restrictions for demo purposes.

- **Existing RAG Infrastructure**: Qdrant Cloud instance, Neon Postgres database, sentence-transformers model - all must remain operational during and after migration.

- **FastAPI + asyncpg**: No version changes expected, but must verify Agents SDK async/await patterns work with FastAPI's lifespan and dependency injection.

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Agents SDK doesn't support base_url override to OpenRouter | High - blocks entire migration | Low | **RESOLVED**: Research confirms `set_default_openai_client()` supports base_url override. OpenRouter provides OpenAI-compatible endpoint. |
| Streaming interface incompatible with FastAPI | Medium - degrades UX to non-streaming | Low | Implement buffering layer that collects Agents SDK chunks and re-streams them via FastAPI. |
| OpenRouter free model quota insufficient | Medium - demo fails during evaluation | Very Low | **MITIGATED**: Mistral Devstral free model has no hard quota limits for demos. Much more reliable than Gemini free tier (which was reduced to ~20-100 RPD in Dec 2025). |
| Performance degradation > 500ms | Medium - fails latency success criteria | Medium | Profile the Agents SDK overhead. If significant, optimize by reducing conversation history size or chunk count. |
| Breaking changes to message format | High - requires extensive refactoring | Low | Thoroughly test Agents SDK message format in isolated environment before integrating into RAG pipeline. Create adapter functions if needed. |
| Existing tests break after migration | Low - slows development | High | Update mocks to simulate Agents SDK instead of Gemini client. Add new integration tests for Agents SDK behavior. |

## Notes

- This migration is driven by hackathon compliance requirements, not technical necessity. The current Gemini direct integration works well, but the hackathon specifically requires "OpenAI Agents/ChatKit SDKs."

- The term "OpenAI Agents SDK" in the hackathon requirements refers to the official OpenAI Agents Python library documented at https://openai.github.io/openai-agents-python/. We use this exact library with package name `openai-agents`.

- **Technical Solution (Clarified 2025-12-25)**: Use `set_default_openai_client()` with OpenRouter's base_url (`https://openrouter.ai/api/v1`) and Mistral Devstral free model (`mistralai/devstral-2512:free`). This avoids Gemini's restrictive free tier quota (reduced to ~20-100 requests/day in December 2025) while maintaining full OpenAI Agents SDK compliance. OpenRouter provides better reliability and higher demo quota for hackathon evaluation.

- Success will be measured by both functional correctness (RAG pipeline works) and compliance verification (judges can see Agents SDK imports and usage in the code).

- The migration should be completed in a single feature branch to avoid leaving the codebase in a partially migrated state. All changes must be atomic and testable.
