# AI Healthcare Assistant -- Low Level Design (LLD)

## Project Goal

Build a simple AI-powered Healthcare Assistant that:

-   Collects patient symptoms through conversation
-   Asks up to 3 relevant follow-up questions
-   Recommends the appropriate department
-   Books appointments using mock APIs
-   Generates a doctor-facing summary
-   Maintains conversation memory
-   Includes basic guardrails and observability

------------------------------------------------------------------------

# Tech Stack

  Component          Technology
  ------------------ ---------------------------
  Backend            FastAPI
  Language           Python 3.11
  LLM                GPT-4.1-mini (OpenAI SDK)
  Database           PostgreSQL
  Frontend           React
  Containerization   Docker Compose

------------------------------------------------------------------------

# High-Level Architecture

``` text
                React UI
                    │
                    ▼
             FastAPI Routes
                    │
      ┌─────────────┼─────────────┐
      ▼             ▼             ▼
 ChatService  AppointmentService MetricsService
      │
      ▼
   LLMService
      │
      ▼
 GuardrailService
      │
      ▼
 PostgreSQL
```

------------------------------------------------------------------------

# Folder Structure

``` text
backend/
├── app/
│   ├── api/
│   │   ├── chat.py
│   │   ├── appointments.py
│   │   └── metrics.py
│   ├── services/
│   │   ├── chat_service.py
│   │   ├── llm_service.py
│   │   ├── memory_service.py
│   │   ├── symptom_service.py
│   │   ├── appointment_service.py
│   │   ├── guardrail_service.py
│   │   └── metrics_service.py
│   ├── prompts/
│   │   ├── system_prompt.py
│   │   └── summary_prompt.py
│   ├── db/
│   │   ├── database.py
│   │   └── models.py
│   ├── utils/
│   │   ├── pii.py
│   │   └── logger.py
│   └── main.py
frontend/
docker-compose.yml
README.md
```

------------------------------------------------------------------------

# Core Components

## ChatService

Responsible for: - Receiving chat messages - Loading conversation
history - Calling guardrails - Extracting symptoms - Asking follow-up
questions - Calling the LLM - Booking appointments - Saving conversation

## LLMService

-   Build prompts
-   Invoke OpenAI SDK
-   Return structured response

## MemoryService

-   Load conversation
-   Save messages
-   Save conversation summary

## SymptomService

Rule-based symptom mapping.

Examples: - Headache → Neurology - Ear pain → ENT - Chest pain →
Cardiology - Back pain → Orthopedics - Skin rash → Dermatology

Unknown cases fall back to the LLM.

## AppointmentService

-   Create appointment
-   List appointments

## GuardrailService

-   PII redaction
-   Prompt injection detection
-   Medical disclaimer enforcement

## MetricsService

Tracks: - Input tokens - Output tokens - Total tokens - Latency -
Appointment count

------------------------------------------------------------------------

# Database Design

## conversations

  Column         Type
  -------------- -----------
  id             UUID
  patient_name   TEXT
  created_at     TIMESTAMP

## messages

  Column            Type
  ----------------- -----------
  id                UUID
  conversation_id   UUID
  role              TEXT
  content           TEXT
  created_at        TIMESTAMP

## appointments

  Column            Type
  ----------------- ------
  id                UUID
  conversation_id   UUID
  department        TEXT
  visit_date        DATE
  summary           TEXT

## conversation_summary

  Column            Type
  ----------------- -----------
  conversation_id   UUID
  summary           TEXT
  updated_at        TIMESTAMP

------------------------------------------------------------------------

# Request Flow

``` text
User
  │
POST /chat
  │
Guardrails
  │
Load Conversation
  │
Extract Symptoms
  │
Enough Information?
 ├── No → Ask Follow-up Question
 └── Yes
        │
Department Mapping
        │
LLM Response
        │
Create Appointment
        │
Generate Doctor Summary
        │
Persist Conversation
        │
Return Response
```

------------------------------------------------------------------------

# Prompt Strategy

## System Prompt

-   Ask a maximum of 3 follow-up questions
-   Never diagnose diseases
-   Never prescribe medication
-   Recommend departments only
-   Always include a medical disclaimer

## Routing Prompt

Select one of: - ENT - Neurology - Orthopedics - Cardiology -
Dermatology

## Summary Prompt

Generate a concise doctor-facing summary including: - Symptoms -
Duration - Severity - Recommended department

------------------------------------------------------------------------

# Memory Strategy

-   Store every message in PostgreSQL.
-   Maintain a running conversation summary.
-   When conversation grows large, summarize older messages and continue
    using the summary as context.

------------------------------------------------------------------------

# Multi-Appointment Handling

Maintain multiple symptom clusters within a conversation.

Example:

-   Headache → Neurology
-   Ear ringing → ENT

Each symptom cluster can independently trigger appointment creation.

------------------------------------------------------------------------

# Guardrails

## PII

Regex detection for: - Email - Phone number

## Prompt Injection

Detect common malicious phrases such as: - Ignore previous
instructions - Reveal system prompt - Developer mode

## Medical Safety

Always respond with:

> I am not a doctor and cannot provide a diagnosis or prescribe
> medication.

------------------------------------------------------------------------

# Observability

Expose a lightweight `/metrics` endpoint.

``` json
{
  "requests": 18,
  "appointments": 4,
  "avg_latency_ms": 720,
  "total_tokens": 9500
}
```

------------------------------------------------------------------------

# APIs

## POST /chat

Handles conversation with the AI assistant.

## POST /appointments

Creates an appointment.

## GET /appointments

Returns all appointments.

## GET /metrics

Returns usage metrics.

------------------------------------------------------------------------

# Docker Compose

Services: - backend - frontend - postgres

------------------------------------------------------------------------

# Testing

-   Symptom mapping
-   PII redaction
-   Appointment API
-   End-to-end conversation flow

------------------------------------------------------------------------

# 2-Day Milestone Plan

## Day 1

### Morning

-   Project setup
-   PostgreSQL setup
-   Database models

### Afternoon

-   ChatService
-   MemoryService
-   OpenAI integration
-   Symptom mapping

### Evening

-   Appointment APIs
-   Tool calling
-   Backend integration testing

------------------------------------------------------------------------

## Day 2

### Morning

-   Guardrails
-   Metrics
-   Conversation summarization

### Afternoon

-   React chat UI
-   Appointment display
-   Metrics page

### Evening

-   Unit tests
-   Docker Compose
-   README
-   End-to-end testing
-   Demo preparation

------------------------------------------------------------------------

# Trade-offs

-   OpenAI SDK instead of LangChain for simplicity.
-   PostgreSQL used for persistent memory.
-   Rule-based routing with LLM fallback.
-   Minimal React frontend.
-   Lightweight metrics instead of a monitoring stack.
