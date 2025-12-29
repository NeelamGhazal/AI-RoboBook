# 🤖 PhyAI Humanoid Textbook

> **AI-Powered Interactive Learning Platform for Humanoid Robotics**
> Built with React, FastAPI, and OpenRouter LLM - Zero-Cost Embeddings, Production-Ready RAG

[![React](https://img.shields.io/badge/React-18.3-61dafb?logo=react&logoColor=white)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Qdrant](https://img.shields.io/badge/Qdrant-1.16-DC244C?logo=qdrant&logoColor=white)](https://qdrant.tech/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql&logoColor=white)](https.postgresql.org/)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-LLM-7C3AED?logo=openai&logoColor=white)](https://openrouter.ai/)

---

## 📚 Overview

**PhyAI Humanoid Textbook** is a production-ready educational platform combining a comprehensive humanoid robotics textbook with an intelligent RAG (Retrieval-Augmented Generation) chatbot. Students can read content AND ask questions about it in real-time with **streaming responses, citations, and context-aware explanations**.

### 🎯 Key Features

✅ **Streaming Chat Responses** - Real-time token-by-token generation like ChatGPT
✅ **Selected Text Q&A** - Highlight text → Click "Ask about this" → Get explanations
✅ **Citation Support** - Every answer includes source references with confidence scores
✅ **Session Persistence** - Conversation history saved across page reloads
✅ **100% Free Embeddings** - Local sentence-transformers (no API costs)
✅ **Free LLM Tier** - OpenRouter with mistralai/devstral-2512:free
✅ **Windows + WSL Support** - Works seamlessly on Windows development machines
✅ **Production Ready** - PostgreSQL, Qdrant Cloud, structured logging, Prometheus metrics

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                      │
│  • Chat Widget (streaming SSE)                          │
│  • Selected Text Detection                              │
│  • Citation Display                                     │
│  • Session Management                                   │
└────────────────┬────────────────────────────────────────┘
                 │ HTTP/SSE
┌────────────────▼────────────────────────────────────────┐
│              BACKEND (FastAPI)                          │
│  • REST API Endpoints                                   │
│  • RAG Pipeline Orchestration                           │
│  • Server-Sent Events Streaming                         │
│  • Session & Message CRUD                               │
└─┬──────────┬──────────┬──────────────┬─────────────────┘
  │          │          │              │
  │ Postgres │  Qdrant  │  OpenRouter  │  Sentence
  │          │  Cloud   │  (LiteLLM)   │  Transformers
  │          │          │              │  (Local)
  │          │          │              │
  └──────────┴──────────┴──────────────┴─────────────────┘
```

### RAG Data Flow

```
User Question
    ↓
Local Embeddings (sentence-transformers, FREE)
    ↓
Vector Search (Qdrant Cloud, 913 chunks)
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

### Frontend

| Technology | Purpose |
|------------|---------|
| **React 18.3** | UI framework with hooks |
| **TypeScript 5.0** | Type-safe development |
| **Tailwind CSS 3.4** | Utility-first styling |
| **Vite** | Build tool & dev server |
| **React Router** | Client-side routing |

### Backend

| Technology | Purpose |
|------------|---------|
| **FastAPI 0.115** | Async Python web framework |
| **PostgreSQL** (asyncpg) | Session & message storage |
| **Qdrant Cloud 1.16** | Vector database (913 chunks) |
| **Sentence-Transformers** | **Local embeddings (100% free!)** |
| **OpenAI Agents SDK** | LLM orchestration |
| **LiteLLM** | **OpenRouter integration** |
| **Structlog** | Structured JSON logging |
| **Prometheus** | Metrics & monitoring |

---

## 🚀 Quick Start

### Prerequisites

- **Node.js 18+** and npm
- **Python 3.11+**
- **PostgreSQL** (local or cloud)
- **Qdrant Cloud** account (free tier available)
- **OpenRouter API key** (free tier available)

### 1. Clone Repository

```bash
git clone <repository-url>
cd phyai-humanoid-textbook
```

### 2. Backend Setup

```bash
cd backend/rag-chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/phyai_textbook

# Qdrant Cloud
QDRANT_URL=https://your-cluster.cloud.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-api-key
QDRANT_COLLECTION_NAME=textbook_chunks

# OpenRouter LLM (Free Tier)
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=mistralai/devstral-2512:free

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
EOF

# Start backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Backend runs on:** http://localhost:8000
**API docs:** http://localhost:8000/docs

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
echo "VITE_API_URL=http://localhost:8000" > .env.local

# Start development server
npm run dev
```

**Frontend runs on:** http://localhost:3000

### 4. Verify Setup

**Backend Health:**
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "dependencies": {...}}
```

**Test Chat:**
```bash
curl -X POST "http://localhost:8000/api/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "question": "What is ROS 2?"}'
# Expected: Streaming SSE response with answer
```

**Frontend:**
1. Open http://localhost:3000
2. Click chat icon (bottom right)
3. Ask: "What is ROS 2?"
4. Should see streaming response with citations

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

1. **Select text** from the textbook (50-500 characters)
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

- **Storage:** PostgreSQL database
- **Recovery:** Auto-recovery on backend restart
- **History:** Last 12 messages included in context
- **Stateless:** Frontend can resume any session by ID

---

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname

# Qdrant Cloud
QDRANT_URL=https://xxx.cloud.qdrant.io:6333
QDRANT_API_KEY=your-key
QDRANT_COLLECTION_NAME=textbook_chunks

# OpenRouter LLM
OPENROUTER_API_KEY=sk-or-v1-xxx
OPENROUTER_MODEL=mistralai/devstral-2512:free

# CORS
CORS_ORIGINS=http://localhost:3000
```

**Frontend (.env.local):**
```bash
VITE_API_URL=http://localhost:8000
```

### Windows + WSL Setup

If running backend on WSL and frontend on Windows:

1. Get WSL IP: `ip addr show eth0 | grep inet`
2. Update `frontend/src/components/ChatWidget/config.ts`:
```typescript
return 'http://172.25.218.26:8000';  // Replace with your WSL IP
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
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── ChatWidget/
│   │   │       ├── ChatWidget.tsx
│   │   │       ├── components/
│   │   │       ├── hooks/
│   │   │       ├── api/
│   │   │       └── types.ts
│   │   ├── pages/
│   │   └── App.tsx
│   └── package.json
│
├── backend/rag-chatbot/
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
│   │   └── main.py
│   ├── scripts/
│   │   ├── ingest_book.py
│   │   └── init_qdrant.py
│   └── requirements.txt
│
└── README.md
```

---

## 🚧 Roadmap

### ✅ Completed

- [x] RAG chatbot with streaming responses
- [x] Selected text Q&A feature
- [x] Citation system with confidence scores
- [x] Session persistence
- [x] Windows + WSL support
- [x] Free embeddings (local sentence-transformers)
- [x] Free LLM tier (OpenRouter)
- [x] Production logging & metrics

### 🔜 Coming Soon

- [ ] Multi-language support (ES, ZH, JA)
- [ ] Voice input/output (Web Speech API)
- [ ] Mobile-responsive chat widget
- [ ] Export conversation history
- [ ] Advanced search (semantic + keyword)
- [ ] Quiz generation from content
- [ ] Progress tracking dashboard

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

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 🙏 Acknowledgments

Built with amazing open-source technologies:

- **React** - UI framework
- **FastAPI** - Python web framework
- **Qdrant** - Vector database
- **Sentence Transformers** - Embedding models
- **OpenAI Agents SDK** - LLM orchestration
- **LiteLLM** - Multi-provider LLM proxy
- **PostgreSQL** - Database
- **Tailwind CSS** - Styling

---

## 📞 Support

- **Documentation:** See `backend/rag-chatbot/BACKEND_ARCHITECTURE_REPORT.md`
- **Setup Help:** See `backend/rag-chatbot/START_COMMANDS.md`
- **Issues:** Open a GitHub issue with detailed info
- **Questions:** Check existing issues or create a new one

---

## 🏆 Highlights

✅ **100% Free Embeddings** - No API costs for retrieval
✅ **Free LLM Tier** - mistralai/devstral-2512:free
✅ **Production Ready** - PostgreSQL, Qdrant, metrics
✅ **Well Documented** - Comprehensive guides included

---

<div align="center">

**Built for education, powered by open source** 🚀

*Making AI-powered learning accessible to everyone*

</div>
