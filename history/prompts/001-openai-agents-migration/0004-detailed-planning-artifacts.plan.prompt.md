---
id: 0004
title: Detailed Planning Artifacts
stage: plan
date: 2025-12-25
surface: agent
model: claude-sonnet-4.5
feature: 001-openai-agents-migration
branch: 001-openai-agents-migration
user: user
command: /sp.plan
labels: ["planning", "architecture", "openrouter", "testing", "documentation"]
links:
  spec: specs/001-openai-agents-migration/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-openai-agents-migration/architecture-diagram.md (created)
  - specs/001-openai-agents-migration/file-modification-checklist.md (created)
  - specs/001-openai-agents-migration/dependency-installation.md (created)
  - specs/001-openai-agents-migration/testing-validation.md (created)
  - specs/001-openai-agents-migration/plan.md (updated with 4-phase implementation)
tests:
  - No tests created (planning phase)
  - Testing strategy documented in testing-validation.md
---

## Prompt

/sp.plan
Create:
- Architecture diagram showing Agents SDK integration flow
- File modification checklist
- Dependency installation steps
- Testing validation points

Technical approach (updated to use OpenRouter instead of direct Gemini):
Phase 1: Setup - Install openai-agents-sdk package, Configure OpenRouter as the LLM backend, Test SDK connection
Phase 2: Migration - Create agents_client.py with OpenAI Agents SDK patterns, Configure global OpenAI client to point to OpenRouter, Modify chat.py to use agents_client, Remove gemini_client.py imports
Phase 3: RAG Integration - Ensure Qdrant retrieval feeds into Agents SDK context, Implement system prompt for RAG instructions, Add context injection to agent messages
Phase 4: Validation - Test endpoint with Postman/curl, Verify Qdrant vectors are retrieved, Confirm responses use book content, Check frontend widget compatibility

Quality checks:
- Response time < 5 seconds
- Qdrant retrieval returns 3+ chunks
- Agent responses cite book content
- No hardcoded/mock responses

Additional configuration details:
- LLM Provider: OpenRouter
- Model: mistralai/devstral-2512:free (fully free, strong tool calling & reasoning, recommended on OpenRouter's coding page)
- Base URL: https://openrouter.ai/api/v1
- Integration method: set_default_openai_client() with custom OpenAI client pointing to OpenRouter

## Response snapshot

Created comprehensive planning artifacts for OpenAI Agents SDK migration with OpenRouter backend:

**1. Architecture Diagram** (`architecture-diagram.md`):
- System architecture overview showing full flow: Frontend → FastAPI → RAG Pipeline → Agents SDK → OpenRouter → Mistral Devstral
- Supporting infrastructure diagrams (Qdrant Cloud, Neon Postgres)
- Data flow sequence (9-step detailed walkthrough)
- Before/After comparison showing migration changes
- Configuration points (environment variables, startup config, agent definition)
- Error handling flow diagram
- Performance characteristics table
- Compliance verification points for hackathon judges

**2. File Modification Checklist** (`file-modification-checklist.md`):
- Complete 4-phase implementation guide (Setup → Migration → Integration → Testing)
- 6 files to modify with exact code changes and validation steps
- 2 new test files to create
- Execution order with rollback points
- Validation checklist (functional, performance, error handling, code quality)
- Troubleshooting guide for common issues
- Estimated LOC changes: ~173 lines across 8 files

**3. Dependency Installation Guide** (`dependency-installation.md`):
- Step-by-step installation process for `openai-agents>=0.1.0`
- Python 3.11+ requirement verification
- Virtual environment setup (Linux/macOS/Windows)
- Environment variable configuration (OpenRouter API key, model, base URL)
- Platform-specific instructions (Ubuntu, macOS, WSL2, native Windows)
- Dependency tree and compatibility notes
- Testing installation with verification scripts
- Troubleshooting section (SSL issues, version conflicts, permissions)
- Docker and cloud deployment notes

**4. Testing Validation Plan** (`testing-validation.md`):
- 4-layer testing strategy: Unit → Integration → Manual → Performance
- 7+ unit tests (mocked Agents SDK)
- 3 integration tests (real OpenRouter API)
- Manual testing procedures (Postman, curl)
- Performance benchmarks (latency, throughput)
- Quality requirement validation (response time <5s, top 3 chunks, cite book content)
- Pre-production validation checklist
- CI/CD configuration example (GitHub Actions)
- Test data fixtures

**5. Updated plan.md** with detailed implementation phases:
- Phase 1: Setup and Dependencies (5 tasks with validation gate)
- Phase 2: Client Configuration and Migration (4 tasks with validation gate)
- Phase 3: RAG Integration (4 tasks with validation gate)
- Phase 4: Testing and Validation (5 tasks with quality checks)
- Implementation order with critical path
- Rollback points at each phase
- Planning artifacts reference table

**Key Architectural Decisions**:
1. **OpenRouter Configuration**: Use `set_default_openai_client()` with `AsyncOpenAI(base_url="https://openrouter.ai/api/v1")` - eliminates need for custom adapter class
2. **Context Injection**: Embed Qdrant chunks in user message (not system prompt) since Agents SDK instructions should be static
3. **Streaming Pattern**: Map `Runner.run_stream()` events (content_delta → token yields) to maintain frontend compatibility
4. **Error Handling**: Fail-fast strategy (no retries) for quota/network errors
5. **Hardcoded Limits**: Top 3 chunks, 12 message history (not configurable for simplicity)

**Critical Path**:
```
Dependencies (requirements.txt, .env, config.py)
  ↓
Client Configuration (main.py lifespan with set_default_openai_client)
  ↓
LLM Service Refactor (llm.py with Agent + Runner)
  ↓
Routing Switch (main.py: chat_minimal → chat)
  ↓
Testing (unit, integration, manual, performance)
```

## Outcome

- ✅ Impact: Completed detailed planning phase with 4 comprehensive artifacts (architecture diagram, file checklist, dependency guide, testing strategy) and updated plan.md with 4-phase implementation roadmap. All planning deliverables from user request fulfilled. Implementation simplified from ~500 LOC (custom adapter) to ~173 LOC (configuration + refactoring) due to OpenRouter's native OpenAI compatibility.
- 🧪 Tests: No code tests created (planning phase). Defined 4-layer testing strategy with 10+ automated tests and quality gates. All tests documented in testing-validation.md.
- 📁 Files: Created 4 new planning artifacts (architecture-diagram.md, file-modification-checklist.md, dependency-installation.md, testing-validation.md), updated 1 existing file (plan.md with implementation phases).
- 🔁 Next prompts: `/sp.tasks` to generate actionable implementation task breakdown based on 4-phase plan, or begin implementation directly following file-modification-checklist.md.
- 🧠 Reflection: This planning phase transformed high-level clarifications into concrete, actionable implementation guides. The 4-phase approach provides clear validation gates and rollback points at each stage. The file modification checklist is particularly detailed with exact code changes, estimated LOC, and validation commands. The architecture diagram provides visual clarity for hackathon judges to verify Agents SDK compliance. OpenRouter integration pattern is now fully documented with all edge cases covered (error handling, performance, testing). Ready for immediate implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None. Planning artifacts are comprehensive and internally consistent. All user-requested deliverables completed.
- Graders run and results (PASS/FAIL): PASS - All 4 planning artifacts created, plan.md updated with 4-phase implementation, quality checks defined, validation gates established, rollback strategy documented.
- Prompt variant (if applicable): Standard /sp.plan workflow extended with specific deliverables request (architecture diagram, checklists, installation guide, testing plan). User provided detailed 4-phase technical approach which was incorporated directly into plan.md.
- Next experiment (smallest change to try): Proceed directly to implementation following file-modification-checklist.md Phase 1 (dependency installation), or execute /sp.tasks to generate granular task breakdown. Consider whether additional ADR is needed for "OpenRouter vs Gemini" decision (already well-documented in CLARIFICATIONS.md and research.md Finding 7).
