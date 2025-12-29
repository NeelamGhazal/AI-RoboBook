# Clarifications Summary: OpenAI Agents SDK Migration

**Date**: 2025-12-25
**Command**: `/sp.clarify`
**Status**: Complete

## User Clarification Responses

### Question 1: Implementation Approach
**User Choice**: **A** - Use OpenRouter's OpenAI endpoint with `set_default_openai_client` (Recommended)

**Rationale**: Simplest approach (3 lines of config), fastest (<100ms overhead), no custom code to maintain.

### Question 2: Configuration Strategy
**User Choice**: **A** - Keep as hardcoded constants (12 messages, 3 chunks)

**Rationale**: Simpler implementation, faster development, sufficient for hackathon demo.

### Question 3: Quota Error Handling
**User Choice**: **A** - Fail immediately with user-friendly error (no retries)

**Rationale**: Simple, clear failure mode, no hanging requests.

---

## Critical Update: OpenRouter vs. Gemini

**User provided additional context**: Due to Gemini free tier quota restrictions (reduced to ~20-100 RPD in December 2025), switching to **OpenRouter with Mistral Devstral** for better reliability.

###  OpenRouter Configuration

```env
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=mistralai/devstral-2512:free
BASE_URL=https://openrouter.ai/api/v1
```

### Code Implementation

```python
from openai import AsyncOpenAI
from agents import set_default_openai_client

openrouter_client = AsyncOpenAI(
    api_key=settings.OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)
set_default_openai_client(openrouter_client)

agent = Agent(
    name="TextbookRAGAgent",
    model="mistralai/devstral-2512:free",
    instructions=SYSTEM_PROMPT,
    tools=[]
)
```

### Why OpenRouter > Gemini

| Factor | Gemini Free (Dec 2025) | OpenRouter Devstral |
|--------|------------------------|---------------------|
| Daily Quota | ~20-100 requests | No hard limit |
| Model Specialization | General | Coding/reasoning |
| Reliability | Quota errors | Stable |
| Setup | OpenAI-compatible | OpenAI-compatible |
| Cost | Free | Free |

---

## Implementation Impact

**Original Plan** (Gemini-based):
- Custom LLM adapter class: ~300 LOC
- Gemini OpenAI endpoint: `https://generativelanguage.googleapis.com/v1beta/openai/`
- Environment: `GOOGLE_API_KEY`, `GEMINI_MODEL`

**Updated Plan** (OpenRouter-based):
- No custom adapter: just configuration (3 lines)
- OpenRouter endpoint: `https://openrouter.ai/api/v1`
- Environment: `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `BASE_URL`
- Model: `mistralai/devstral-2512:free` (specialized for agentic/coding tasks)

**Simplification**: ~300 LOC → ~50 LOC (configuration only, no adapter class)

---

## Files Updated

All planning artifacts updated to reflect OpenRouter:

1. ✅ `spec.md` - Updated FR-002, SC-003, all Gemini references → OpenRouter
2. ✅ `plan.md` - Updated summary, technical context, dependencies
3. ✅ `research.md` - Added Finding 7 (OpenRouter alternative)
4. ✅ `contracts/agents_sdk_interface.md` - Updated configuration contracts, env vars, logging
5. ⚠️ `quickstart.md` - Needs update (see quickstart-openrouter-diff.md for changes)

---

## Validation Checklist

- [x] All 3 clarification questions answered
- [x] OpenRouter configuration validated (user has API key ready)
- [x] Environment variables defined (OPENROUTER_API_KEY, OPENROUTER_MODEL, BASE_URL)
- [x] Model confirmed free and suitable (mistralai/devstral-2512:free)
- [x] Hardcoded limits confirmed (top 3 chunks, 12 message history)
- [x] Error handling strategy confirmed (fail fast, no retries)
- [x] Planning artifacts updated with clarifications

---

## Next Steps

**Ready for**: `/sp.tasks` to generate implementation task breakdown

**Expected tasks**:
1. Update `config.py` with OpenRouter env vars
2. Configure `AsyncOpenAI` client in `main.py` lifespan
3. Create `Agent` instance in `llm.py`
4. Refactor `generate_response_stream()` to use `Runner.run_stream()`
5. Switch routing from `chat_minimal` to `chat` in `main.py`
6. Add `openai-agents` to `requirements.txt`
7. Update tests to mock OpenRouter/Agents SDK
8. Manual testing with real OpenRouter API

---

## Key Decisions Summary

| Decision Point | Choice | Impact |
|----------------|--------|--------|
| LLM Provider | OpenRouter (Mistral Devstral) | Better quota, specialized model |
| Integration Method | `set_default_openai_client()` | Simplest, no custom adapter |
| Retrieval Limit | Top 3 chunks (hardcoded) | Simpler, faster development |
| History Limit | 12 messages (hardcoded) | Prevents context overflow |
| Error Handling | Fail fast (no retries) | Clear failure, no delays |
| Configuration | Environment variables | Standard practice |

---

**Specification Status**: ✅ Complete with clarifications
**Branch**: `001-openai-agents-migration`
**Ready for**: Task generation and implementation
