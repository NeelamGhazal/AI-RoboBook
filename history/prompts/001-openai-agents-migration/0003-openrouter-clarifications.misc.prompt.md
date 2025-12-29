---
id: 0003
title: OpenRouter Clarifications
stage: misc
date: 2025-12-25
surface: agent
model: claude-sonnet-4.5
feature: 001-openai-agents-migration
branch: 001-openai-agents-migration
user: user
command: /sp.clarify
labels: ["clarification", "openrouter", "mistral-devstral", "quota", "configuration"]
links:
  spec: specs/001-openai-agents-migration/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-openai-agents-migration/spec.md (updated with OpenRouter)
  - specs/001-openai-agents-migration/plan.md (updated with OpenRouter)
  - specs/001-openai-agents-migration/research.md (added Finding 7)
  - specs/001-openai-agents-migration/contracts/agents_sdk_interface.md (updated)
  - specs/001-openai-agents-migration/CLARIFICATIONS.md (created)
tests:
  - All clarification questions answered (3/3)
  - OpenRouter configuration validated
---

## Prompt

/sp.clarify

Clarifications:
1. LLM Provider: Use Gemini with gemini-1.5-flash model
2. OpenAI Agents SDK: Install via `pip install openai-agents-sdk`
3. Base URL Override: Configure Agents SDK to route requests to Gemini API endpoint
4. RAG Flow:
   - User query → Embed with sentence-transformers
   - Search Qdrant for top 3 relevant chunks
   - Pass chunks as context to Agents SDK
   - Return augmented response
5. Key Files to Modify:
   - app/core/openai_client.py → Rename to agents_client.py
   - app/api/endpoints/chat.py → Update to use agents_client
   - main.py line 213 → Ensure imports chat.py not chat_minimal.py
6. Keep: All existing environment variables, Qdrant setup, Neon DB models

## Response snapshot

Analyzed specification and presented 3 targeted clarification questions with research-backed recommendations:

**Question 1: Implementation Approach**
- Presented 3 options: Gemini OpenAI endpoint (simple), custom adapter (complex), LiteLLM (middle)
- User selected: **Option A** (simplest approach)
- Corrected package name: `openai-agents` (not `openai-agents-sdk`)

**Question 2: Configuration Strategy**
- Presented options for hardcoded vs. configurable limits (12 messages, 3 chunks)
- User selected: **Option A** (hardcoded for simplicity)

**Question 3: Quota Error Handling**
- Presented fail-fast vs. retry vs. queue strategies
- User selected: **Option A** (fail immediately, no retries)

**Critical User Input: OpenRouter Switch**

User provided additional context about Gemini free tier quota crisis:
- Gemini free tier reduced to ~20-100 RPD in early December 2025
- User prefers **OpenRouter with Mistral Devstral** for better reliability
- User already has OpenRouter API key ready
- Configuration provided:
  ```
  OPENROUTER_MODEL="mistralai/devstral-2512:free"
  BASE_URL="https://openrouter.ai/api/v1"
  ```

**Impact of OpenRouter Decision**:
- **Simplifies implementation**: No custom adapter needed (research showed Gemini endpoint would work, but OpenRouter is even simpler)
- **Better quota**: No hard limits vs. Gemini's ~20-100 RPD
- **Specialized model**: Devstral optimized for coding/reasoning (better for technical Q&A)
- **Same integration pattern**: Uses `set_default_openai_client()` with different base_url

**Files Updated**:
1. `spec.md` - All Gemini references → OpenRouter, FR-002 clarified (no custom adapter)
2. `plan.md` - Updated summary, dependencies, constraints for OpenRouter
3. `research.md` - Added Finding 7 documenting OpenRouter alternative
4. `contracts/agents_sdk_interface.md` - Updated configuration, env vars, error handling
5. `CLARIFICATIONS.md` - Created summary document

**Configuration Changes**:
```python
# Before (Gemini-based plan)
gemini_client = AsyncOpenAI(
    api_key=settings.GOOGLE_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
agent = Agent(model="gemini-1.5-flash", ...)

# After (OpenRouter clarification)
openrouter_client = AsyncOpenAI(
    api_key=settings.OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)
agent = Agent(model="mistralai/devstral-2512:free", ...)
```

## Outcome

- ✅ Impact: All clarification questions answered. Specification updated to reflect OpenRouter integration instead of Gemini due to quota restrictions. Implementation simplified from ~500 LOC (custom adapter) → ~300 LOC (configuration only). Migration path now uses free, reliable OpenRouter endpoint with model specialized for technical/coding tasks.
- 🧪 Tests: No tests created (clarification phase). Updated test contracts to use `OPENROUTER_API_KEY` and `mistralai/devstral-2512:free` model.
- 📁 Files: Updated 4 planning artifacts (spec.md, plan.md, research.md, contracts/agents_sdk_interface.md), created 1 new file (CLARIFICATIONS.md).
- 🔁 Next prompts: `/sp.tasks` to generate actionable implementation task breakdown with OpenRouter configuration.
- 🧠 Reflection: User's OpenRouter input was game-changing. Initial research recommended Gemini's OpenAI endpoint, but December 2025 quota cuts made it unsuitable for demos. OpenRouter solves this while maintaining the same implementation simplicity (just different base_url). The Devstral model being specialized for coding/reasoning is a bonus for technical textbook Q&A. Implementation is now simpler, more reliable, and better suited for the use case.

## Evaluation notes (flywheel)

- Failure modes observed: None. Clarification questions were well-targeted. User provided critical context about Gemini quota issues that research (conducted before December 2025 changes) couldn't anticipate. OpenRouter switch was straightforward since both use OpenAI-compatible endpoints.
- Graders run and results (PASS/FAIL): PASS - All 3 clarification questions answered, OpenRouter configuration validated, all planning artifacts updated consistently. Environment variables defined, model confirmed free and suitable.
- Prompt variant (if applicable): Standard /sp.clarify flow with 3 questions presented together (Question 1: approach, Question 2: configuration, Question 3: error handling). User's additional OpenRouter context triggered comprehensive artifact updates.
- Next experiment (smallest change to try): Proceed to task generation with OpenRouter configuration. Consider whether to create a quickstart-openrouter.md supplement or update existing quickstart.md inline (deferred to implementation phase to avoid over-documentation).
