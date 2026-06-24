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
       ├── MemoryService (PostgreSQL + Summarization)
       └── LLMService (OpenAI GPT-4o-mini)
                     │
                     ▼
               PostgreSQL
```

### Tech Stack

| Component | Technology |
|---|---|
| Backend | FastAPI (Python 3.11) |
| LLM | GPT-4o-mini (OpenAI SDK) |
| Database | PostgreSQL 16 |
| Frontend | React (Vite) |
| Containerization | Docker Compose |

## Quick Start

```bash
# 1. Clone the repository
git clone <repo-url>
cd ai-healthcare-assistant

# 2. Add your OpenAI API key
# Edit the .env file and replace 'your-api-key-here' with your actual key
nano .env

# 3. Run the application
docker compose up --build

# 4. Open the UI
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

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

1. **Full Persistence**: Every message (user, assistant, tool) is stored in PostgreSQL
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
- Estimated cost (based on GPT-4o-mini pricing)

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
| `OPENAI_API_KEY` | — | Your OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model to use |
| `OPENAI_TEMPERATURE` | `0.3` | Response randomness |
| `OPENAI_MAX_TOKENS` | `1024` | Max response tokens |
| `OPENAI_FREQUENCY_PENALTY` | `0.0` | Frequency penalty |

## Trade-offs

| Decision | Rationale |
|---|---|
| **OpenAI SDK** over LangChain | Simpler, fewer abstractions, direct control over prompts and tool calling |
| **PostgreSQL** for memory | Persistent, queryable, supports the conversation + summary pattern well |
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
├── .env
└── README.md
```
