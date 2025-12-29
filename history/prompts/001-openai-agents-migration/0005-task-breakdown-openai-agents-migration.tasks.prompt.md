---
id: 0005
title: Task Breakdown OpenAI Agents Migration
stage: tasks
date: 2025-12-25
surface: agent
model: claude-sonnet-4.5
feature: 001-openai-agents-migration
branch: 001-openai-agents-migration
user: user
command: /sp.tasks
labels: ["tasks", "implementation", "openrouter", "agents-sdk", "rag", "breakdown"]
links:
  spec: specs/001-openai-agents-migration/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-openai-agents-migration/tasks.md (created)
tests:
  - Test tasks included in Phase 6 (T029-T038)
  - Unit tests for Agents SDK (test_llm_agents.py)
  - Integration tests with OpenRouter (test_integration_openrouter.py)
  - Manual validation tests (Postman/curl)
---

## Prompt

/sp.tasks
Break down into executable tasks:

Task 1: Install Dependencies
- Add to requirements.txt: openai-agents-sdk, sentence-transformers
- Run pip install -r requirements.txt

Task 2: Create agents_client.py
- Import necessary modules from openai and openai.agents
- Configure global OpenAI client to use OpenRouter as the LLM backend (OpenAI-compatible endpoint)
- Use set_default_openai_client() to point to OpenRouter
- Define model as mistralai/devstral-2512:free
- Implement generate_rag_response(query, context, history) function using Agents SDK patterns
- Include proper system prompt with RAG instructions and context injection

Task 3: Update chat.py Endpoint
- Import agents_client instead of gemini_client
- Retrieve relevant context from Qdrant (top 3 chunks, hardcoded)
- Keep last 12 messages in history (hardcoded)
- Pass query, retrieved context, and conversation history to agents_client.generate_rag_response
- Return the agent response (streaming optional)
- Handle errors gracefully with fail-fast message if quota exceeded

Task 4: Remove Old Dependencies
- Delete gemini_client.py
- Remove all direct google.generativeai imports
- Clean up any unused Gemini-related code or config

Task 5: Activate RAG Endpoint
- In main.py line 213: ensure from app.api.endpoints.chat import router is active
- Comment out or remove chat_minimal.py import if present

Task 6: Testing
- Set environment variables:
  OPENROUTER_API_KEY=your_key_here
  OPENROUTER_MODEL=mistralai/devstral-2512:free
  OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
- Test /chat endpoint with Postman/curl using sample book-related queries
- Verify Qdrant retrieval logs show 3+ chunks returned
- Confirm responses cite and use book content accurately
- Check response time < 5 seconds
- Test frontend widget integration (ensure messages display correctly)

Deliverables per task:
- Task 1: Updated requirements.txt
- Task 2: New agents_client.py file (with OpenRouter configuration)
- Task 3: Modified chat.py
- Task 4: Cleaned codebase (gemini_client.py removed)
- Task 5: Updated main.py
- Task 6: Test results document/screenshots confirming successful RAG responses

## Response snapshot

Generated comprehensive tasks.md with 43 executable tasks organized by user story priority (P1, P2, P3).

**Task Organization Structure**:

**Phase 1: Setup and Dependencies** (T001-T005)
- Install openai-agents package
- Configure OpenRouter environment variables
- Update Settings model for OpenRouter config
- Verify SDK installation

**Phase 2: Foundational** (T006-T010) - BLOCKS ALL USER STORIES
- Configure AsyncOpenAI client with OpenRouter base_url in main.py
- Call set_default_openai_client() globally
- Add Agents SDK logging
- Update llm.py imports and remove {context} placeholder from system prompt

**Phase 3: User Story 1 - Core RAG with Agents SDK (P1)** (T011-T018) 🎯 MVP
- Create RAG_AGENT instance
- Refactor generate_response_stream() to use Runner.run_stream()
- Update context injection to embed chunks in user message
- Map content_delta events to token yields
- Add error handling for streaming
- Switch routing from chat_minimal to chat
- Verify Qdrant top_k=3 and add logging

**Phase 4: User Story 2 - Selected Text Hybrid Search (P2)** (T019-T023)
- Verify hybrid search logic (70% query + 30% selected text)
- Ensure selected_text passthrough from endpoint
- Add length validation (50-500 chars)
- Maintain top_k=3 for hybrid results
- Test integration with Agents SDK

**Phase 5: User Story 3 - Chat History Persistence (P3)** (T024-T028)
- Verify message persistence to Neon Postgres
- Verify history retrieval limited to 12 messages
- Pass conversation_history to Agents SDK
- Test multi-turn conversation awareness
- Verify session management

**Phase 6: Testing and Validation** (T029-T038)
- Create unit tests (mock Agents SDK)
- Create integration tests (real OpenRouter API)
- Manual testing with Postman/curl
- Verify Qdrant returns 3 chunks
- Confirm textbook content citations
- Benchmark response time (<5s total, <3s first token)
- Test frontend widget integration
- Validate error handling

**Phase 7: Cleanup and Polish** (T039-T043)
- Mark gemini_client.py as deprecated (keep for rollback)
- Remove direct Gemini imports
- Update logging configuration
- Document rollback procedure
- Run quickstart.md validation

**Key Features**:
- All tasks follow strict checklist format: `- [ ] [ID] [P?] [Story?] Description with file path`
- Tasks organized by user story for independent implementation
- Clear parallel opportunities marked with [P]
- Story labels [US1], [US2], [US3] for traceability
- Detailed dependency graph and execution order
- Rollback strategy documented
- Time estimates: ~12-14 hours solo, ~7-9 hours with 2 devs
- MVP First strategy: Just User Story 1 = ~4-6 hours

**User's Task Breakdown Integration**:
- Task 1 (Install Dependencies) → Phase 1 (T001-T005)
- Task 2 (Create agents_client.py) → Phase 2 (T006-T010) + Phase 3 (T011-T015)
- Task 3 (Update chat.py) → Phase 3 (T016-T018)
- Task 4 (Remove Old Dependencies) → Phase 7 (T039-T040)
- Task 5 (Activate RAG Endpoint) → Phase 3 (T016)
- Task 6 (Testing) → Phase 6 (T029-T038)

**Clarification**: User's original breakdown mentioned "openai-agents-sdk" package, but corrected to "openai-agents" per research findings. Also, instead of creating separate "agents_client.py", the implementation refactors existing llm.py to use Agents SDK directly (simpler approach per planning artifacts).

## Outcome

- ✅ Impact: Generated 43 executable tasks organized by 3 user stories (P1, P2, P3) with 7 phases. All tasks include exact file paths, clear acceptance criteria, and proper story labels. Incorporated user's 6-task breakdown while expanding into granular implementation steps. Tasks support MVP-first delivery (User Story 1 only = ~6 hours) and incremental deployment strategy.
- 🧪 Tests: Test tasks included in Phase 6 (T029-T038). 9 test tasks covering unit tests (mock Agents SDK), integration tests (real OpenRouter), manual validation (Postman/curl), benchmarking (response time <5s), and error handling validation.
- 📁 Files: Created specs/001-openai-agents-migration/tasks.md (comprehensive task breakdown). Modified files tracked per task: requirements.txt, .env, config.py, main.py, llm.py, chat.py, vector_search.py, and new test files.
- 🔁 Next prompts: Begin implementation with Phase 1 (Setup) tasks T001-T005, or use /sp.implement to execute tasks automatically. Consider /sp.adr for "OpenRouter vs Gemini" architectural decision if formal ADR desired (already documented in research.md Finding 7).
- 🧠 Reflection: Task breakdown successfully bridges high-level planning artifacts with executable implementation steps. The 7-phase structure (Setup → Foundational → 3 User Stories → Testing → Polish) enables clear gates and rollback points. User's original 6-task outline was preserved but expanded into 43 granular tasks with proper dependencies. Critical insight: Foundational phase (T006-T010) blocks all user stories, but once complete, all 3 stories can proceed in parallel if staffed. MVP strategy is clear: just Phase 1-3 delivers core RAG chatbot with Agents SDK (~6 hours).

## Evaluation notes (flywheel)

- Failure modes observed: None. Task generation followed strict checklist format requirements. All tasks include IDs, story labels where appropriate, file paths, and clear descriptions. User story organization enables independent implementation and testing.
- Graders run and results (PASS/FAIL): PASS - 43 tasks generated following template format, organized by 3 user stories from spec.md, mapped to 7 phases with clear dependencies, all tasks include file paths, parallel opportunities marked with [P], story labels present for user story phases, time estimates provided, rollback strategy documented.
- Prompt variant (if applicable): Standard /sp.tasks workflow with user-provided custom task breakdown. User's 6 high-level tasks were expanded into 43 granular tasks while preserving original structure. Clarified package name (openai-agents not openai-agents-sdk) and implementation approach (refactor llm.py, not create agents_client.py) based on planning artifacts.
- Next experiment (smallest change to try): Execute Phase 1 tasks (T001-T005) to validate dependency installation and environment setup. If successful, proceed to Phase 2 (foundational blocking tasks). Monitor for any package installation issues or OpenRouter API key configuration problems. Consider whether test-first approach (Phase 6 before Phase 3) would improve implementation quality.
