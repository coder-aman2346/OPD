Take Home Assignment – AI Healthcare Assistant

Time Limit: 2 Days

Problem Statement

Build an AI-powered healthcare assistant that can:

* Collect symptoms from a patient through conversation
* Ask relevant follow-up questions
* Recommend an appropriate department (ENT, Neurology, Orthopedics, etc.)
* Book appointments using provided APIs
* Generate a doctor-facing summary after booking

The focus of this assignment is LLM engineering and software engineering practices, not frontend development.

⸻

Required APIs

Create Appointment

POST /appointments

Request:

{
"patient_name": "John Doe",
"department": "ENT",
"visit_date": "2026-07-01",
"summary": "Patient reports ringing in ears for 3 days."
}

Response:

{
"appointment_id": "apt_123"
}

List Appointments

GET /appointments

Response:

[
{
"appointment_id": "apt_123",
"patient_name": "John Doe",
"department": "ENT",
"visit_date": "2026-07-01"
}
]

⸻

Chatbot Requirements

The chatbot should:

* Maintain conversation context
* Ask relevant follow-up questions before booking an appointment
* Use function/tool calling for appointment creation
* Generate department-specific summaries for doctors
* Support multiple appointments within the same conversation

Example:

A user may discuss both recurring headaches and hearing issues.

The assistant should be able to:

* Book a Neurology appointment
* Book an ENT appointment
* Generate separate summaries for each department

⸻

LLM Configuration

Support runtime configuration for:

* Model
* Temperature
* Max Tokens
* Frequency Penalty
* Response Schema (if supported)

⸻

Observability

Capture and expose:

* Input Tokens
* Output Tokens
* Cached Tokens (if available)
* Total Tokens
* Time To First Token (TTFT)
* Request Latency

These can be surfaced through logs, API responses, or a simple dashboard.

⸻

Safety

Implement basic guardrails:

* PII detection/redaction (email, phone number, etc.)
* Prompt injection protection
* Prevent medical diagnosis or prescription recommendations

Reasonable implementations are sufficient.

⸻

Frontend

A minimal chat interface is sufficient.

Frontend polish will not be evaluated.

⸻

Deliverables

Submit the assignment as a private GitHub repository and add the following collaborators:

* parassain
* vedang-sixhats

The repository should contain:

* Source code
* README
* Docker Compose setup

The application should be runnable locally using:

docker compose up

The README should briefly describe:

* Architecture
* Prompting strategy
* Memory implementation
* Guardrails
* Tradeoffs made

⸻

Evaluation Criteria

We will primarily evaluate:

* Prompt Engineering
* Tool Calling & Agent Design
* Code Quality & Repository Structure
* Observability & Guardrails
* Documentation

Frontend design and API complexity are not evaluation criteria.

Bonus Points

* Structured outputs
* Cost tracking
* Conversation tracing
* Automated tests
* Clean LLM abstraction