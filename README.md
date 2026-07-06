# ResearchGPT – AI Research Assistant

A production-ready **Retrieval-Augmented Generation (RAG)** research assistant that lets you upload research papers, books, lecture notes, and documents — then ask questions and get **cited answers** grounded only in your uploaded content.

![Tech Stack](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat)
![FAISS](https://img.shields.io/badge/FAISS-0466C8?style=flat)
![Gemini](https://img.shields.io/badge/Google_Gemini-4285F4?style=flat&logo=google&logoColor=white)

---

## Features

### Core RAG Pipeline
- **Document Upload** — PDF, DOCX, TXT, Markdown
- **Intelligent Chunking** — Semantic text splitting with page metadata
- **Vector Search** — FAISS + Sentence Transformers embeddings
- **Hybrid Retrieval** — Semantic + keyword search with cross-encoder reranking
- **Cited Answers** — Every response includes document name, page number, paragraph, and confidence score
- **Streaming Responses** — Real-time token streaming via SSE

### Authentication
- JWT-based auth with bcrypt password hashing
- Signup, login, profile management

### AI Research Tools
- Document summarization
- Compare two research papers
- Generate literature reviews
- Quiz & flashcard generation
- Entity & keyword extraction

### UI
- Modern dark/light mode interface
- Drag-and-drop file upload
- Real-time chat with Markdown, math (KaTeX), and code rendering
- Document panel with search, rename, delete
- Export chats to Markdown, PDF, DOCX
- Voice input (Web Speech API)

---

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   React UI  │────▶│   FastAPI    │────▶│   Gemini    │
│  (Vite+TS)  │◀────│   Backend    │◀────│     API     │
└─────────────┘     └──────┬───────┘     └─────────────┘
                           │
                    ┌──────┴───────┐
                    │  RAG Pipeline │
                    ├──────────────┤
                    │  PyMuPDF     │  Text extraction
                    │  Chunker     │  Semantic splitting
                    │  Embeddings  │  Sentence Transformers
                    │  FAISS       │  Vector store
                    │  Retriever   │  Hybrid search
                    │  Reranker    │  Cross-encoder
                    └──────┬───────┘
                           │
                    ┌──────┴───────┐
                    │   SQLite     │
                    └──────────────┘
```

---

## Project Structure

```
researchgpt/
├── backend/
│   ├── api/routers/       # FastAPI route handlers
│   ├── auth/              # JWT & password utilities
│   ├── database/          # SQLAlchemy models & session
│   ├── models/            # Pydantic schemas
│   ├── rag/               # Embeddings, FAISS, retrieval, LLM
│   ├── services/          # Business logic layer
│   ├── utils/             # Document parsing, export, logging
│   ├── tests/             # Unit tests
│   ├── config.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # React UI components
│   │   ├── pages/         # Route pages
│   │   ├── hooks/         # React Query hooks
│   │   ├── services/      # API client
│   │   ├── context/       # Auth & theme providers
│   │   └── types/         # TypeScript interfaces
│   └── package.json
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── .env.example
└── README.md
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Google Gemini API key ([Get one here](https://aistudio.google.com/apikey))

### 1. Clone & Configure

```bash
cd researchgpt
cp .env.example .env
# Edit .env and set your GOOGLE_API_KEY
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Run backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at: http://localhost:8000/docs

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

### 4. Docker (Alternative)

```bash
cp .env.example .env
# Set GOOGLE_API_KEY in .env

docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/signup` | Create account |
| POST | `/api/v1/auth/login` | Login & get JWT |
| GET | `/api/v1/auth/me` | Get current user |
| POST | `/api/v1/documents/upload` | Upload document |
| GET | `/api/v1/documents` | List documents |
| DELETE | `/api/v1/documents/{id}` | Delete document |
| PATCH | `/api/v1/documents/{id}/rename` | Rename document |
| POST | `/api/v1/chat` | Chat (streaming SSE) |
| GET | `/api/v1/history` | Conversation history |
| DELETE | `/api/v1/history` | Clear all history |
| POST | `/api/v1/search` | Hybrid search |
| GET | `/api/v1/summary/{id}` | Document summary |
| POST | `/api/v1/compare` | Compare papers |
| POST | `/api/v1/quiz` | Generate quiz |
| POST | `/api/v1/flashcards` | Generate flashcards |
| POST | `/api/v1/export` | Export chat |

---

## RAG Pipeline

```
Upload Document
      │
      ▼
Extract Text (PyMuPDF / python-docx)
      │
      ▼
Clean & Split into Chunks (LangChain)
      │
      ▼
Generate Embeddings (Sentence Transformers)
      │
      ▼
Store in FAISS + Metadata in SQLite
      │
      ▼
User Asks Question
      │
      ▼
Embed Query → Hybrid Retrieve → Rerank
      │
      ▼
Build Prompt with Context → Gemini Generates Answer
      │
      ▼
Return Answer + Citations (doc, page, score)
```

### Prompt Template

The LLM is instructed to:
- Answer **only** from retrieved context
- Say *"I could not find this information in your uploaded documents."* when context is insufficient
- **Never hallucinate**
- Always include `[Source N]` citations

---

## Testing

```bash
# Activate venv first
pip install -r backend/requirements.txt

# Run all tests
pytest backend/tests/ -v

# Run with coverage
pytest backend/tests/ --cov=backend --cov-report=term-missing
```

### Test Coverage
- Health check endpoint
- User signup & login flow
- Unauthorized access protection
- Text cleaning utilities

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_API_KEY` | — | **Required.** Google Gemini API key |
| `SECRET_KEY` | change-me | JWT signing secret |
| `GEMINI_MODEL` | gemini-2.0-flash | Gemini model name |
| `EMBEDDING_MODEL` | all-MiniLM-L6-v2 | Sentence Transformers model |
| `CHUNK_SIZE` | 1000 | Text chunk size (chars) |
| `CHUNK_OVERLAP` | 200 | Chunk overlap (chars) |
| `TOP_K` | 10 | Initial retrieval count |
| `RERANK_TOP_K` | 5 | Post-rerank count |
| `MAX_UPLOAD_SIZE_MB` | 50 | Max file upload size |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI, Uvicorn |
| RAG | LangChain, FAISS, Sentence Transformers |
| LLM | Google Gemini API |
| Document Parsing | PyMuPDF, python-docx, Unstructured |
| Database | SQLite (SQLAlchemy async) |
| Auth | JWT, bcrypt |
| Frontend | React 18, Vite, TypeScript |
| Styling | Tailwind CSS |
| State | React Query, Context API |
| Animation | Framer Motion |
| Markdown | react-markdown, KaTeX, GFM |

---

## Design Principles

- **SOLID** — Service layer separation, dependency injection
- **Clean Architecture** — Routers → Services → RAG/DB layers
- **Type Safety** — Python type hints + TypeScript strict mode
- **Async-first** — Async FastAPI with aiosqlite
- **No Hallucination** — Strict context-only prompting with citations

---

## License

MIT License — free for personal and commercial use.

---

Built with ❤️ for researchers, students, and knowledge workers.
