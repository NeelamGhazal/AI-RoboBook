# 🤖 PhyAI Humanoid Textbook

> **AI-Powered Interactive Learning Platform for Humanoid Robotics**
> Built with Docusaurus, FastAPI, and OpenRouter LLM - Educational Content Creation with Embedded RAG Chatbot

[![Docusaurus](https://img.shields.io/badge/Docusaurus-3.6-3ECC5F?logo=docusaurus&logoColor=white)](https://docusaurus.io/)
[![Vercel](https://img.shields.io/badge/Vercel-Production-000000?logo=vercel&logoColor=white)](https://vercel.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Qdrant](https://img.shields.io/badge/Qdrant-1.16-DC244C?logo=qdrant&logoColor=white)](https://qdrant.tech/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql&logoColor=white)](https://postgresql.org/)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-LLM-7C3AED?logo=openai&logoColor=white)](https://openrouter.ai/)

---

## 📚 Overview

**PhyAI Humanoid Textbook** is a dual-purpose educational platform that combines:

1. **AI-Driven Educational Content Creation**: A Docusaurus-based technical textbook for humanoid robotics, created using Spec-Kit Plus and Claude Code workflow for systematic content development
2. **Embedded RAG Chatbot**: An intelligent Q&A system with streaming responses, citations, and context-aware explanations integrated directly into the learning experience

### 📖 Textbook Modules

The platform covers four comprehensive modules on humanoid robotics:

- **Module 1: ROS 2 Fundamentals** - Architecture, nodes, topics, services, and actions
- **Module 2: Robot Simulation** - Gazebo, physics engines, sensor modeling
- **Module 3: NVIDIA Isaac** - Isaac Sim, Isaac Gym, reinforcement learning
- **Module 4: Voice Control** - Speech recognition, NLP, voice commands for robots

### 🎯 Key Features

✅ **Streaming Chat Responses** - Real-time token-by-token generation like ChatGPT
✅ **Selected Text Q&A** - Highlight text → Click "Ask about this" → Get explanations
✅ **Citation Support** - Every answer includes source references with confidence scores
✅ **Session Persistence** - Conversation history saved across page reloads
✅ **100% Free Embeddings** - Local sentence-transformers (no API costs)
✅ **Free LLM Tier** - OpenRouter with mistralai/devstral-2512:free
✅ **Docusaurus MDX** - Rich interactive documentation with React components
✅ **Spec-Kit Plus Workflow** - AI-driven content specification and creation
✅ **Production Ready** - PostgreSQL, Qdrant Cloud, structured logging, Prometheus metrics

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│              FRONTEND (Docusaurus Site - Vercel)                │
│  • Educational Content (docs/ folder with 4 modules)            │
│  • MDX Support (Markdown + React Components)                    │
│  • Embedded Chat Widget (streaming SSE)                         │
│  • Selected Text Detection                                      │
│  • Citation Display                                             │
│  • Session Management                                           │
└────────────────┬────────────────────────────────────────────────┘
                 │ HTTP/SSE
┌────────────────▼────────────────────────────────────────────────┐
│         BACKEND (FastAPI - HuggingFace Spaces)                  │
│  • REST API Endpoints                                           │
│  • RAG Pipeline Orchestration                                   │
│  • Server-Sent Events Streaming                                 │
│  • Session & Message CRUD                                       │
└─┬──────────┬──────────┬──────────────┬───────────────────────────┘
  │          │          │              │
  │ Neon     │  Qdrant  │  OpenRouter  │  Sentence
  │ Postgres │  Cloud   │  (LiteLLM)   │  Transformers
  │          │          │              │  (Local)
  │          │          │              │
  └──────────┴──────────┴──────────────┴───────────────────────────┘
```

### RAG Data Flow

```
User Question (from embedded chat widget)
    ↓
Local Embeddings (sentence-transformers, FREE)
    ↓
Vector Search (Qdrant Cloud, 913 textbook chunks)
    ↓
Context Building (with conversation history)
    ↓
LLM Generation (OpenAI Agents SDK → LiteLLM → OpenRouter)
    ↓
Streaming Response (Server-Sent Events)
    ↓
Citations + Metadata
```

---

## 🛠️ Technology Stack

### Frontend (Docusaurus Site)

| Technology | Version | Purpose |
|------------|---------|---------|
| **Docusaurus** | 3.6 | Static site generator for educational content |
| **Vercel** | Latest | Production hosting with CDN |
| **MDX** | 3.1 | Markdown with React components |
| **TypeScript** | 5.0 | Type-safe development |
| **Tailwind CSS** | 3.4 | Utility-first styling for chat widget |
| **React 18.3** | 18.3 | UI components and chat widget |

### Backend (FastAPI Server)

| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | 0.115 | Async Python web framework |
| **Neon PostgreSQL** | asyncpg 0.29 | Serverless session & message storage |
| **Qdrant Cloud** | 1.16 | Vector database (913 chunks) |
| **Sentence-Transformers** | 3.0.1 | **Local embeddings (100% free!)** |
| **OpenAI Agents SDK** | 0.6.0 | LLM orchestration and streaming |
| **LiteLLM** | 1.80.11 | **OpenRouter integration** |
| **Structlog** | 24.4.0 | Structured JSON logging |
| **Prometheus** | 0.17.0 | Metrics & monitoring |

### Development Tools

| Tool | Purpose |
|------|---------|
| **Spec-Kit Plus** | AI-driven content specification workflow |
| **Claude Code** | Automated development and content creation |
| **Git** | Version control and branch-based development |

---

## 🚀 Quick Start

### Prerequisites

- **Node.js 18+** and npm
- **Python 3.11+**
- **Neon PostgreSQL** account (serverless, free tier available)
- **Qdrant Cloud** account (free tier available)
- **OpenRouter API key** (free tier available)

### 1. Clone Repository

```bash
git clone <repository-url>
cd phyai-humanoid-textbook
```

### 2. Backend Setup (FastAPI)

```bash
cd backend/rag-chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
# Neon Serverless PostgreSQL
NEON_DATABASE_URL=postgresql://user:pass@endpoint.neon.tech/dbname?sslmode=require

# Qdrant Cloud
QDRANT_URL=https://your-cluster.cloud.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-api-key
QDRANT_COLLECTION_NAME=textbook_chunks

# OpenRouter LLM (Free Tier)
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=mistralai/devstral-2512:free
BASE_URL=https://openrouter.ai/api/v1

# CORS (include your Vercel production URL)
CORS_ORIGINS=http://localhost:3000,https://your-site.vercel.app
EOF

# Start backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Backend runs on:** http://localhost:8000
**API docs:** http://localhost:8000/docs

### 3. Frontend Setup (Docusaurus)

```bash
cd frontend

# Install dependencies
npm install

# Start Docusaurus development server
npm start
```

**Frontend runs on:** http://localhost:3000

**Docusaurus Site Structure:**
```
frontend/
├── docs/                      # Educational content
│   ├── module1-ros2/          # ROS 2 Fundamentals
│   ├── module2-simulation/    # Robot Simulation
│   ├── module3-isaac/         # NVIDIA Isaac
│   └── module4-voice/         # Voice Control
├── src/
│   ├── components/ChatWidget/ # Embedded RAG chatbot
│   ├── pages/                 # Custom pages
│   └── theme/
│       └── Root.tsx           # Chat widget injection point
├── docusaurus.config.js       # Site configuration
└── sidebars.js                # Navigation structure
```

### 4. Deploy to Production

**Frontend (Vercel):**
```bash
cd frontend
npm run build              # Build Docusaurus site
vercel --prod              # Deploy to Vercel
```

**Backend (HuggingFace Spaces):**
```bash
cd backend/rag-chatbot
# Follow HUGGINGFACE_DEPLOYMENT.md for detailed instructions
# Push to HF Spaces repository with Dockerfile
```

### 5. Verify Setup

**Backend Health:**
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "dependencies": {...}}
```

**Test Chat API:**
```bash
curl -X POST "http://localhost:8000/api/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "question": "What is ROS 2?"}'
# Expected: Streaming SSE response with answer
```

**Frontend (Docusaurus Site):**
1. Open http://localhost:3000
2. Navigate to any module documentation
3. Click chat icon (bottom right)
4. Ask: "What is ROS 2?"
5. Should see streaming response with citations

---

## 📖 Usage Examples

### General Query

**User:** "What is ROS 2?"

**Response:**
```
ROS 2 (Robot Operating System 2) is a next-generation robotics
framework designed for production robotics applications. It is not
an operating system but a collection of libraries, tools, and
conventions that facilitate robotics development...

📚 Sources:
• Module1 - Chapter 1: ROS 2 Architecture (confidence: 0.71)
• Module3 - Chapter 1: Isaac Sim Introduction (confidence: 0.62)
```

### Selected Text Q&A

1. **Select text** from the Docusaurus textbook (50-500 characters)
2. **"Ask about this" button** appears above selection
3. **Click button** → Chat opens with context loaded
4. **Ask:** "explain this" or "what does this mean?"
5. **Get response** focused on the selected text

**Example:**

**Selected:** "ROS 2 is built from the ground up to address real-world robotics challenges including security, determinism, and multi-robot systems."

**Question:** "explain this"

**Response:**
```
This text describes the fundamental design principles of ROS 2:

1. Security: Built-in authentication and encryption
2. Determinism: Predictable real-time behavior
3. Multi-robot systems: Native support for robot fleets

[Detailed explanation based on selected text...]

📚 Sources:
• Selected Text (confidence: 1.00)
• Module1 - Related content (confidence: 0.68)
```

---

## 🎯 Key Features Explained

### 1. Streaming Responses

- **Technology:** Server-Sent Events (SSE)
- **Format:** `data: {"type": "token", "content": "word"}`
- **Experience:** ChatGPT-style progressive text display
- **Latency:** ~1-2 seconds to first token

### 2. Selected Text Mode

- **Detection:** `window.getSelection()` API
- **Validation:** 50-500 character range
- **Context:** Selected text becomes primary source
- **Confidence:** 1.0 (highest) for user-selected content

### 3. Citation System

Every response includes:
- **Source chunk** (chapter, section, URL)
- **Confidence score** (0.0-1.0)
- **Text snippet** (first 100 chars)
- **Traceability** back to original content

### 4. Session Persistence

- **Storage:** Neon Serverless PostgreSQL database
- **Recovery:** Auto-recovery on backend restart
- **History:** Last 12 messages included in context
- **Stateless:** Frontend can resume any session by ID

---

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```bash
# Neon Serverless PostgreSQL
NEON_DATABASE_URL=postgresql://user:pass@endpoint.neon.tech/dbname?sslmode=require

# Qdrant Cloud
QDRANT_URL=https://xxx.cloud.qdrant.io:6333
QDRANT_API_KEY=your-key
QDRANT_COLLECTION_NAME=textbook_chunks

# OpenRouter LLM
OPENROUTER_API_KEY=sk-or-v1-xxx
OPENROUTER_MODEL=mistralai/devstral-2512:free
BASE_URL=https://openrouter.ai/api/v1

# CORS (include Vercel production URL)
CORS_ORIGINS=http://localhost:3000,https://your-site.vercel.app
```

**Frontend (Docusaurus):**
- **Chat widget API URL** is configured in `src/components/ChatWidget/config.ts`
- **Production URL** is set to HuggingFace Spaces backend by default
- **Local development** can override by setting `window.CHAT_API_URL = 'http://localhost:8000'`

### Windows + WSL Setup

If running backend on WSL and frontend on Windows:

1. Get WSL IP: `ip addr show eth0 | grep inet`
2. Update `frontend/src/components/ChatWidget/config.ts`:
```typescript
return 'http://172.25.218.26:8000';  // Replace with your WSL IP
```

---

## 🧑‍💻 Development Workflow

### Spec-Kit Plus & Claude Code Integration

This project uses **Spec-Kit Plus** and **Claude Code** for systematic content development:

1. **Content Specification**: Create structured specs for each module using Spec-Kit Plus templates
2. **AI-Driven Creation**: Use Claude Code to generate educational content following specifications
3. **Iterative Refinement**: Review and refine content with AI assistance
4. **Quality Assurance**: Validate content accuracy and educational value
5. **Vector Ingestion**: Process finalized content into Qdrant for RAG retrieval

### Content Ingestion Pipeline

**Step 1: Write Content in Docusaurus**
```bash
# Add new educational content to docs/
docs/module1-ros2/chapter1-intro.md
```

**Step 2: Process Content for RAG**
```bash
cd backend/rag-chatbot
python scripts/ingest_book.py --input ../../frontend/docs --collection textbook_chunks
```

**Step 3: Verify Ingestion**
```bash
# Check Qdrant collection stats
python scripts/check_qdrant.py
# Expected: Shows chunk count, embeddings dimension
```

**Step 4: Test RAG Retrieval**
```bash
# Test query through API
curl -X POST "http://localhost:8000/api/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "question": "Your test question about new content"}'
```

---

## 📊 API Endpoints

### Chat

```
POST /api/v1/chat/stream      - Streaming chat (SSE)
POST /api/v1/chat             - Non-streaming chat
GET  /api/v1/chat/history/{id} - Get conversation history
GET  /api/v1/chat/health      - Chat service health
```

### Sessions

```
POST /api/v1/sessions          - Create new session
GET  /api/v1/sessions/{id}     - Get session details
```

### System

```
GET /health                    - System health check
GET /docs                      - Swagger UI
GET /metrics                   - Prometheus metrics
```

### Request Format

```json
{
  "session_id": "uuid-string",
  "question": "What is ROS 2?",
  "selected_text": "optional-context"
}
```

### Response Format (SSE)

```
data: {"type": "token", "content": "ROS "}
data: {"type": "token", "content": "2 "}
data: {"type": "citations", "citations": [{...}]}
data: {"type": "metadata", "metadata": {...}}
data: {"type": "done"}
```

---

## 📁 Project Structure

```
phyai-humanoid-textbook/
├── frontend/                          # Docusaurus Site
│   ├── docs/                          # Educational content (MDX)
│   │   ├── module1-ros2/              # ROS 2 Fundamentals
│   │   │   ├── chapter1-intro.md
│   │   │   ├── chapter2-nodes.md
│   │   │   └── ...
│   │   ├── module2-simulation/        # Robot Simulation
│   │   ├── module3-isaac/             # NVIDIA Isaac
│   │   └── module4-voice/             # Voice Control
│   ├── src/
│   │   ├── components/
│   │   │   └── ChatWidget/            # Embedded RAG chatbot
│   │   │       ├── ChatWidget.tsx
│   │   │       ├── components/
│   │   │       ├── hooks/
│   │   │       ├── api/
│   │   │       ├── config.ts
│   │   │       └── types.ts
│   │   ├── pages/
│   │   └── theme/
│   │       └── Root.tsx               # Chat widget injection
│   ├── docusaurus.config.js           # Site configuration
│   ├── sidebars.js                    # Navigation structure
│   ├── vercel.json                    # Vercel deployment config
│   └── package.json
│
├── backend/rag-chatbot/               # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── chat.py
│   │   │   └── sessions.py
│   │   ├── services/
│   │   │   ├── rag.py
│   │   │   ├── vector_search.py
│   │   │   ├── llm.py
│   │   │   └── citation_builder.py
│   │   ├── clients/
│   │   │   ├── db_client.py
│   │   │   ├── qdrant_client.py
│   │   │   └── local_embedding_client.py
│   │   ├── db/
│   │   │   └── crud.py
│   │   ├── config.py
│   │   └── main.py
│   ├── scripts/
│   │   ├── ingest_book.py             # Content ingestion pipeline
│   │   └── init_qdrant.py
│   ├── Dockerfile                     # HF Spaces deployment
│   ├── requirements.txt
│   └── HUGGINGFACE_DEPLOYMENT.md
│
├── .specify/                          # Spec-Kit Plus templates
│   └── memory/constitution.md
│
└── README.md
```

---

## 🌐 Live Deployments

| Component | Platform | URL | Test Instructions |
|-----------|----------|-----|-------------------|
| **Frontend (Docusaurus)** | Vercel | `https://phyai-humanoid-textbook.vercel.app` | 1. Open URL<br>2. Navigate to any module<br>3. Click chat icon (bottom right) |
| **Backend (FastAPI)** | HuggingFace Spaces | `https://neelumghazal-phyai-rag-chatbot-backend.hf.space` | 1. Open `/docs` endpoint<br>2. Test `/health` endpoint<br>3. Try POST to `/api/v1/chat/stream` |

**End-to-End Test:**
1. Visit Vercel frontend
2. Select text from any module (50+ characters)
3. Click "Ask about this" button
4. Ask a question in the chat
5. Verify streaming response with citations

---

## 🚧 Roadmap

### ✅ Completed

- [x] Docusaurus-based educational content platform
- [x] RAG chatbot with streaming responses
- [x] Selected text Q&A feature
- [x] Citation system with confidence scores
- [x] Session persistence with Neon PostgreSQL
- [x] Windows + WSL support
- [x] Free embeddings (local sentence-transformers)
- [x] Free LLM tier (OpenRouter)
- [x] Production logging & metrics
- [x] Vercel deployment for frontend
- [x] HuggingFace Spaces deployment for backend
- [x] Spec-Kit Plus integration for content workflow

### 🔜 Coming Soon

- [ ] Multi-language support (ES, ZH, JA)
- [ ] Voice input/output (Web Speech API)
- [ ] Mobile-responsive chat widget
- [ ] Export conversation history
- [ ] Advanced search (semantic + keyword)
- [ ] Quiz generation from content
- [ ] Progress tracking dashboard
- [ ] Interactive code examples with live execution

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests (if applicable)
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Code Style

**Python:** PEP 8, type hints, docstrings
**TypeScript:** ESLint + Prettier, functional components
**MDX:** Clear headings, consistent formatting, educational tone

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 🙏 Acknowledgments

Built with amazing open-source technologies:

- **Docusaurus** - Modern static site generator for documentation
- **Vercel** - Seamless deployment and hosting platform
- **MDX** - Markdown with React components
- **React** - UI framework for interactive components
- **FastAPI** - High-performance Python web framework
- **Qdrant** - Vector database for semantic search
- **Sentence Transformers** - Local embedding models
- **OpenAI Agents SDK** - LLM orchestration and streaming
- **LiteLLM** - Multi-provider LLM proxy
- **Neon** - Serverless PostgreSQL database
- **Tailwind CSS** - Utility-first styling framework
- **Spec-Kit Plus** - AI-driven content specification workflow
- **Claude Code** - Automated development and content creation

---

## 📞 Support

- **Deployment Guides:**
  - Frontend: See `frontend/VERCEL_DEPLOYMENT.md`
  - Backend: See `backend/rag-chatbot/HUGGINGFACE_DEPLOYMENT.md`
- **Architecture:** See `backend/rag-chatbot/HF_DEPLOYMENT_ARCHITECTURE.md`
- **Backend Details:** See `backend/rag-chatbot/BACKEND_ARCHITECTURE_REPORT.md`
- **Issues:** Open a GitHub issue with detailed info
- **Questions:** Check existing issues or create a new one

---

## 🏆 Project Highlights

### Dual Objectives Achieved

**1. AI-Driven Educational Content Creation**
- ✅ Systematic content specification using Spec-Kit Plus workflow
- ✅ Claude Code integration for AI-assisted content development
- ✅ Docusaurus platform for rich, interactive documentation
- ✅ MDX support for combining Markdown with React components
- ✅ Modular structure for scalable educational content

**2. Embedded RAG Chatbot System**
- ✅ **100% Free Embeddings** - No API costs for retrieval (sentence-transformers)
- ✅ **Free LLM Tier** - mistralai/devstral-2512:free via OpenRouter
- ✅ **Production Infrastructure** - Neon PostgreSQL + Qdrant Cloud
- ✅ **Professional Development** - Structured logging, metrics, health checks
- ✅ **Seamless Integration** - Chat widget embedded in every documentation page

### Technical Excellence

- 🚀 **Modern Stack**: Docusaurus 3.6, FastAPI 0.115, OpenAI Agents SDK 0.6
- 🌐 **Cloud-Native**: Vercel (frontend) + HuggingFace Spaces (backend)
- 💰 **Cost-Optimized**: Local embeddings + free LLM tier = minimal operational costs
- 📊 **Well-Documented**: Comprehensive guides for deployment and architecture
- 🔒 **Production-Ready**: Security headers, CORS, health checks, monitoring

---

<div align="center">

**Built for education, powered by open source, enhanced by AI** 🚀

*Making AI-powered learning accessible to everyone through systematic content creation and intelligent assistance*

</div>
