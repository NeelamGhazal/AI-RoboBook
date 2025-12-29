# Tasks: OpenAI Agents SDK Migration for RAG Chatbot

**Input**: Design documents from `/specs/001-openai-agents-migration/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, file-modification-checklist.md

**Tests**: Tests are NOT explicitly requested in the spec, but the user's task breakdown includes "Task 6: Testing" with validation steps. Test tasks included for completeness.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a web application with backend/frontend separation:
- Backend: `backend/rag-chatbot/`
- Frontend: No changes (out of scope)

---

## Phase 1: Setup and Dependencies

**Purpose**: Install OpenAI Agents SDK and configure OpenRouter integration

- [X] T001 Add `openai-agents>=0.1.0` to backend/rag-chatbot/requirements.txt
- [X] T002 Install dependencies via `pip install -r requirements.txt` in backend/rag-chatbot/
- [X] T003 [P] Add OpenRouter env vars to backend/rag-chatbot/.env (OPENROUTER_API_KEY, OPENROUTER_MODEL=mistralai/devstral-2512:free, BASE_URL=https://openrouter.ai/api/v1)
- [X] T004 [P] Update Settings model in backend/rag-chatbot/app/config.py to include OPENROUTER_API_KEY, OPENROUTER_MODEL, and BASE_URL fields
- [X] T005 Verify Agents SDK installation: `python -c "from agents import Agent, Runner, set_default_openai_client; print('✅ Agents SDK installed')"`

**Validation Gate**:
- ✅ All imports work (`from agents import ...`)
- ✅ Server starts without import errors
- ✅ Environment variables load correctly from .env

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Configure global OpenAI client to route Agents SDK requests to OpenRouter

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Configure AsyncOpenAI client with OpenRouter base_url in backend/rag-chatbot/app/main.py lifespan startup
- [X] T007 Call set_default_openai_client(openrouter_client) in backend/rag-chatbot/app/main.py lifespan startup
- [X] T008 Add logging for "agents_sdk_configured" event with model and base_url in backend/rag-chatbot/app/main.py
- [X] T009 Update imports in backend/rag-chatbot/app/services/llm.py to import Agent, Runner from agents module
- [X] T010 Remove {context} placeholder from SYSTEM_PROMPT in backend/rag-chatbot/app/services/llm.py (make static system instruction)

**Checkpoint**: Foundation ready - OpenRouter client configured globally, Agents SDK ready to use

---

## Phase 3: User Story 1 - RAG-Powered Chat with OpenAI Agents SDK (Priority: P1) 🎯 MVP

**Goal**: Implement core RAG chatbot using OpenAI Agents SDK with OpenRouter/Mistral Devstral backend. This replaces direct Gemini integration while maintaining retrieval-augmented responses with citations.

**Independent Test**: Send POST to `/api/v1/chat/stream` with question "What is ROS 2?", verify response includes Qdrant-retrieved context (3 chunks), is generated via Agents SDK (not mock), and includes citations.

**Acceptance Scenarios**:
1. User asks "What is ROS 2?" → System retrieves top 3 chunks from Qdrant → Passes to Agents SDK via OpenRouter → Streams contextual answer with citations
2. Backend configured with only free OpenRouter API key → Agents SDK routes to OpenRouter via base_url → Returns valid response using Mistral Devstral
3. User asks about topic not in textbook → Qdrant returns no chunks → Agents SDK responds "I couldn't find relevant information in the textbook"

### Implementation for User Story 1

- [X] T011 [US1] Create RAG_AGENT instance in backend/rag-chatbot/app/services/llm.py using Agent(name="TextbookRAGAgent", model=settings.OPENROUTER_MODEL, instructions=SYSTEM_PROMPT, tools=[])
- [X] T012 [US1] Refactor generate_response_stream() in backend/rag-chatbot/app/services/llm.py to use Runner.run_stream() instead of gemini_client.generate_chat_completion_stream()
- [X] T013 [US1] Update context injection pattern in backend/rag-chatbot/app/services/llm.py to embed chunks in user message as "**Textbook Excerpts:**\n{context}\n\n**Question:** {question}"
- [X] T014 [US1] Map Runner.run_stream() event.type == "content_delta" to token yields in backend/rag-chatbot/app/services/llm.py
- [X] T015 [US1] Add error handling for event.type == "error" in backend/rag-chatbot/app/services/llm.py streaming loop (raise RuntimeError with fail-fast behavior)
- [X] T016 [US1] Switch routing in backend/rag-chatbot/app/main.py from chat_minimal.router to chat.router (line ~178)
- [X] T017 [US1] Verify chat.py endpoint uses top_k=3 for Qdrant retrieval in backend/rag-chatbot/app/api/endpoints/chat.py
- [X] T018 [US1] Add logging for agent_request_started, agent_response_complete, and agent_error events in backend/rag-chatbot/app/services/llm.py

**Checkpoint**: At this point, User Story 1 should be fully functional - chatbot responds to queries using Agents SDK with OpenRouter, retrieves 3 chunks from Qdrant, streams responses with citations

---

## Phase 4: User Story 2 - Selected Text Context-Aware Responses (Priority: P2)

**Goal**: Enable hybrid vector search (70% query embedding + 30% selected text embedding) to provide contextually relevant responses when user selects text from the book.

**Independent Test**: Send POST to `/api/v1/chat/stream` with `{"message": "How does this work?", "selected_text": "ROS 2 uses DDS for communication"}`, verify response is contextually relevant to selected text using hybrid search.

**Acceptance Scenarios**:
1. User selects text from Chapter 3 about simulation, asks "How does this work?" → Hybrid search (70% query + 30% selected text) → Retrieves contextually relevant chunks → Agents SDK generates response addressing selected passage
2. Selected text is 50 characters → System accepts it (minimum threshold) → Includes in hybrid search
3. Selected text exceeds 500 characters → System truncates it → Uses for hybrid retrieval

### Implementation for User Story 2

- [X] T019 [US2] Verify hybrid search logic exists in backend/rag-chatbot/app/services/vector_search.py (70% query embedding + 30% selected text embedding)
- [X] T020 [US2] Ensure selected_text parameter is passed through from chat.py endpoint to vector_search in backend/rag-chatbot/app/api/endpoints/chat.py
- [X] T021 [US2] Add selected_text length validation (min 50 chars, max 500 chars, truncate if needed) in backend/rag-chatbot/app/api/endpoints/chat.py
- [X] T022 [US2] Verify top_k=3 is maintained for hybrid search results in backend/rag-chatbot/app/services/vector_search.py
- [X] T023 [US2] Test selected text query with Agents SDK context injection in backend/rag-chatbot/app/services/llm.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - general queries use standard search, selected text queries use hybrid search

---

## Phase 5: User Story 3 - Chat History Persistence (Priority: P3)

**Goal**: Maintain conversation context by persisting messages to Neon Postgres and including last 12 messages in Agents SDK prompts for multi-turn conversations.

**Independent Test**: Create session, send multiple messages, verify subsequent responses show awareness of prior conversation (e.g., "As I mentioned earlier...").

**Acceptance Scenarios**:
1. User has session with 5 prior messages → System includes last 5 messages in Agents SDK context → Generates response aware of conversation history
2. User has session with 20 prior messages → System includes only most recent 12 messages → Generates coherent response (avoids context overflow)
3. New session created → First message sent → System generates response without conversation history → Saves both user question and assistant response to Neon Postgres

### Implementation for User Story 3

- [ ] T024 [US3] Verify message persistence to Neon Postgres exists in backend/rag-chatbot/app/db/crud.py (save_message function)
- [ ] T025 [US3] Verify conversation history retrieval limited to 12 messages in backend/rag-chatbot/app/api/endpoints/chat.py
- [ ] T026 [US3] Ensure conversation_history is passed to Agents SDK via Runner.run_stream() context_variables (or as part of user input) in backend/rag-chatbot/app/services/llm.py
- [ ] T027 [US3] Test multi-turn conversation with Agents SDK context awareness in backend/rag-chatbot/app/services/llm.py
- [ ] T028 [US3] Verify session creation and last_activity_at updates work with Agents SDK flow in backend/rag-chatbot/app/api/endpoints/chat.py

**Checkpoint**: All user stories should now be independently functional - general queries, selected text queries, and multi-turn conversations all work with Agents SDK

---

## Phase 6: Testing and Validation

**Purpose**: Comprehensive testing to validate Agents SDK integration meets quality requirements

- [ ] T029 [P] Create tests/test_llm_agents.py with unit tests for RAG_AGENT creation, streaming, error handling, context injection (mock Runner.run_stream)
- [ ] T030 [P] Create tests/test_integration_openrouter.py with integration tests using real OpenRouter API (require OPENROUTER_API_KEY)
- [ ] T031 Test POST /api/v1/chat/stream endpoint with Postman/curl using sample question "What is ROS 2?"
- [ ] T032 Verify Qdrant retrieval logs show exactly 3 chunks returned for test queries
- [ ] T033 Confirm responses cite textbook content accurately (not generic knowledge)
- [ ] T034 Benchmark response time: ensure p90 < 3 seconds for first token, total < 5 seconds
- [ ] T035 Test frontend widget integration: verify messages display correctly with streaming tokens
- [ ] T036 Run all unit tests: `pytest tests/test_llm_agents.py -v`
- [ ] T037 Run integration tests: `pytest tests/test_integration_openrouter.py -v -m integration`
- [ ] T038 Validate error handling: test with invalid OPENROUTER_API_KEY, verify fail-fast with user-friendly message

**Validation Checklist**:
- ✅ Response time < 5 seconds (average)
- ✅ Qdrant retrieval returns 3+ chunks
- ✅ Agent responses cite book content (not generic knowledge)
- ✅ No hardcoded/mock responses
- ✅ First token latency < 3 seconds (p90)
- ✅ Streaming works (no buffering)
- ✅ Error handling returns user-friendly messages

---

## Phase 7: Cleanup and Polish

**Purpose**: Remove deprecated code and finalize migration

- [ ] T039 [P] Mark gemini_client.py as deprecated in backend/rag-chatbot/app/clients/gemini_client.py (add deprecation comment, keep file for rollback)
- [ ] T040 [P] Remove direct google.generativeai imports from backend/rag-chatbot/app/services/llm.py (if any remain)
- [ ] T041 Update logging configuration to include Agents SDK interaction metadata in backend/rag-chatbot/app/utils/logging.py
- [ ] T042 Document rollback procedure in specs/001-openai-agents-migration/ROLLBACK.md (switch routing back to chat_minimal.router)
- [ ] T043 Run quickstart.md validation to ensure developer setup guide is accurate

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational - Integrates with US1 but independently testable
  - User Story 3 (P3): Can start after Foundational - Integrates with US1 but independently testable
- **Testing (Phase 6)**: Depends on User Story 1 completion (minimum), ideally all user stories
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

```
Foundational Phase (Phase 2) [BLOCKS ALL]
    ├── User Story 1 (Phase 3) - Core RAG with Agents SDK [INDEPENDENT]
    ├── User Story 2 (Phase 4) - Selected text hybrid search [INDEPENDENT after US1]
    └── User Story 3 (Phase 5) - Chat history persistence [INDEPENDENT after US1]
```

### Within Each User Story

**User Story 1**:
1. Create RAG_AGENT instance (T011)
2. Refactor streaming logic (T012-T015) - parallel eligible
3. Switch routing (T016)
4. Verify and log (T017-T018) - parallel eligible

**User Story 2**:
1. Verify hybrid search logic (T019)
2. Ensure selected_text passthrough (T020-T022) - parallel eligible
3. Test integration (T023)

**User Story 3**:
1. Verify persistence (T024)
2. Verify history retrieval (T025-T026) - parallel eligible
3. Test multi-turn conversations (T027-T028)

### Parallel Opportunities

**Phase 1 (Setup)**:
- T003 (env vars) and T004 (config.py) can run in parallel

**Phase 2 (Foundational)**:
- T006-T008 (main.py changes) sequential
- T009-T010 (llm.py changes) can run after T006-T008

**Phase 3 (User Story 1)**:
- T011 (create agent) first
- T012-T015 (refactor streaming) sequential
- T017-T018 (logging) can be parallel with T012-T015

**Phase 6 (Testing)**:
- T029 and T030 (test file creation) can run in parallel
- T031-T035 (manual tests) can run in parallel
- T036-T038 (automated tests) sequential

**Parallel Team Strategy**:
Once Foundational (Phase 2) completes:
- Developer A: User Story 1 (Phase 3)
- Developer B: User Story 2 (Phase 4) - starts after US1 basics done
- Developer C: User Story 3 (Phase 5) - starts after US1 basics done

---

## Parallel Example: User Story 1

```bash
# After T011 (agent creation) completes:

# Launch refactoring tasks together:
Task T012: "Refactor generate_response_stream() in app/services/llm.py"
Task T013: "Update context injection pattern in app/services/llm.py"
Task T014: "Map Runner.run_stream() events in app/services/llm.py"
Task T015: "Add error handling in app/services/llm.py"

# Then after streaming refactor:
Task T016: "Switch routing in app/main.py"

# Then in parallel:
Task T017: "Verify Qdrant top_k=3 in app/api/endpoints/chat.py"
Task T018: "Add logging in app/services/llm.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T010) - CRITICAL
3. Complete Phase 3: User Story 1 (T011-T018)
4. **STOP and VALIDATE**: Test with curl/Postman, verify Agents SDK integration
5. Deploy to staging/demo if ready

**Time Estimate**: ~4-6 hours for experienced developer (MVP only)

### Incremental Delivery

1. **Foundation** (Phase 1-2): Setup + OpenRouter client configured → ~2 hours
2. **MVP** (Phase 3): User Story 1 → Test independently → Deploy/Demo → ~3 hours
3. **Enhancement 1** (Phase 4): User Story 2 → Test independently → Deploy/Demo → ~2 hours
4. **Enhancement 2** (Phase 5): User Story 3 → Test independently → Deploy/Demo → ~1 hour
5. **Quality** (Phase 6): Testing → Validation → ~3 hours
6. **Finalize** (Phase 7): Cleanup → Documentation → ~1 hour

**Total Estimate**: ~12-14 hours for complete migration

### Parallel Team Strategy

With 2 developers:

1. **Together**: Complete Setup + Foundational (Phase 1-2) → ~2 hours
2. **Split**:
   - Developer A: User Story 1 (Phase 3) → ~3 hours
   - Developer B: Setup test infrastructure (Phase 6, T029-T030) → ~2 hours
3. **Developer A**: User Story 2 (Phase 4) → ~2 hours
4. **Developer B**: User Story 3 (Phase 5) → ~1 hour
5. **Together**: Testing + Validation (Phase 6, T031-T038) → ~2 hours
6. **Either**: Cleanup (Phase 7) → ~1 hour

**Total Estimate with 2 devs**: ~7-9 hours wall-clock time

---

## Rollback Strategy

**Immediate Rollback** (if Agents SDK integration fails in production):

1. In `backend/rag-chatbot/app/main.py` line ~178:
   ```python
   # Switch back to mock endpoint
   app.include_router(chat_minimal.router, prefix="/api/v1/chat", tags=["chat"])
   # app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
   ```

2. Restart server: `uvicorn app.main:app --reload`

3. Verify health check: `curl http://localhost:8000/health`

**Rollback SLA**: <5 minutes (simple routing change)

**Full Rollback** (if OpenRouter experiences downtime):

1. Revert to gemini_client usage in `backend/rag-chatbot/app/services/llm.py`
2. Re-enable Gemini client initialization in `backend/rag-chatbot/app/main.py` lifespan
3. Ensure GOOGLE_API_KEY is set in .env

**Note**: gemini_client.py is kept (deprecated but not deleted) specifically for emergency rollback.

---

## Notes

- **[P]** tasks = different files, no dependencies, can run in parallel
- **[Story]** label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group (e.g., after T005, T010, T018, etc.)
- Stop at any checkpoint to validate story independently
- All file paths use `backend/rag-chatbot/` prefix (web app structure)
- Tests are included for completeness per user's Task 6 request
- **Critical Path**: Phase 1 → Phase 2 (blocks all) → Phase 3 (MVP) → Phase 6 (validation)
- **Quality Gates**: Response time <5s, 3 chunks from Qdrant, cite book content, no mock data
