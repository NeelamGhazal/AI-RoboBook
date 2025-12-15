<!--
SYNC IMPACT REPORT - 2025-12-13

Version Change: TEMPLATE → 1.0.0 (MAJOR - Initial constitution ratification)

Principles Defined:
- Educational Excellence
- AI-Native Architecture
- Technical Rigor
- Accessibility & Inclusivity
- Claude Code Integration
- Content Structure Standards
- Hardware & Software Coverage

Sections Added:
- Core Principles (7 principles)
- Technical Implementation Standards
- Content Quality Standards
- Constraints & Boundaries
- Governance

Templates Requiring Updates:
✅ plan-template.md - Constitution Check section will reference these principles
✅ spec-template.md - User stories must align with educational excellence
✅ tasks-template.md - Tasks will reference content structure and technical standards

Follow-up Actions:
- None - All placeholders filled
- Constitution ready for use in /sp.plan, /sp.specify, and /sp.tasks workflows

Rationale for MAJOR (1.0.0):
- Initial comprehensive constitution for hackathon project
- Establishes foundational governance for AI-Native Textbook development
- Defines non-negotiable standards for educational content and technical implementation
-->

# Physical AI & Humanoid Robotics Textbook Constitution

## Core Principles

### I. Educational Excellence

**MUST ensure pedagogically sound, technically accurate content that bridges theory with practice.**

- Content MUST be technically accurate and verified against official documentation (ROS 2, NVIDIA Isaac, Gazebo, Unity)
- Each chapter MUST include: learning objectives, practical examples, code snippets, hands-on exercises, assessment questions
- Progressive learning curve MUST be maintained from fundamentals to advanced concepts
- Real-world applicability MUST be demonstrated for humanoid robotics and embodied AI scenarios
- All hardware specifications MUST match current market availability (as of Nov 2025)
- All software versions MUST be specified and verified (Ubuntu 22.04 LTS, ROS 2 Humble/Iron)

**Rationale**: Educational content that lacks technical accuracy or pedagogical structure fails students and undermines the mission to prepare the next generation of roboticists.

### II. AI-Native Architecture

**MUST deliver seamless RAG chatbot integration for intelligent, context-aware learning experiences.**

- RAG chatbot MUST use OpenAI Agents/ChatKit SDKs with FastAPI backend
- Vector store MUST use Qdrant Cloud (Free Tier) with Neon Serverless Postgres
- Chatbot MUST support:
  - General Q&A about book content with <3 seconds response time
  - Selected text queries (user highlights text → asks question)
  - Context-aware follow-up questions
  - Source citation with chapter/section references
- Book content MUST serve as the knowledge base for RAG system
- Chatbot responses MUST be accurate and cite specific sections

**Rationale**: An AI-native textbook is not just content plus a chatbot—it's an intelligent learning companion that understands robotics concepts and adapts to each learner's needs.

### III. Technical Rigor (NON-NEGOTIABLE)

**ALL code examples MUST be tested, reproducible, and follow established conventions.**

- Python code MUST follow PEP 8 style guide
- ROS 2 code MUST follow official ROS conventions
- Every code example MUST include:
  - requirements.txt or package.xml
  - Setup instructions
  - Testing verification on Ubuntu 22.04 LTS
- Complex logic MUST have inline comments
- Each major example MUST have a README
- Hardware setups MUST include troubleshooting sections
- All external links MUST be functional
- NO code examples may be theoretical—all MUST be executable

**Rationale**: Students learn by doing. Code that doesn't run or lacks setup instructions wastes precious learning time and breeds frustration.

### IV. Accessibility & Inclusivity

**Content MUST be accessible to learners with varying backgrounds and available in multiple formats.**

- Explanations MUST be clear for learners with different experience levels
- Bilingual support (English/Urdu) MUST be accurate (not machine-translated gibberish)
- Responsive design MUST work on desktop, tablet, and mobile devices
- Progressive disclosure MUST be used for complex topics
- Dark/light mode support MUST be implemented
- Authentication system (if implemented) MUST collect user background to enable personalization:
  - Software background (AI/ML experience level)
  - Hardware background (robotics/electronics experience)
  - Prior ROS 2 knowledge
  - Programming proficiency (Python, C++)

**Rationale**: Robotics education should not be limited by language barriers, device constraints, or assumed prerequisites. Accessibility broadens reach and impact.

### V. Claude Code Integration

**ALL content generation and project management MUST use Claude Code with Spec-Kit Plus.**

- Book content MUST be generated/managed via Claude Code
- Spec-Kit Plus MUST be used for project structure and specifications
- Reusable Subagents MUST be created for repetitive tasks (bonus feature)
- Agent Skills MUST be demonstrated for domain-specific operations (bonus feature)
- Every user interaction MUST generate a Prompt History Record (PHR) under `history/prompts/`:
  - Constitution updates → `history/prompts/constitution/`
  - Feature-specific work → `history/prompts/<feature-name>/`
  - General operations → `history/prompts/general/`
- Architectural decisions MUST be surfaced for ADR documentation when significant

**Rationale**: This project demonstrates the power of AI-assisted development. Claude Code is not just a tool—it's a core part of the development philosophy and competitive differentiator.

### VI. Content Structure Standards

**Module organization MUST deliver 18-22 comprehensive chapters across 4 core modules.**

- Module 1 (ROS 2 - Weeks 3-5): 4-5 chapters covering:
  1. ROS 2 Architecture fundamentals
  2. Nodes, Topics, and Services
  3. Building ROS 2 Packages with Python
  4. Launch Files and Parameter Management
  5. URDF for Humanoid Robots (optional 5th)

- Module 2 (Gazebo & Unity - Weeks 6-7): 4-5 chapters covering:
  1. Gazebo Simulation Environment Setup
  2. Robot Description Formats (URDF/SDF)
  3. Physics and Sensor Simulation
  4. Unity for Robot Visualization
  5. Integrating Gazebo with ROS 2 (optional 5th)

- Module 3 (NVIDIA Isaac - Weeks 8-10): 4-5 chapters covering:
  1. NVIDIA Isaac SDK and Isaac Sim
  2. AI-Powered Perception
  3. Reinforcement Learning for Robot Control
  4. Sim-to-Real Transfer Techniques
  5. Hardware-Accelerated VSLAM (optional 5th)

- Module 4 (VLA - Weeks 11-13): 4-5 chapters covering:
  1. Voice-to-Action with OpenAI Whisper
  2. LLMs for Cognitive Planning
  3. Multi-Modal Interaction Design
  4. Capstone Project: Autonomous Humanoid
  5. Debugging and Deployment (optional 5th)

- Additional: Introduction to Physical AI (Weeks 1-2): 2-3 chapters

- Each chapter MUST:
  - Have clear learning objectives
  - Take 15-25 minutes to read
  - Include practical examples and code snippets
  - Provide hands-on exercises or lab activities
  - End with assessment questions
  - Reference hardware requirements where applicable

**Rationale**: A structured curriculum with clear learning objectives ensures comprehensive coverage and measurable progress. The 4-5 chapter range per module provides depth without overwhelming learners.

### VII. Hardware & Software Coverage

**MUST provide accurate, current, and complete hardware/software specifications.**

Hardware Coverage MUST Include:

1. **Workstation Requirements**:
   - GPU: NVIDIA RTX 4070 Ti minimum (12GB VRAM), RTX 4090 recommended (24GB VRAM)
   - CPU: Intel i7 13th Gen+ or AMD Ryzen 9
   - RAM: 64GB DDR5 (32GB minimum)
   - OS: Ubuntu 22.04 LTS

2. **Edge Computing Kit**:
   - NVIDIA Jetson Orin Nano (8GB) or Orin NX (16GB)
   - Intel RealSense D435i or D455
   - USB IMU (BNO055) if needed
   - ReSpeaker USB Mic Array

3. **Robot Hardware Options**:
   - Budget: Unitree Go2 Edu ($1,800-$3,000)
   - Mid-range: Unitree G1 ($16,000)
   - Premium: Full humanoid platforms
   - Alternative: Hiwonder TonyPi Pro ($600)

4. **Cloud Alternative**:
   - AWS g5.2xlarge or g6e.xlarge instances
   - Cost breakdown per quarter
   - Sim-to-real transfer workflow

Software Stack Coverage MUST Include:
- ROS 2 (Humble/Iron) architecture
- URDF/SDF robot description
- Gazebo physics simulation
- Unity for visualization
- NVIDIA Isaac Sim workflow
- Isaac ROS perception
- Nav2 path planning
- OpenAI Whisper integration
- LLM-to-action pipelines

**Rationale**: Students need clear, accurate hardware requirements and costs to make informed decisions. Outdated or vague specifications create barriers to entry and frustrate learners.

## Technical Implementation Standards

### Book Platform (Docusaurus)

- MUST use Docusaurus (latest stable version)
- MUST implement responsive design for desktop, tablet, mobile
- MUST support dark/light mode
- MUST integrate search functionality
- MUST provide sidebar + breadcrumb navigation
- MUST load in <5 seconds on standard broadband
- MUST support Chrome, Firefox, Safari (latest 2 versions)

### RAG Chatbot Requirements

- MUST build with OpenAI Agents/ChatKit SDKs
- MUST use FastAPI backend
- MUST use Neon Serverless Postgres database
- MUST use Qdrant Cloud (Free Tier) vector store
- MUST implement:
  - General Q&A about book content
  - Selected text queries (highlight → ask)
  - Context-aware follow-up questions
  - Source citation (chapter/section references)
- MUST respond in <3 seconds for typical queries

### Authentication System (BONUS)

- SHOULD implement using Better-Auth (https://www.better-auth.com/)
- Signup flow SHOULD collect:
  - Software background (AI/ML experience level)
  - Hardware background (robotics/electronics experience)
  - Prior ROS 2 knowledge
  - Programming proficiency (Python, C++)
- User profiles MUST be stored securely
- Session management MUST support personalized content

### Deployment

- MUST deploy to GitHub Pages or Vercel
- MUST use public GitHub repository
- MUST NOT expose API keys or credentials in repo
- MUST provide environment variables template
- MUST document database migrations/schema

## Content Quality Standards

### Minimum Requirements

- **Chapter Count**: Minimum 18 chapters, recommended 20-22 chapters
- **Code Examples**: Minimum 20 working examples across all modules
- **Diagrams/Visuals**: Minimum 30 technical diagrams/illustrations
- **Assessment Items**: Minimum 4 assessment/project descriptions
- **External Resources**: Properly cited and hyperlinked

### Technical Accuracy Checklist

Before content is considered complete, it MUST pass:

- [ ] ROS 2 commands and APIs verified against official documentation
- [ ] NVIDIA Isaac versions and requirements up-to-date
- [ ] Gazebo/Unity integration steps tested
- [ ] Hardware specifications match current market availability
- [ ] Price estimates for hardware updated (as of Nov 2025)
- [ ] All external links functional

### Bonus Features (Additional Points)

**Subagents & Agent Skills (50 points)**:
- [ ] Created reusable Subagents for content generation
- [ ] Demonstrated Agent Skills for domain operations
- [ ] Documented reusability and efficiency gains

**Authentication & User Profiling (50 points)**:
- [ ] Better-Auth signup/signin implemented
- [ ] User background questions integrated
- [ ] Profile data stored securely
- [ ] Personalization hooks in place

**Content Personalization (50 points)**:
- [ ] Button at chapter start for personalization
- [ ] Content adapts to beginner/intermediate/advanced
- [ ] Uses stored user background effectively
- [ ] Smooth UX for toggling personalization

**Urdu Translation (50 points)**:
- [ ] Translation button at chapter start
- [ ] High-quality Urdu technical translation
- [ ] Maintains formatting and code blocks
- [ ] Bidirectional text rendering correct

## Constraints & Boundaries

### Non-Negotiable Constraints

- **Submission Deadline**: Sunday, November 30, 2025 at 6:00 PM PKT (HARD CUTOFF)
- **Demo Video**: Maximum 90 seconds
- **Browser Support**: Chrome, Firefox, Safari (latest 2 versions only)
- **Response Time**: Chatbot <3 seconds for typical queries
- **Load Time**: Book <5 seconds on standard broadband

### In Scope

- 4 core modules (ROS 2, Gazebo/Unity, NVIDIA Isaac, VLA)
- Introduction to Physical AI (Weeks 1-2)
- RAG chatbot with selected text queries
- Docusaurus-based textbook
- Public GitHub repository
- Deployment to GitHub Pages or Vercel
- Bonus features (optional): Authentication, Personalization, Translation, Subagents/Skills

### Out of Scope

- Live instructor interactions
- Video tutorials (beyond 90-second demo)
- Mobile native apps
- Offline-first functionality
- Real-time collaborative editing
- Automated grading systems
- LMS integration

### Security & Privacy

- NO API keys or credentials in public repository
- User data MUST be stored securely if authentication implemented
- MUST provide .env.example for environment variables
- MUST use HTTPS for deployment
- MUST sanitize user inputs to chatbot

## Governance

### Amendment Procedure

1. Proposed changes MUST be discussed with rationale
2. Impact on existing templates, specs, plans, and tasks MUST be assessed
3. Version number MUST be incremented according to semantic versioning:
   - **MAJOR**: Backward-incompatible governance/principle changes
   - **MINOR**: New principles or materially expanded guidance
   - **PATCH**: Clarifications, wording, typos, non-semantic refinements
4. Sync Impact Report MUST be generated and prepended as HTML comment
5. All dependent templates MUST be updated to reflect changes
6. LAST_AMENDED_DATE MUST be updated to amendment date

### Compliance & Verification

- All planning workflows (`/sp.plan`) MUST include Constitution Check gate
- All specifications (`/sp.specify`) MUST verify alignment with educational excellence standards
- All tasks (`/sp.tasks`) MUST reference applicable principles
- Complexity that violates simplicity principles MUST be justified in plan.md Complexity Tracking table
- Constitution supersedes all other guidance documents

### Versioning Policy

- Constitution version MUST be tracked in this file
- Changes MUST be documented in Sync Impact Report
- Breaking changes MUST increment MAJOR version
- New principles or sections MUST increment MINOR version
- Clarifications and fixes MUST increment PATCH version

### Conflict Resolution

- When guidance conflicts, constitution principles take precedence
- When principles conflict, prioritize in order:
  1. Educational Excellence (student learning outcomes)
  2. Technical Rigor (quality and reproducibility)
  3. AI-Native Architecture (intelligent learning)
  4. Accessibility & Inclusivity (broad reach)
  5. Other principles as applicable

### Living Document Philosophy

This constitution is a living document that evolves with the project. However, core principles (Educational Excellence, Technical Rigor, AI-Native Architecture) are foundational and should rarely change. Evolution should add depth and clarity, not compromise core values.

---

**Version**: 1.0.0 | **Ratified**: 2025-12-13 | **Last Amended**: 2025-12-13
