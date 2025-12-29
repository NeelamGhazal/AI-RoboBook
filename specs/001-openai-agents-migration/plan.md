# Implementation Plan: OpenAI Agents SDK Migration for RAG Chatbot

**Branch**: `001-openai-agents-migration` | **Date**: 2025-12-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-openai-agents-migration/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Migrate the hackathon RAG chatbot backend from direct Google Gemini integration to OpenAI Agents SDK compliance using `set_default_openai_client()` with OpenRouter's base_url override. The system will route all Agents SDK requests to OpenRouter's Mistral Devstral free model (`mistralai/devstral-2512:free`), ensuring proper SDK usage for hackathon evaluation while maintaining the existing RAG pipeline functionality (Qdrant vector search → top 3 chunks → context retrieval → streaming responses with citations). This approach avoids Gemini's restrictive free tier quota (~20-100 RPD) and requires zero custom adapter code, zero frontend changes, zero database schema modifications.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- FastAPI 0.115.0 (existing async web framework)
- openai-agents (to be added - official OpenAI Agents SDK)
- openai 1.51.0 (existing - will configure with OpenRouter base_url)
- qdrant-client 1.16.2 (existing vector database client)
- asyncpg 0.29.0 (existing async Postgres client)
- sentence-transformers 2.2.2 (existing local embedding model)
- pydantic 2.9.2, structlog 24.4.0 (existing infrastructure)
- google-generativeai 0.8.3 (existing - will be deprecated/unused post-migration)

**Storage**:
- Qdrant Cloud (Free Tier) - vector database for semantic search (existing, unchanged)
- Neon Serverless Postgres - chat sessions and message persistence (existing, unchanged)

**Testing**: pytest (existing test infrastructure)
**Target Platform**: Linux server (Railway deployment via Docker)
**Project Type**: Web (FastAPI backend API serving frontend chatbot widget)
**Performance Goals**:
- <3 seconds p90 response time (first token to stream)
- Support 100 concurrent requests without rate limiting errors
- Streaming token delivery with <200ms Agents SDK overhead

**Constraints**:
- MUST work with free OpenRouter/Mistral Devstral only (no OpenAI paid credits)
- MUST maintain frontend compatibility (no changes to request/response format)
- MUST preserve existing database schemas (no migrations)
- MUST use ONLY openai.agents SDK classes with AsyncOpenAI client configured for OpenRouter
- MUST keep RAG pipeline functional (no mock responses, top 3 chunks, 12 message history limit)
- MUST handle quota errors with immediate failure (no retries)

**Scale/Scope**:
- Hackathon demo scale: 100-200 requests during evaluation (no quota issues with OpenRouter)
- 6 Python files to modify (main.py, llm.py, config.py, chat.py + 2 test files)
- 1 new package dependency (openai-agents)
- ~300 lines of code to refactor (NO custom adapter needed - just configuration + llm service updates)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle Alignment

**✅ II. AI-Native Architecture (PRIMARY DRIVER)**
- **Requirement**: "RAG chatbot MUST use OpenAI Agents/ChatKit SDKs with FastAPI backend"
- **Current State**: Using direct Gemini integration (non-compliant)
- **Post-Migration**: Custom LLM adapter implementing Agents SDK interface (compliant)
- **Impact**: Achieves hackathon compliance without sacrificing free-tier Gemini usage

**✅ III. Technical Rigor (MAINTAINED)**
- **Requirement**: "All code examples MUST be tested, reproducible, and follow established conventions"
- **Approach**: Adapter class follows Agents SDK interface contracts, existing tests will be updated to mock Agents SDK instead of direct Gemini client
- **Compliance**: Proper abstraction layer, no shortcuts or workarounds

**✅ I. Educational Excellence (PRESERVED)**
- **Requirement**: "Chatbot MUST support general Q&A with <3 seconds response time, selected text queries, context-aware follow-ups, source citations"
- **Impact**: No degradation - RAG pipeline remains functional, streaming preserved, citations intact
- **Verification**: All acceptance scenarios from spec remain testable

**✅ V. Claude Code Integration (IN PROGRESS)**
- **Requirement**: "Every user interaction MUST generate PHR, architectural decisions MUST be surfaced for ADR"
- **Current Status**: Using /sp.plan workflow, will create PHR upon completion
- **ADR Candidate**: Custom LLM adapter pattern decision (already documented in spec FR-002, may warrant ADR if pattern is reusable)

### Gate Results

| Gate | Status | Evidence |
|------|--------|----------|
| Maintains RAG functionality | ✅ PASS | No changes to rag.py pipeline, vector_search.py, or Qdrant integration |
| No frontend breaking changes | ✅ PASS | Request/response schemas unchanged, streaming event format preserved |
| Free tier compatible | ✅ PASS | Continues using Gemini free API, zero OpenAI costs |
| Follows SDK patterns correctly | ⚠️ RESEARCH REQUIRED | Need to verify Agents SDK interface requirements in Phase 0 |
| Performance within constraints | ⚠️ DESIGN REQUIRED | Need to measure Agents SDK abstraction overhead in Phase 1 |

### Complexity Justification

**No violations requiring justification.** This migration adds one abstraction layer (Agents SDK adapter) which is architecturally justified by hackathon compliance requirements and follows the Adapter design pattern (GoF).

## Project Structure

### Documentation (this feature)

```text
specs/001-openai-agents-migration/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (in progress - /sp.plan output)
├── research.md          # Phase 0 output (pending)
├── data-model.md        # Phase 1 output (pending)
├── quickstart.md        # Phase 1 output (pending)
├── contracts/           # Phase 1 output (pending)
│   └── agents_sdk_interface.md  # Agents SDK adapter contract
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

**Existing Backend Structure** (will be modified):

```text
backend/rag-chatbot/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── chat.py               # ⚠️ ACTIVATE (currently inactive)
│   │       ├── chat_minimal.py       # ⚠️ DEACTIVATE (currently active)
│   │       └── sessions.py           # ✓ No changes
│   │
│   ├── clients/
│   │   ├── gemini_client.py          # 🔄 REPLACE with agents_adapter.py
│   │   ├── agents_adapter.py         # ➕ NEW (Agents SDK wrapper for Gemini)
│   │   ├── qdrant_client.py          # ✓ No changes
│   │   ├── db_client.py              # ✓ No changes
│   │   └── local_embedding_client.py # ✓ No changes
│   │
│   ├── services/
│   │   ├── llm.py                    # 🔄 REFACTOR (use agents_adapter instead of gemini_client)
│   │   ├── rag.py                    # ✓ Minimal changes (if any)
│   │   ├── vector_search.py          # ✓ No changes
│   │   └── citation_builder.py       # ✓ No changes
│   │
│   ├── models/
│   │   ├── schemas.py                # ✓ No changes (request/response schemas)
│   │   ├── session.py                # ✓ No changes
│   │   └── message.py                # ✓ No changes
│   │
│   ├── db/
│   │   └── crud.py                   # ✓ No changes
│   │
│   ├── utils/
│   │   ├── logging.py                # ⚠️ ADD (Agents SDK interaction logging)
│   │   └── metrics.py                # ✓ No changes
│   │
│   ├── config.py                     # ⚠️ UPDATE (no new env vars needed)
│   └── main.py                       # 🔄 CRITICAL (switch to chat.py, init agents_adapter)
│
├── tests/
│   ├── unit/
│   │   └── test_agents_adapter.py    # ➕ NEW
│   ├── integration/
│   │   └── test_rag_with_agents.py   # 🔄 UPDATE (mock Agents SDK)
│   └── contract/
│       └── test_streaming_contract.py # ✓ No changes (validates frontend compatibility)
│
└── requirements.txt                   # 🔄 ADD openai-agents

frontend/                              # ✓ NO CHANGES (out of scope)
```

**Structure Decision**: Web application (backend + frontend separation). This migration only modifies the backend layer. The critical path is:
1. Configure `AsyncOpenAI` client with OpenRouter base_url in `main.py` lifespan
2. Call `set_default_openai_client()` to set global Agents SDK client
3. Update `llm.py` to use `Agent` and `Runner` from `openai.agents`
4. Switch `main.py` routing from `chat_minimal.router` to `chat.router` (line 178)
5. Update `config.py` with OpenRouter env vars (OPENROUTER_API_KEY, OPENROUTER_MODEL, BASE_URL)

**Files Modified**: 6 total (main.py, llm.py, config.py, chat.py, requirements.txt, .env)
**Files Created**: 2 test files (test_openrouter_agents.py, test_rag_with_agents.py - update existing)
**Files Deleted**: 0 (gemini_client.py deprecated but kept for rollback reference)

**Critical Simplification** (Clarified 2025-12-25): No custom adapter class needed. OpenRouter provides native OpenAI-compatible endpoint, so `set_default_openai_client()` handles all routing. This reduces implementation from ~500 LOC to ~300 LOC.

## Implementation Phases

This migration follows a 4-phase approach with clear validation gates between each phase:

### Phase 1: Setup and Dependencies

**Objective**: Install and configure OpenAI Agents SDK with OpenRouter backend

**Tasks**:
1. ☐ Update `requirements.txt` with `openai-agents>=0.1.0`
2. ☐ Install dependencies: `pip install -r requirements.txt`
3. ☐ Configure `.env` with OpenRouter credentials:
   - `OPENROUTER_API_KEY=sk-or-v1-...`
   - `OPENROUTER_MODEL=mistralai/devstral-2512:free`
   - `BASE_URL=https://openrouter.ai/api/v1`
4. ☐ Update `app/config.py` Settings model with OpenRouter env vars
5. ☐ Test SDK installation: `python -c "from agents import Agent, Runner; print('✅ SDK ready')"`

**Validation Gate**:
- ✅ All imports work (`from agents import ...`)
- ✅ Server starts without import errors
- ✅ Environment variables load correctly

**Reference**: See `dependency-installation.md` for detailed setup instructions

---

### Phase 2: Client Configuration and Migration

**Objective**: Configure Agents SDK to use OpenRouter endpoint and migrate LLM service

**Tasks**:
1. ☐ Update `app/main.py` lifespan:
   - Create `AsyncOpenAI` client with `base_url="https://openrouter.ai/api/v1"`
   - Call `set_default_openai_client(openrouter_client)`
   - Log "agents_sdk_configured" message
2. ☐ Refactor `app/services/llm.py`:
   - Import `Agent`, `Runner` from `agents`
   - Remove `{context}` placeholder from `SYSTEM_PROMPT` (make static)
   - Create `RAG_AGENT = Agent(model="mistralai/devstral-2512:free", ...)`
   - Replace `gemini_client.generate_chat_completion_stream()` with `Runner.run_stream()`
   - Map `content_delta` events to token yields
3. ☐ Verify `app/api/endpoints/chat.py`:
   - Ensure it uses updated `llm.generate_response_stream()`
   - Verify message history limit (12 messages)
   - Confirm Qdrant top_k=3 retrieval
4. ☐ Update routing in `app/main.py`:
   - Switch from `chat_minimal.router` to `chat.router` (line ~178)

**Validation Gate**:
- ✅ Server starts and logs "agents_sdk_configured"
- ✅ No import errors from `agents` module
- ✅ Agent created with correct model name

**Reference**: See `file-modification-checklist.md` sections 2.1-3.2

---

### Phase 3: RAG Integration

**Objective**: Ensure Qdrant retrieval integrates properly with Agents SDK context

**Tasks**:
1. ☐ Verify context injection pattern in `llm.py`:
   - Context embedded in user message (not system prompt)
   - Format: `**Textbook Excerpts:**\n{context}\n\n**Question:** {question}`
2. ☐ Test Qdrant retrieval:
   - Verify `retrieve_chunks()` returns exactly 3 chunks
   - Confirm chunks have `text`, `chapter`, `section` fields
3. ☐ Test hybrid search (selected text queries):
   - Verify 70% query + 30% selected text embedding
   - Confirm top 3 chunks returned
4. ☐ Verify conversation history:
   - Last 12 messages included in context (if available)
   - Older messages truncated

**Validation Gate**:
- ✅ Qdrant retrieval returns 3 chunks
- ✅ Context appears in agent's user input
- ✅ Conversation history limited to 12 messages

**Reference**: See `contracts/agents_sdk_interface.md` sections 3.1-5.2

---

### Phase 4: Testing and Validation

**Objective**: Validate end-to-end functionality with real OpenRouter API

**Tasks**:
1. ☐ **Unit Tests** (mocked Agents SDK):
   - Create `tests/test_llm_agents.py`
   - Test agent creation, streaming, error handling, context injection
   - Run: `pytest tests/test_llm_agents.py -v`
2. ☐ **Integration Tests** (real OpenRouter):
   - Create `tests/test_integration_openrouter.py`
   - Test full RAG pipeline with real API
   - Run: `pytest tests/test_integration_openrouter.py -v -m integration`
3. ☐ **Manual Testing** (Postman/curl):
   - Test: `POST /api/v1/chat/stream` with sample question
   - Verify streaming tokens (progressive delivery)
   - Confirm response cites textbook content
4. ☐ **Performance Benchmarks**:
   - Measure average response time (should be <5s)
   - Measure first token latency (should be <3s p90)
   - Verify throughput handles concurrent requests
5. ☐ **Frontend Compatibility**:
   - Test chatbot widget with real backend
   - Verify streaming display works
   - Confirm citations render correctly

**Quality Checks (MUST ALL PASS)**:
- ✅ Response time < 5 seconds (average)
- ✅ Qdrant retrieval returns 3+ chunks
- ✅ Agent responses cite book content (not generic knowledge)
- ✅ No hardcoded/mock responses
- ✅ First token latency < 3 seconds (p90)
- ✅ Streaming works (no buffering)
- ✅ Error handling returns user-friendly messages

**Reference**: See `testing-validation.md` for complete test specifications

---

### Implementation Order (Critical Path)

Follow this exact sequence to minimize errors:

```
1. Phase 1: Setup
   └─> Install dependencies → Configure .env → Update config.py → Test imports

2. Phase 2: Migration
   └─> Configure main.py lifespan → Refactor llm.py → Update routing

3. Phase 3: RAG Integration
   └─> Verify context injection → Test Qdrant → Test history limits

4. Phase 4: Validation
   └─> Unit tests → Integration tests → Manual tests → Performance tests
```

**Rollback Points**:
- After Phase 1: Can abort with no code changes
- After Phase 2.3: Can switch routing back to `chat_minimal.router` in <5 minutes
- After Phase 4: Full rollback via git revert (gemini_client.py preserved)

---

## Planning Artifacts

This plan is supported by the following detailed planning documents:

| Artifact | Purpose | Location |
|----------|---------|----------|
| **Architecture Diagram** | System flow with Agents SDK integration | `architecture-diagram.md` |
| **File Modification Checklist** | Step-by-step code changes with validation | `file-modification-checklist.md` |
| **Dependency Installation** | Package setup and troubleshooting | `dependency-installation.md` |
| **Testing Validation** | 4-layer testing strategy with quality gates | `testing-validation.md` |
| **API Contracts** | Agents SDK interface specifications | `contracts/agents_sdk_interface.md` |
| **Quickstart Guide** | Developer onboarding and setup | `quickstart.md` |
| **Research Findings** | OpenRouter alternative analysis | `research.md` |
| **Clarifications** | User decisions and configuration details | `CLARIFICATIONS.md` |

**Next Step**: Execute `/sp.tasks` to generate actionable task breakdown from this plan.

---

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations detected.** The OpenRouter integration via `set_default_openai_client()` is a standard configuration pattern (3 lines of code) justified by hackathon SDK compliance requirements and Gemini quota limitations. No unnecessary complexity introduced.
