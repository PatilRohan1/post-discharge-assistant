# Post-Discharge Medical AI Assistant

Production-ready multi-agent AI system for post-discharge patient care with RAG-powered medical knowledge, intelligent agent orchestration, and real-time patient data retrieval.

---

## Overview

**Post-Discharge Medical AI Assistant** is an enterprise-grade conversational AI platform designed for healthcare interactions. Built on FastAPI with multi-agent architecture, it combines patient database management, nephrology reference materials (RAG), and web search to provide comprehensive post-discharge support.

**Tech Stack:**
- **LLM:** Groq API (Llama 3.1 - 100% FREE)
- **Embeddings:** Sentence Transformers (Local - 100% FREE)
- **Vector Database:** ChromaDB (Persistent)
- **Web Search:** DuckDuckGo (100% FREE)
- **Backend Framework:** FastAPI (Python 3.8+)
- **Frontend:** Streamlit

**Features:**
- 27+ dummy patient records with comprehensive medical data
- 1000+ page nephrology reference book processing with OCR
- Multi-agent orchestration (Receptionist → Clinical)
- RAG with semantic search and citations
- Web search fallback for recent medical information
- Comprehensive logging system

---

## Quick Start

### Prerequisites

- Python 3.8+
- Tesseract OCR installed
- Poppler (for PDF processing)
- Groq API key (FREE - no credit card required)

### System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr poppler-utils
```

**macOS:**
```bash
brew install tesseract poppler
```

**Windows:**
- Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
- Poppler: https://github.com/oschwartz10612/poppler-windows/releases

### Installation

```bash
git clone https://github.com/yourusername/post-discharge-assistant.git
cd post-discharge-assistant

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Configure API keys in .env
```

### Environment Variables

```bash
# Groq API (FREE - get from https://console.groq.com/keys)
GROQ_API_KEY=gsk_your_key_here

# Application
APP_MODE=development
PORT=8000

# Models (FREE)
RECEPTIONIST_MODEL=llama-3.1-8b-instant
CLINICAL_MODEL=llama-3.1-70b-versatile
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Paths
LOG_FOLDER_PATH=src/logs
DATA_FOLDER_PATH=src/data
VECTOR_DB_PATH=src/vector_db
PATIENTS_JSON_PATH=src/data/patients.json
NEPHROLOGY_PDF_PATH=src/data/nephrology_book.pdf
```

### Running the Application

```bash
# Terminal 1: Start Backend
cd src
python main.py
# Backend starts on http://localhost:8000

# Terminal 2: Start Frontend
cd frontend
python -m streamlit run streamlit_app.py
# Frontend opens at http://localhost:8501
```

---

## Architecture

```
User → Streamlit → FastAPI → Agent Orchestrator → Tools (DB/RAG/Web) → Response
```

**Flow:**
1. User sends message via Streamlit interface
2. FastAPI receives request at `/api/v1/chat/message`
3. Chat Service routes to appropriate agent:
   - **Receptionist Agent**: Patient identification, general queries
   - **Clinical Agent**: Medical questions, RAG + web search
4. Agents use tools:
   - Patient Database Tool: Retrieve discharge reports
   - RAG Tool: Search nephrology reference materials
   - Web Search Tool: Find current medical information
5. LLM Service (Groq API) generates responses
6. Complete interaction logged to file system
7. Response returned to user with citations

---

## Project Structure

```
post-discharge-assistant/
├── src/
│   ├── main.py                          # FastAPI server entry point
│   ├── api/
│   │   ├── custom_exception.py          # Custom exception classes
│   │   ├── error_handler.py             # Centralized error handling
│   │   └── chat/
│   │       ├── chat_controller.py       # API endpoints
│   │       ├── chat_service.py          # Business logic
│   │       └── chat_models.py           # Pydantic models
│   ├── agents/
│   │   ├── receptionist_agent.py        # Patient identification & routing
│   │   └── clinical_agent.py            # Medical Q&A with RAG
│   ├── tools/
│   │   ├── patient_db_tool.py           # Patient database operations
│   │   ├── rag_tool.py                  # RAG implementation (PDF + OCR)
│   │   └── web_search_tool.py           # DuckDuckGo search
│   ├── services/
│   │   ├── llm_service.py               # Groq API integration
│   │   ├── session_service.py           # Session management
│   │   └── patient_service.py           # Patient business logic
│   ├── utils/
│   │   └── logger.py                    # Loguru-based logging
│   ├── constants/
│   │   ├── environment_constants.py     # Environment config
│   │   └── http_constants.py            # HTTP status codes
│   ├── data/
│   │   ├── patients.json                # 27 patient records
│   │   └── nephrology_book.pdf          # 1000+ page reference
│   ├── vector_db/                       # ChromaDB storage (auto-created)
│   └── logs/                            # Daily log files
│       └── YYYY-MM-DD/
│           ├── file_info.log
│           └── file_error.log
├── frontend/
│   └── streamlit_app.py                 # Web interface
├── requirements.txt
├── .env.example
├── README.md
└── FREE_APIS_SETUP.md                   # Detailed API setup guide
```

---

## Core Components

### 1. main.py - API Gateway

FastAPI server managing HTTP endpoints and application lifecycle.

**Endpoints:**
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/` | GET | Health check |
| `/api/v1/chat/message` | POST | Send chat message |
| `/api/v1/chat/session/{id}` | GET | Get session info |
| `/api/v1/chat/session/{id}/reset` | POST | Reset session |
| `/api/v1/chat/greeting` | GET | Get initial greeting |
| `/api/v1/chat/patients` | GET | List all patients |

**Features:**
- CORS middleware for frontend integration
- Async lifespan management
- Centralized error handling
- Request validation with Pydantic

### 2. chat_service.py - Business Logic

Orchestrates conversation flow between agents and manages session state.

**Key Features:**
- **Session Management**: Maintains conversation context per user
- **Agent Routing**: Intelligently switches between Receptionist and Clinical agents
- **State Persistence**: Tracks patient identification and conversation history
- **Error Recovery**: Graceful handling of service failures

**Critical Methods:**
- `process_message()`: Main entry point for chat processing
- `_route_to_agent()`: Determines appropriate agent for message
- `_update_session_state()`: Maintains conversation context
- `_format_response()`: Structures response with metadata

### 3. receptionist_agent.py - Patient Interface

Handles patient identification and general conversation management.

**Responsibilities:**
- Greet patients and collect names
- Search patient database using fuzzy matching
- Ask follow-up questions about recovery
- Detect medical queries and route to Clinical Agent
- Maintain conversational tone

**Input:** Patient name/message  
**Output:** Greeting/acknowledgment or route to Clinical Agent

**Features:**
- Name extraction using pattern matching
- Multiple patient name handling
- Personalized discharge report summaries
- Medical keyword detection for routing

### 4. clinical_agent.py - Medical Knowledge Expert

Handles medical questions using RAG and web search with proper citations.

**Configuration:**
- Model: Llama 3.1 70B (Groq)
- Temperature: 0.3 (factual responses)
- Max tokens: 1500
- Context: Full conversation + patient data

**Workflow:**
1. Receive medical query from Receptionist Agent
2. Search RAG (nephrology reference book)
3. Determine if web search needed (recent info keywords)
4. Generate response with LLM using all context
5. Format response with proper citations
6. Add medical disclaimer

**Citation Format:**
- Reference book: `[Source: Reference Book, Page X]`
- Web search: `[Source: Web - URL]`

### 5. patient_db_tool.py - Database Operations

Manages patient record retrieval with error handling.

**Features:**
- Fuzzy name matching (handles typos, partial names)
- Multiple patient detection
- Structured error responses
- Formatted discharge summaries

**Data Structure:**
```json
{
  "patient_name": "John Smith",
  "patient_id": "P001",
  "discharge_date": "2024-01-15",
  "primary_diagnosis": "Chronic Kidney Disease Stage 3",
  "medications": ["Lisinopril 10mg daily"],
  "dietary_restrictions": "Low sodium (2g/day)",
  "follow_up": "Nephrology clinic in 2 weeks",
  "warning_signs": "Swelling, shortness of breath",
  "discharge_instructions": "Monitor BP daily"
}
```

### 6. rag_tool.py - Knowledge Retrieval

Processes 1000+ page nephrology PDF with OCR fallback and semantic search.

**Features:**
- **PDF Processing**: Text extraction + OCR for scanned pages
- **Chunking**: RecursiveCharacterTextSplitter (1000 chars, 200 overlap)
- **Embeddings**: Sentence Transformers (384 dimensions, local)
- **Vector DB**: ChromaDB (persistent, one-time creation)
- **Search**: Semantic similarity with relevance scores
- **Citations**: Page numbers and source tracking

**First Run:** 10-30 minutes (PDF processing + embedding)  
**Subsequent Runs:** <5 seconds (loads existing vector DB)

**Optimization:**
- Checks if vector DB exists before processing
- Logs progress every 100 pages
- Graceful fallback to OCR for unreadable pages

### 7. web_search_tool.py - Current Information

DuckDuckGo integration for recent medical information.

**Use Cases:**
- Latest research papers
- Recent treatment guidelines
- New medications/procedures
- Current clinical trials

**Trigger Keywords:**
- "latest", "recent", "new", "current"
- "2024", "2025", "research", "study"

**Output Format:**
```python
{
  "title": "Article title",
  "snippet": "Brief description...",
  "link": "https://source.com",
  "source": "Web Search (DuckDuckGo)"
}
```

### 8. llm_service.py - AI Response Generation

Groq API integration for ultra-fast LLM responses.

**Models:**
- **Receptionist**: Llama 3.1 8B Instant (100+ tokens/sec)
- **Clinical**: Llama 3.1 70B Versatile (50+ tokens/sec)

**Methods:**
- `generate_receptionist_response()`: Quick, conversational (temp: 0.7)
- `generate_clinical_response()`: Detailed, factual (temp: 0.3)
- `generate_with_context()`: Full conversation history support

**Performance:**
- First token latency: 300-500ms
- Total generation: 1-2 seconds for full response
- Cost: $0 (completely FREE)

### 9. session_service.py - State Management

Manages user sessions and conversation context.

**Features:**
- Session creation and retrieval
- Conversation history tracking
- Patient context persistence
- Session reset functionality

**Session Structure:**
```python
{
  "session_id": "uuid",
  "current_agent": "receptionist",
  "patient_identified": False,
  "patient_context": {...},
  "conversation_history": [
    {"timestamp": "...", "role": "user", "message": "..."},
    {"timestamp": "...", "role": "assistant", "message": "..."}
  ]
}
```

### 10. logger.py - Logging System

Loguru-based logging with daily file rotation and environment-specific configuration.

**Features:**
- Daily log files (organized by date)
- Separate info and error logs
- Full traceback for exceptions
- Production-optimized (no backtrace in production)

**Log Structure:**
```
src/logs/
└── 2024-11-09/
    ├── file_info.log    # Info level messages
    └── file_error.log   # Error level with tracebacks
```

---

## Performance Metrics

| Component | Current | Technology |
|-----------|---------|------------|
| Patient DB Lookup | <50ms | JSON in-memory |
| RAG Search | 100-200ms | ChromaDB + HuggingFace |
| LLM First Token | 300-500ms | Groq (Llama 3.1) |
| LLM Full Response | 1-2s | Streaming generation |
| Web Search | 500-1000ms | DuckDuckGo |
| End-to-End | 2-4s | Full pipeline |

---

## Key Features

### Implemented

- Multi-agent architecture (Receptionist + Clinical)
- 27 comprehensive patient records
- RAG with 1000+ page nephrology reference
- OCR fallback for scanned PDF pages
- Vector database with one-time creation
- Semantic search with citations
- Web search for recent information
- Session management with conversation history
- Intelligent agent routing
- Comprehensive logging system
- Medical disclaimers on all responses
- Streamlit web interface
- 100% FREE APIs (no costs)

###  In Progress

- Multi-language support
- Voice interface integration
- Enhanced fuzzy matching for patient names

### Roadmap

- Email/SMS notifications for appointments
- Integration with EHR systems
- Medication reminder system
- Symptom severity assessment
- Emergency escalation protocols
- Analytics dashboard
- Multi-tenant support
- Mobile app (React Native)

---

## Development

### Local Testing

```bash
# Terminal 1: Backend with auto-reload
cd src
python main.py
# Or with uvicorn directly:
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
python -m streamlit run streamlit_app.py

# Terminal 3: Test API directly
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test123",
    "message": "My name is John Smith",
    "current_agent": "receptionist"
  }'
```

### Testing Patient Names

Try these test patients (from `patients.json`):
- John Smith (CKD Stage 3)
- Sarah Johnson (Acute Kidney Injury)
- Michael Chen (CKD Stage 4)
- Emily Davis (Nephrotic Syndrome)
- Robert Martinez (Polycystic Kidney Disease)
- Linda Brown (Diabetic Nephropathy)
- James Wilson (Glomerulonephritis)
- Patricia Garcia (Kidney Stones)

### Deployment Checklist

- [ ] Groq API key configured
- [ ] Tesseract and Poppler installed
- [ ] Nephrology PDF placed in `src/data/`
- [ ] Vector database created (first run)
- [ ] Environment variables validated
- [ ] CORS origins configured
- [ ] SSL certificate installed (production)
- [ ] Logging paths writable
- [ ] Health check endpoint accessible
- [ ] Rate limiting configured (if needed)

---

## Troubleshooting

**Issue:** Vector database not found  
**Solution:** 
```bash
# First run will create it automatically (10-30 minutes)
# Or manually trigger creation:
cd src
python -c "from tools.rag_tool import RAGTool; RAGTool()"
```

**Issue:** Groq API authentication failed  
**Solution:** 
```bash
# Verify API key
echo $GROQ_API_KEY
# Should start with "gsk_"

# Test connection
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer $GROQ_API_KEY"
```

**Issue:** Tesseract not found  
**Solution:** 
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Verify installation
tesseract --version
```

**Issue:** Patient not found  
**Solution:** 
- Check spelling carefully
- Try full name (e.g., "John Smith" not "John")
- View all patients: GET `/api/v1/chat/patients`

**Issue:** High memory usage during PDF processing  
**Solution:** 
- Process PDF once, reuse vector DB
- Reduce chunk size in `.env`: `CHUNK_SIZE=500`
- Use smaller batch sizes for OCR

**Issue:** Slow RAG search  
**Solution:** 
```bash
# Rebuild vector DB with smaller chunks
rm -rf src/vector_db/
# Restart backend to rebuild
```

---

## Technical Concepts

### Multi-Agent Architecture

Two specialized agents with distinct responsibilities:
- **Receptionist**: First contact, patient identification, general queries
- **Clinical**: Medical expertise, RAG-powered answers, citations

Benefits:
- **Separation of concerns**: Each agent optimized for specific tasks
- **Efficiency**: Lighter model for simple tasks, powerful model for complex queries
- **Cost optimization**: Use cheaper/faster models where appropriate

### RAG (Retrieval Augmented Generation)

Combines information retrieval with LLM generation:
1. User asks medical question
2. Search vector database for relevant chunks
3. Retrieve top 3 most similar passages
4. Inject passages into LLM context
5. Generate answer grounded in reference material

Benefits:
- **Accuracy**: Reduces hallucinations
- **Citations**: Traceable sources (page numbers)
- **Up-to-date**: Add new PDFs without retraining

### Vector Embeddings

Text → Numbers that capture semantic meaning:
- "kidney failure" and "renal failure" have similar vectors
- Enables semantic search (meaning-based, not keyword-based)
- 384 dimensions per chunk (all-MiniLM-L6-v2)

### Session Management

Stateful conversations require tracking:
- **Session ID**: Unique identifier per user
- **Conversation history**: Last N messages for context
- **Patient context**: Retrieved discharge report
- **Current agent**: Which agent is handling the conversation

