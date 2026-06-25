# AI Healthcare Assistant

An AI-powered healthcare assistant that collects patient symptoms through conversation, asks relevant follow-up questions, recommends appropriate medical departments, books appointments, and generates doctor-facing summaries.

## Architecture

```
                React UI (Vite)
                     │
                     ▼
              FastAPI Routes
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
  ChatService  AppointmentSvc  MetricsSvc
       │
       ├── GuardrailService (PII + Injection + Safety)
       ├── MemoryService (SQLite/PostgreSQL + Summarization)
       └── LLMService (Gemini 2.5 Flash)
                     │
                     ▼
               SQLite / PostgreSQL
```

### Tech Stack

| Component | Technology |
|---|---|
| Backend | FastAPI (Python 3.11) |
| LLM | Gemini 2.5 Flash (via OpenAI Compatibility SDK) |
| Database | SQLite (Local) / PostgreSQL |
| Frontend | React (Vite) |
| Containerization | Docker Compose (Optional) |

## Quick Start

### 1. Clone the repository
```bash
git clone <repo-url>
cd ai-healthcare-assistant
```

### 2. Configure Environment Variables
Copy the `.env.example` file to `.env` and add your Gemini API key:
```bash
cp .env.example .env
# Edit .env and replace YOUR_GEMINI_API_KEY_HERE with your actual key
```

### 3. Run Locally (Without Docker)

**Backend (FastAPI):**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Or .\.venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m uvicorn app.main:app --port 8000 --reload
```

**Frontend (React/Vite):**
```bash
cd frontend
npm install
npm run dev
```

The UI will be available at `http://localhost:5173` and the backend API at `http://localhost:8000`.

### 4. Database Access
By default, the application uses a local SQLite database located at `backend/healthcare.db`. You can view it using any SQLite viewer (like the "SQLite Viewer" VS Code extension or DB Browser for SQLite).

## Prompting Strategy

### System Prompt
The system prompt instructs the LLM to:
- Act as a healthcare assistant (not a doctor)
- Collect symptoms and ask up to **3 follow-up questions** (duration, severity, associated symptoms)
- Map symptoms to one of 6 departments: ENT, Neurology, Orthopedics, Cardiology, Dermatology, General Medicine
- Collect patient name and preferred visit date before booking
- Use the `book_appointment` tool for appointment creation
- Handle multiple symptom clusters independently (e.g., headache → Neurology + ear pain → ENT)
- Always include a medical disclaimer

### Tool Calling
A single tool `book_appointment` is defined with **strict mode** (structured output):
- Parameters: `patient_name`, `department` (enum), `visit_date`, `summary`
- The LLM decides when to call this tool based on conversation context
- After tool execution, the LLM generates a confirmation message

### Summary Generation
Doctor-facing summaries are generated inline by the LLM when booking appointments, including:
- Chief complaint, duration, severity, associated symptoms
- Recommended department

## Memory Implementation

1. **Full Persistence**: Every message (user, assistant, tool) is stored in the database.
2. **Running Summary**: When conversation exceeds 20 messages, older messages are summarized via LLM and stored as a `conversation_summary`
3. **Context Window**: The LLM receives the summary (if exists) + last 10 messages, keeping the context window manageable
4. **Compaction**: After summarization, older messages are deleted from the messages table

## Guardrails

### PII Detection
- Regex-based detection for: **email**, **phone numbers**, **SSN**
- Non-blocking: user receives a warning but the message is still processed
- PII is detected in the user's input before sending to the LLM

### Prompt Injection Protection
- 13 regex patterns detecting common injection attempts:
  - "ignore previous instructions", "reveal system prompt", "developer mode", "jailbreak", etc.
- **Blocking**: message is rejected and a safe response is returned without calling the LLM

### Medical Safety
- Enforced via system prompt: the LLM is instructed to never diagnose or prescribe
- Every response includes a medical disclaimer
- The LLM only recommends departments, never treatments

## Observability

### Per-Request Metrics (in API response)
- Input tokens, output tokens, cached tokens, total tokens
- Time to First Token (TTFT)
- Request latency
- Model used

### Aggregate Metrics (`GET /metrics`)
- Total requests and appointments
- Average latency and TTFT
- Total token usage across all categories
- Estimated cost (based on Gemini API pricing)

### Conversation Tracing
- Unique request ID per HTTP request (returned in `X-Request-ID` header)
- Conversation ID tracking across messages
- Structured JSON logging with request/conversation context

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/chat` | Send a message to the assistant |
| POST | `/appointments` | Create an appointment directly |
| GET | `/appointments` | List all appointments |
| GET | `/metrics` | Get aggregate metrics |
| GET | `/health` | Health check |
| GET | `/docs` | Swagger UI |

## LLM Configuration

All parameters are configurable via environment variables in `.env`:

| Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | — | Your Gemini API key |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Model to use |
| `GEMINI_API_BASE` | `https://generativelanguage.googleapis.com/v1beta/openai/` | OpenAI Compatibility Layer Base URL |

## Trade-offs

| Decision | Rationale |
|---|---|
| **Gemini via OpenAI SDK** over native SDK | Simpler, uses existing OpenAI abstractions, direct control over prompts and tool calling |
| **SQLite / PostgreSQL** for memory | Persistent, queryable, supports the conversation + summary pattern well |
| **Strict mode** tool calling | Ensures structured, validated outputs from the LLM |
| **Regex-based** guardrails | Fast, no additional API calls; reasonable for the scope |
| **In-memory** metrics | Sufficient for single-instance; avoids adding Redis/Prometheus complexity |
| **Minimal React** frontend | Focus is on backend/LLM engineering per assessment criteria |
| **SQLAlchemy async** | Non-blocking DB operations in FastAPI's async request handling |

## Running Tests

```bash
cd backend
pip install -r requirements.txt
pip install aiosqlite  # Required for test DB
pytest -v
```

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI routes
│   │   ├── db/            # Database models & session
│   │   ├── prompts/       # LLM prompt templates
│   │   ├── services/      # Business logic layer
│   │   ├── utils/         # PII detection, logging
│   │   ├── config.py      # Environment configuration
│   │   └── main.py        # App entry point
│   ├── tests/             # pytest test suite
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/           # API client
│   │   ├── components/    # React components
│   │   ├── App.jsx        # Main app
│   │   └── index.css      # Design system
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```
