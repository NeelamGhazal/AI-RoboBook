---
id: 0001
title: Initial Constitution for PhyAI Textbook
stage: constitution
date: 2025-12-13
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: Developer
command: /sp.constitution
labels: ["constitution", "hackathon", "phyai-textbook", "initial-setup"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - null
---

## Prompt

```text
/sp.constitution
## Project: AI-Native Textbook for Physical AI & Humanoid Robotics Course

---

## Introduction

The future of AI is not confined to screens and servers—it's stepping into the physical world. This hackathon challenges you to create an AI-native textbook that teaches the next generation of roboticists and AI engineers how to build humanoid robots that can see, think, move, and interact naturally in human environments.

You are not just writing a book. You are building an **intelligent learning companion** that understands robotics, answers questions about ROS 2 and NVIDIA Isaac, and adapts to each student's background. This is where education meets embodied intelligence.

By participating in this hackathon, you're not only competing for recognition—you're auditioning to become a founding member of Panaversity's core team, potentially launching your journey as an AI startup founder in the education technology space.

---

## Project Overview

**Mission:** Create a comprehensive, interactive, AI-native textbook using Docusaurus with an embedded RAG chatbot for teaching Physical AI & Humanoid Robotics.

**Vision:** Bridge the gap between digital AI and physical robotics by providing an accessible, intelligent, and personalized learning experience that prepares students to work with humanoid robots in simulated and real-world environments.

**Deliverable:** A fully deployed textbook on GitHub Pages that includes:
- 4 comprehensive modules covering 13 weeks of coursework
- Each module containing 4-5 detailed chapters
- An embedded conversational AI chatbot powered by RAG
- Interactive features for personalization and multilingual support
- Complete technical documentation and reproducible setup

---

## Core Principles

### 1. Educational Excellence
- Content must be technically accurate and pedagogically sound
- Bridge theory with practical implementation
- Progressive learning curve from fundamentals to advanced concepts
- Real-world applicability for humanoid robotics and embodied AI

### 2. AI-Native Architecture
- Seamless integration of RAG chatbot for interactive learning
- Context-aware responses using book content as knowledge base
- Support for selected text queries (user highlights text, asks question)
- Intelligent personalization based on user background

### 3. Technical Rigor
- All code examples must be tested and reproducible
- Hardware specifications must be accurate and current
- Software versions must be specified and verified
- ROS 2, Gazebo, NVIDIA Isaac, and Unity implementations must be functional

### 4. Accessibility & Inclusivity
- Clear explanations for learners with varying backgrounds
- Bilingual support (English/Urdu) for broader accessibility
- Responsive design for multiple devices
- Progressive disclosure of complexity

[... full hackathon requirements including module structure, hardware coverage, constraints, success criteria, and timeline ...]

**Submission Deadline:** Sunday, November 30, 2025 at 6:00 PM PKT
```

## Response snapshot

Created comprehensive constitution v1.0.0 for AI-Native Textbook for Physical AI & Humanoid Robotics Course hackathon project.

**Seven Core Principles Established:**
1. Educational Excellence - Pedagogically sound, technically accurate content verified against official docs
2. AI-Native Architecture - RAG chatbot with OpenAI Agents/ChatKit, FastAPI, Qdrant, Neon Postgres
3. Technical Rigor (NON-NEGOTIABLE) - All code tested, reproducible, follows PEP 8 and ROS conventions
4. Accessibility & Inclusivity - Bilingual (English/Urdu), responsive design, personalization
5. Claude Code Integration - All content via Claude Code, PHR for every interaction, ADR suggestions
6. Content Structure Standards - 18-22 chapters across 4 modules (4-5 chapters each)
7. Hardware & Software Coverage - Accurate specs, pricing, cloud alternatives

**Technical Implementation Standards:**
- Docusaurus (latest stable), responsive, dark/light mode, <5s load time
- RAG chatbot <3s response time with source citations
- Better-Auth for optional authentication/personalization
- GitHub Pages/Vercel deployment

**Content Quality Standards:**
- Minimum 18 chapters, 20 code examples, 30 diagrams, 4 assessments
- Technical accuracy checklist for ROS 2, Isaac, Gazebo, Unity
- Bonus features: Subagents/Skills, Authentication, Personalization, Urdu Translation

**Governance:**
- Semantic versioning (MAJOR.MINOR.PATCH)
- Constitution Check in /sp.plan workflows
- Amendment procedure with Sync Impact Reports
- Conflict resolution prioritizes Educational Excellence > Technical Rigor > AI-Native Architecture

## Outcome

- ✅ Impact: Constitution v1.0.0 ratified, establishing foundational governance for hackathon project competing for Panaversity core team position
- 🧪 Tests: N/A (documentation artifact)
- 📁 Files: Created/updated .specify/memory/constitution.md with complete principles, standards, and governance
- 🔁 Next prompts: Ready for /sp.specify (feature specs), /sp.plan (module planning), /sp.tasks (content creation tasks)
- 🧠 Reflection: Constitution captures both base requirements (100 points) and bonus features (up to 200 points), enabling systematic development of educational content while maintaining competitive edge through Claude Code integration

## Evaluation notes (flywheel)

- Failure modes observed: None - all placeholders filled, version rationale clear, governance procedures defined
- Graders run and results (PASS/FAIL): PASS - No unresolved placeholders, dates ISO format, principles testable and declarative
- Prompt variant (if applicable): Standard /sp.constitution workflow with comprehensive hackathon requirements
- Next experiment (smallest change to try): Begin module specification with /sp.specify for "Introduction to Physical AI" (Weeks 1-2) to validate constitution principles against actual content creation workflow
