# CONTEXT.md

## Project Name

LoanSP AI

---

# Project Overview

LoanSP AI is a fintech AI assistant focused on helping users:

- understand loan affordability
- analyze debt pressure
- simulate repayment strategies
- compare financial scenarios
- receive loan recommendations through conversational interaction

This project is designed as a production-style AI-powered financial assistant.

The system is NOT a generic AI chatbot.

The architecture follows a deterministic financial system design where:
- financial calculations are handled by backend logic
- LLM is only used as a conversational layer

---

# Phase 1 Goal

Phase 1 focuses on building a clean MVP with:

- modern chatbot UI
- persistent user chat sessions
- FastAPI backend
- Grok-powered conversation
- deterministic backend processing
- Dockerized development environment

The main purpose of Phase 1 is to establish:
- scalable architecture
- clean domain separation
- frontend/backend communication
- conversation workflow
- session persistence

---

# Product UX Direction

The application should feel like a modern fintech AI platform.

UI style:
- blue-based fintech theme
- clean conversational interface
- responsive design
- smooth chat experience
- user-friendly layout

Primary color palette:
- royal blue
- navy blue
- cyan accents
- white/light gray chat surfaces

The chatbot experience should resemble:
- modern banking assistant
- AI financial advisor
- conversational fintech platform

---

# High-Level Architecture

Frontend (React)
        ↓
FastAPI Backend
        ↓
-----------------------------------
| Conversation Service           |
| Financial Engine               |
| Recommendation Engine          |
-----------------------------------
        ↓
PostgreSQL Database

---

# System Flow

User sends message
        ↓
Frontend sends request to FastAPI
        ↓
FastAPI processes request
        ↓
Conversation module calls Grok API
        ↓
Grok response returned to backend
        ↓
Backend formats response
        ↓
Response returned to frontend
        ↓
Chat UI updates in real-time

---

# Core Engineering Philosophy

## IMPORTANT

LLM is NOT the financial brain.

LLM responsibilities:
- conversational interaction
- natural language understanding
- intent extraction
- response explanation

LLM MUST NOT:
- calculate financial formulas
- determine eligibility
- make financial decisions
- generate deterministic calculations

All financial calculations must be implemented inside backend services.

---

# Frontend Stack

- React
- Vite
- JavaScript/TypeScript
- TailwindCSS
- Axios
- Zustand (future state management)

---

# Backend Stack

- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Pytest

---

# AI Stack

- Grok API
- Prompt engineering
- Structured response generation

---

# Infrastructure Stack

- Docker
- Docker Compose

Future phases may include:
- Kubernetes
- Redis
- Celery
- Kafka
- ArgoCD
- Prometheus
- Grafana

---

# Architecture Style

The project follows:

- Modular Monolith architecture
- Microservice-ready structure
- Docker-first development
- Clean architecture principles

Even though the application is initially deployed as one backend service,
all modules must remain isolated and scalable.

---

# Frontend Responsibilities

Frontend responsibilities:
- render chatbot interface
- handle user interactions
- manage session state
- display conversation history
- communicate with backend APIs

Frontend MUST NOT:
- call Grok API directly
- contain business logic
- perform financial calculations

---

# Backend Responsibilities

Backend responsibilities:
- expose REST APIs
- manage business logic
- manage user sessions
- communicate with Grok API
- process financial calculations
- persist conversation history

---

# Conversation Module Responsibilities

Responsibilities:
- communicate with Grok API
- handle prompts
- generate conversational responses
- structure extracted information

Must NOT:
- calculate EMI
- calculate DTI
- determine loan approval
- perform recommendation scoring

---

# Financial Engine Responsibilities

Responsibilities:
- EMI calculations
- DTI calculations
- affordability estimation
- amortization calculations
- interest simulations

This is the deterministic financial core of the platform.

---

# Recommendation Engine Responsibilities

Responsibilities:
- recommendation scoring
- strategy ranking
- loan comparison
- rule-based evaluation

This module must remain deterministic and explainable.

---

# Backend Folder Structure

backend/
│
├── app/
│   │
│   ├── api/
│   │   ├── routes/
│   │   │   ├── chat.py
│   │   │   ├── loan.py
│   │   │   └── health.py
│   │   │
│   │   └── dependencies/
│   │
│   ├── modules/
│   │   │
│   │   ├── conversation/
│   │   │   ├── grok_client.py
│   │   │   ├── prompt_templates.py
│   │   │   ├── extractor.py
│   │   │   └── schemas.py
│   │   │
│   │   ├── financial_engine/
│   │   │   ├── formulas.py
│   │   │   ├── calculators.py
│   │   │   └── dti.py
│   │   │
│   │   └── recommendation/
│   │       ├── scoring.py
│   │       └── ranking.py
│   │
│   ├── services/
│   │   ├── chat_service.py
│   │   └── loan_service.py
│   │
│   ├── schemas/
│   │
│   ├── database/
│   │   ├── models/
│   │   ├── repositories/
│   │   └── session.py
│   │
│   ├── core/
│   │   ├── config/
│   │   ├── logging/
│   │   └── security/
│   │
│   ├── utils/
│   │
│   └── main.py
│
├── tests/
├── Dockerfile
└── requirements.txt

---

# Frontend Folder Structure

frontend/
│
├── public/
│
├── src/
│   │
│   ├── components/
│   │   ├── chat/
│   │   │   ├── Chatbot.jsx
│   │   │   ├── ChatInput.jsx
│   │   │   ├── ChatMessage.jsx
│   │   │   ├── ChatSidebar.jsx
│   │   │   └── TypingIndicator.jsx
│   │
│   ├── pages/
│   │   └── ChatPage.jsx
│   │
│   ├── services/
│   │   ├── api.js
│   │   └── chat.service.js
│   │
│   ├── hooks/
│   │   └── useChatbot.js
│   │
│   ├── store/
│   │
│   ├── styles/
│   │
│   ├── App.jsx
│   │
│   └── main.jsx
│
├── Dockerfile
├── package.json
└── vite.config.js

---

# Session Persistence

The system must support:
- per-user chat sessions
- persistent conversation history
- session restoration

Database relationship:

users
  └── sessions
          └── messages

Each message should contain:
- session_id
- role
- content
- timestamp

---

# API Design Principles

All APIs must follow REST conventions.

Base prefix:

/api/v1

Main endpoints:

POST /chat
POST /loan/calculate
POST /recommendation
POST /simulation

---

# Chat API Flow

Frontend sends:

{
  "session_id": "uuid",
  "message": "I want to borrow money"
}

Backend:
- validates request
- stores message
- calls Grok API
- stores response
- returns formatted output

Frontend renders:
- user message
- AI response
- loading state
- typing animation

---

# Important Engineering Rules

## Frontend

Frontend MUST NEVER:
- call Grok API directly
- expose API keys
- perform financial calculations

---

## Backend

Backend MUST:
- centralize business logic
- protect API credentials
- manage sessions
- validate requests
- isolate LLM communication

---

# Docker Philosophy

Phase 1 must run completely using Docker Compose.

Containers:

- frontend-container
- backend-container
- postgres-container

Future modules should be easy to split into independent services.

---

# Future Scalability

This architecture is intentionally designed to evolve into:

- conversation-service
- recommendation-service
- simulation-service
- notification-service

without major rewrites.

---

# Non Goals (Phase 1)

Phase 1 does NOT include:

- real bank integration
- production authentication
- credit bureau integration
- autonomous lending decisions
- Kubernetes deployment
- Redis/Celery/Kafka
- event-driven architecture
- advanced ML risk scoring

---

# Success Criteria

Phase 1 is successful if:

- chatbot UI works smoothly
- frontend communicates with backend correctly
- Grok integration works reliably
- sessions persist correctly
- Docker environment runs successfully
- architecture remains clean and modular

---

# Development Workflow

Recommended workflow:

1. Setup project structure
2. Setup Docker environment
3. Build FastAPI skeleton
4. Build React chatbot UI
5. Connect frontend to backend
6. Integrate Grok API
7. Add session persistence
8. Add financial engine
9. Add recommendation engine
10. Add testing

---

# AI Coding Assistant Rules

When generating code:

- prioritize modularity
- avoid overengineering
- keep architecture clean
- isolate business logic
- separate LLM logic from financial logic
- prefer readability over clever abstractions

This project should resemble a real fintech engineering system,
NOT a hackathon AI demo.