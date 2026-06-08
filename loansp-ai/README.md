# LoanSP AI - Vietnamese Loan Consultation Chatbot

An AI-powered loan consultation chatbot built for the Vietnamese market, featuring multi-agent orchestration with LangGraph, MCP (Model Context Protocol) tool integration, and Redis-backed session memory.

## Features

- **Loan Product Recommendations**: Suggests the best loan products from 6 major Vietnamese banks (VIB, Techcombank, Vietcombank, ACB, VPBank, BIDV, MB Bank) based on customer profile (income, purpose, amount, term, asset value)
- **FAQ & Policy Search**: Answers common loan questions and searches bank policies using fuzzy + keyword matching
- **Financial Analysis**:
  - DTI (Debt-to-Income) calculation with eligibility assessment
  - LTV (Loan-to-Value) calculation with eligibility assessment
  - Monthly payment estimation with amortization schedule
  - Product comparison by total interest and monthly payment
- **Multi-turn Conversation**: Redis-backed session memory with profile extraction, conversation history, and active task tracking
- **Multi-task Support**: Handles complex queries combining multiple intents (e.g., "show me loan packages and tell me the interest policy")
- **Natural Language Responses**: LLM synthesizes multi-tool results into coherent, natural Vietnamese replies
- **Bilingual Support**: Question bank in Vietnamese and English
- **Graceful Fallback**: Local fallback implementations when MCP servers are unreachable

## Architecture

```
┌─────────┐      POST /chat      ┌──────────┐
│  User   │ ───────────────────> │ FastAPI  │
│ (HTML)  │ <─────────────────── │ Backend  │
└─────────┘                      └────┬─────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
              ┌─────▼─────┐   ┌────▼────┐   ┌────────▼────────┐
              │  Redis    │   │  LLM    │   │  MCP Client     │
              │ (Memory)  │   │ (Groq)  │   │ (SSE over HTTP) │
              └───────────┘   └─────────┘   └────────┬────────┘
                                                     │
                          ┌──────────┬───────────────┼───────────────┐
                          │          │               │               │
                    ┌─────▼─────┐ ┌─▼────────┐ ┌────▼─────┐ ┌──────▼──────┐
                    │loan_calc  │ │ product  │ │knowledge │ │loan_mcp   │
                    │_mcp_server│ │_mcp_server│ │_mcp_server│ │(legacy)   │
                    │:8000      │ │:8000     │ │:8000     │ │(empty)    │
                    └───────────┘ └──────────┘ └──────────┘ └─────────────┘
```

### Agent Workflow (LangGraph)

1. **load_memory** - Loads customer profile & active task from Redis
2. **extract_profile** - Extracts structured loan info (income, asset, amount, purpose, etc.) from user message
3. **intent_classifier** - Classifies intent: `loan_recommendation`, `loan_analysis`, `faq`, `general`
4. **planner** - Decomposes intent into executable tasks (e.g., `recommend_loan`, `calculate_dti`, `faq_search`)
5. **validator** - Checks if profile has required fields for each task
6. **ask_missing** (conditional) - Asks user for missing required fields in Vietnamese
7. **executor** - Calls MCP servers or falls back to local implementations
8. **clear_task** - Clears active task and ends the workflow

### MCP Servers

| Server | Tools | Default URL |
|--------|-------|-------------|
| `loan_calc_mcp` | `calculate_dti`, `calculate_ltv`, `estimate_payment` | `http://localhost:8001/sse` |
| `product_mcp` | `recommend_loan`, `compare_products` | `http://localhost:8002/sse` |
| `knowledge_mcp` | `faq_search`, `policy_search` | `http://localhost:8003/sse` |

## Tech Stack

- **Python 3.10**
- **FastAPI** + Uvicorn
- **LangGraph** 0.1.19 (stateful agent workflow)
- **LangChain** 0.2.17 (LLM orchestration)
- **Groq API** (`llama-3.3-70b-versatile`)
- **MCP** 1.2.0 (Model Context Protocol via SSE)
- **Redis** 8.0.0 (async session storage)
- **Pydantic** v2
- **Structlog** (structured JSON logging)
- **Docker** + **Kubernetes**
- **Pytest** (testing)

## Project Structure

```
loansp-ai/
├── backend/                    # FastAPI backend (main orchestrator)
│   ├── app/
│   │   ├── main.py             # FastAPI app, lifespan, service wiring
│   │   ├── api/
│   │   │   ├── chat.py         # POST /chat endpoint
│   │   │   ├── health_check.py # GET /health endpoint
│   │   │   └── web_html.py     # Static HTML frontend
│   │   ├── langgraph/
│   │   │   ├── workflow.py     # StateGraph definition
│   │   │   ├── node.py         # 9 graph node implementations
│   │   │   └── ai_service.py   # LLM chain wrappers
│   │   ├── planner/
│   │   │   ├── planner_service.py
│   │   │   ├── intent_planner.py
│   │   │   └── task_planner.py
│   │   ├── validator/
│   │   │   ├── validation_service.py
│   │   │   └── validator.py
│   │   ├── executor/
│   │   │   ├── executor_service.py
│   │   │   ├── task_executor.py
│   │   │   └── result_builder.py
│   │   ├── memory/
│   │   │   ├── memory_service.py
│   │   │   ├── profile_memory.py
│   │   │   └── redis_client.py
│   │   ├── MCP/
│   │   │   └── mcp_client.py   # Async SSE MCP client
│   │   └── schemas/
│   │       └── chat_schema.py
│   ├── src/
│   │   └── index.html          # Bootstrap/jQuery chat UI
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
│
├── loan_calc_mcp_server/       # MCP: DTI, LTV, Payment calculations
│   ├── server.py
│   └── tools/
│       ├── dti_calc.py
│       ├── ltv_calc.py
│       └── payment_calc.py
│
├── product_mcp_server/         # MCP: Product recommendation (28 products)
│   ├── server.py
│   ├── data/products.json
│   └── tools/
│       └── recommend.py
│
├── knowledge_mcp_server/       # MCP: FAQ & Policy search
│   ├── server.py
│   └── tools/
│       ├── faq_search.py
│       └── policy_search.py
│
├── k8s/                        # Kubernetes manifests
│   ├── backend.yaml
│   ├── redis.yaml
│   ├── loan-calc-mcp.yaml
│   ├── product-mcp.yaml
│   └── knowledge-mcp.yaml
│
└── test/                       # Pytest test suite
    ├── conftest.py
    ├── test_chat.py
    ├── test_planner.py
    └── test_validator.py
```

## Getting Started

### Prerequisites

- Python 3.10+
- Redis (local or Docker)
- Groq API key (starts with `gsk_`)

### 1. Environment Setup

Create a `.env` file in the project root:

```ini
GROQ_API=gsk_your_groq_api_key_here
REDIS_HOST=localhost
REDIS_PORT=6379
LOAN_CALC_MCP_URL=http://localhost:8001/sse
PRODUCT_MCP_URL=http://localhost:8002/sse
KNOWLEDGE_MCP_URL=http://localhost:8003/sse
ENVIRONMENT=development
```

### 2. Start Redis

```bash
docker run -d -p 6379:6379 redis:7-alpine
```

### 3. Start MCP Servers

Terminal 1:
```bash
cd loan_calc_mcp_server
pip install -r requirements.txt
python server.py
```

Terminal 2:
```bash
cd product_mcp_server
pip install -r requirements.txt
python server.py
```

Terminal 3:
```bash
cd knowledge_mcp_server
pip install -r requirements.txt
python server.py
```

### 4. Start Backend

```bash
cd backend
pip install -r requirements.txt
python app/main.py
```

Or with uvicorn:
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Access the Chat UI

Open `http://localhost:8000` in your browser.

## Docker Deployment

### Backend Only

```bash
cd backend
docker-compose up --build
```

### All Services (Manual)

```bash
# Start Redis
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Build and run MCP servers
docker build -t loan-calc-mcp ./loan_calc_mcp_server
docker run -d -p 8001:8000 --name loan-calc-mcp loan-calc-mcp

docker build -t product-mcp ./product_mcp_server
docker run -d -p 8002:8000 --name product-mcp product-mcp

docker build -t knowledge-mcp ./knowledge_mcp_server
docker run -d -p 8003:8000 --name knowledge-mcp knowledge-mcp

# Build and run backend
docker build -t loansp-backend ./backend
docker run -d -p 8000:8000 --env-file .env --name loansp-backend loansp-backend
```

## Kubernetes Deployment

Apply all manifests:

```bash
kubectl apply -f k8s/
```

Create the required secret for Groq API:

```bash
kubectl create secret generic backend-secret \
  --from-literal=GROQ_API=gsk_your_key_here
```

Check pod status:

```bash
kubectl get pods
kubectl logs -f deployment/backend
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Chat UI (index.html) |
| `POST` | `/chat` | Main chat endpoint |
| `GET` | `/health` | Health check |

### Chat Request

```json
POST /chat
{
  "message": "Tôi muốn vay mua nhà, thu nhập 20 triệu/tháng",
  "thread_id": "user-session-123"
}
```

### Chat Response

```json
{
  "response": "Dựa trên thu nhập 20 triệu/tháng của bạn, gói vay phù hợp nhất là Techcombank Home Loan với lãi suất 6.2%/năm..."
}
```

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GROQ_API` | Groq API key (starts with `gsk_`) | Yes | — |
| `REDIS_HOST` | Redis server hostname | No | `localhost` |
| `REDIS_PORT` | Redis server port | No | `6379` |
| `LOAN_CALC_MCP_URL` | Loan calc MCP SSE endpoint | No | `http://localhost:8001/sse` |
| `PRODUCT_MCP_URL` | Product MCP SSE endpoint | No | `http://localhost:8002/sse` |
| `KNOWLEDGE_MCP_URL` | Knowledge MCP SSE endpoint | No | `http://localhost:8003/sse` |
| `ENVIRONMENT` | Runtime environment | No | `production` |
| `CI` | CI flag (skips API key validation if set) | No | — |

## Testing

```bash
cd backend
pytest ../test/ -v
```

## Loan Product Database

The system includes 28 loan products from 6 Vietnamese banks:

| Bank | Home Loan | Car Loan | Consumer Loan | Business Loan |
|------|-----------|----------|---------------|---------------|
| VIB | 6.5% | 7.5% | 10.0% | 8.0% |
| Techcombank | 6.2% | 6.8% | — | 7.5% |
| Vietcombank | 6.0% | 7.0% | 9.5% | 7.2% |
| ACB | 6.8% | 7.8% | 10.5% | — |
| VPBank | 6.3% | 7.2% | — | 7.8% |
| BIDV | 6.1% | 7.0% | — | 7.5% |
| MB Bank | 6.4% | 7.3% | 10.0% | 7.9% |

## Notes

- The `loan_mcp_server/` directory is a legacy placeholder and currently empty
- The `knowledge_mcp_server/services/` directory contains empty files for future embedding/milvus/rerank integration
- The frontend currently hardcodes `thread_id: "default_thread_id"` — multi-session UI tracking is not yet implemented
- When `ENVIRONMENT` is set to `development` or `test` (or `CI` env is set), the Groq API key validation is skipped for CI/CD pipelines

## License

Private - Internal use only
