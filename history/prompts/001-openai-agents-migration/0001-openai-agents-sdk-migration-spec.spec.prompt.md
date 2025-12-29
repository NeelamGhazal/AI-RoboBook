---
id: 0001
title: OpenAI Agents SDK Migration Spec
stage: spec
date: 2025-12-24
surface: agent
model: claude-sonnet-4.5
feature: 001-openai-agents-migration
branch: 001-openai-agents-migration
user: system
command: /sp.specify
labels: ["hackathon", "openai-agents-sdk", "gemini", "rag-chatbot", "migration"]
links:
  spec: specs/001-openai-agents-migration/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-openai-agents-migration/spec.md
  - specs/001-openai-agents-migration/checklists/requirements.md
tests:
  - Specification quality validation (all items passed)
---

## Prompt

/sp.specify

Migrate hackathon chatbot backend to OpenAI Agents SDK with free LLM provider.

IMPORTANT CONSTRAINTS (MANDATORY):
- You MUST follow OpenAI Agents SDK patterns EXACTLY as documented here:
  https://openai.github.io/openai-agents-python/
- Do NOT use the legacy openai client library anywhere.
- Use ONLY openai.agents SDK classes, imports, and lifecycle.

Target audience:
Hackathon judges evaluating strict RAG + SDK compliance.

Technical goals:
- Replace Gemini direct client with OpenAI Agents SDK wrapper
- Gemini must be used ONLY as an underlying LLM via base_url override
- Gemini FREE API key must work through Agents SDK
- No OpenAI paid credits required

Architecture requirements:
- RAG pipeline must remain real and functional:
  Qdrant → retrieved context → Agents SDK → LLM → response
- All chatbot responses must be retrieval-augmented (NO mock/canned replies)
- chat.py endpoint (NOT chat_minimal.py) must be active in main.py
- Existing Qdrant + Neon DB setup must remain unchanged
- Frontend chatbot widget compatibility must remain unchanged
- Backend folder structure must remain unchanged

Explicitly forbidden:
- Using openai.OpenAI client
- Mock responses
- Switching to a different database
- Frontend changes
- Deployment changes

## Response snapshot

Created comprehensive feature specification for migrating RAG chatbot backend to OpenAI Agents SDK with Gemini as underlying LLM provider.

**Specification Structure:**
- 3 prioritized user stories (P1: Core RAG + Agents SDK, P2: Selected text context, P3: Chat history)
- 15 functional requirements covering SDK integration, RAG pipeline, streaming, persistence
- 8 success criteria (measurable, technology-agnostic)
- Edge cases, assumptions, dependencies, and risk mitigation table

**Key Decision (Clarified with User):**
- FR-002: Implement custom LLM adapter class conforming to Agents SDK interface but calling Gemini internally (User selected Option B)

**Files Created:**
1. specs/001-openai-agents-migration/spec.md (202 lines)
2. specs/001-openai-agents-migration/checklists/requirements.md (validation checklist)

**Validation Results:**
- All 13 checklist items passed
- No implementation details in spec
- All requirements testable and unambiguous
- Success criteria measurable and technology-agnostic
- 1 clarification marker resolved

**Branch:** 001-openai-agents-migration (created and checked out)

## Outcome

- ✅ Impact: Specification complete and validated. Defines clear migration path from direct Gemini integration to OpenAI Agents SDK with custom LLM adapter, maintaining all existing RAG functionality and frontend compatibility.
- 🧪 Tests: Specification quality validation completed - all 13 checklist items passed. No unit tests created (spec phase).
- 📁 Files: Created 2 files (spec.md, requirements.md checklist), modified 0 existing files.
- 🔁 Next prompts: `/sp.plan` to create implementation architecture, or `/sp.clarify` if additional business clarifications needed before technical planning.
- 🧠 Reflection: Successfully captured hackathon compliance requirements while preserving existing RAG infrastructure. Custom LLM adapter approach provides flexibility for Agents SDK integration without breaking existing Qdrant + Neon DB setup.

## Evaluation notes (flywheel)

- Failure modes observed: None. Specification followed template structure correctly. Single clarification marker was minimal and focused on critical integration pattern decision.
- Graders run and results (PASS/FAIL): PASS - All specification quality checklist items validated successfully (13/13 passed).
- Prompt variant (if applicable): Standard /sp.specify flow with single clarification question presented to user.
- Next experiment (smallest change to try): Proceed to planning phase to design the custom LLM adapter architecture and integration with existing RAG pipeline.
