# DukaanDost AI
### Autonomous AI Growth Manager for Small Retail Businesses
> *"Your AI Business Partner That Doesn't Just Advise. It Takes Action."*

Developed as a technical assignment for the **Eko AI Engineering Internship**.

---

## 1. Project Overview

**DukaanDost AI** is a production-grade, multi-tenant autonomous AI business management platform engineered for Indian kirana store owners (demonstrated with **Sharma General Store**, Ranchi, Jharkhand, owned by **Sharma Ji**).

Unlike passive chatbots that generate generic conversational advice, DukaanDost AI operates as an **Autonomous AI Worker**:
- **Understands High-Level Goals:** Ingests objectives such as *"Increase monthly net income from ₹8,000 to ₹10,000 by identifying business opportunities, optimizing inventory, and reducing avoidable expenses."*
- **Decomposes & Plans Independently:** Automatically analyzes baseline records and generates concrete, prioritized initiatives.
- **Coordinates Specialized Agents:** Orchestrates 6 agents with distinct responsibilities (Business Analyst, Strategy Planner, Marketing Agent, Inventory Agent, Finance Agent, Supervisor).
- **Enforces Financial Guardrails:** Deterministic finance rules prevent negative-margin pricing and cap promotional discounts.
- **Human-in-the-Loop Oversight:** LangGraph interrupts pause thread execution on high-risk tasks until approved by store owners.
- **Resilient State Persistence:** SQLite / PostgreSQL database models and SQLite-backed LangGraph checkpoints enable seamless crash recovery.
- **Multi-Tenant Architecture:** Complete workspace segregation, JWT authentication, and Role-Based Access Control (RBAC).
- **Zero-Cost-First AI Architecture:** Operates 100% offline at **₹0 cost** using deterministic intelligence, with optional runtime integration of cloud LLMs (OpenAI, Gemini, Groq) and local open-source models (Ollama).
- **Production Observability:** Liveness/readiness probes, process telemetry, request correlation IDs, online backups, and automated CI.

---

## 2. Business Problem & Scenario

Small Indian neighbourhood kirana stores operate in intensely competitive environments with constrained capital:
- **Baseline Store:** Sharma General Store, Ranchi, Jharkhand, India.
- **Proprietor:** Sharma Ji.
- **Synthetic Records:** 120 customers, 32 products, 320 transactions, 5 recurring operating expenses.
- **Initial Monthly Financials:**
  $$\text{Revenue: } ₹95,000 \quad|\quad \text{COGS: } ₹76,000 \quad|\quad \text{Gross Profit: } ₹19,000$$
  $$\text{Operating Expenses: } ₹11,000 \quad|\quad \mathbf{Baseline\ Net\ Income:\ ₹8,000.00}$$
- **Target Monthly Income:** ₹10,000 (Required Uplift: ₹2,000 / +25.0%).

*Note: Initial business metrics are derived directly from transactional database records, not hardcoded. All growth outcomes are mathematically simulated within safe sandbox boundaries.*

---

## 3. Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 18, TypeScript 5.7, Vite 6.1, Tailwind CSS, Lucide React, Recharts, React Router DOM v6, Axios |
| **Backend** | Python 3.11+, FastAPI, LangGraph, Pydantic v2, SQLAlchemy 2.0, Alembic, Pandas, PyJWT, bcrypt, psutil |
| **Persistence** | SQLite (application data + `langgraph-checkpoint-sqlite` checkpoints) / PostgreSQL (production scaling) |
| **AI Intelligence** | Deterministic Local Engine (1.2ms, ₹0 cost), OpenAI (`gpt-4o-mini`), Google Gemini (`gemini-2.0-flash`), Groq (`llama-3.3-70b`), Ollama (`llama3`) |
| **DevOps & QA** | Docker, Docker Compose, Nginx, GitHub Actions CI, Pytest (40 tests passing in 3.89s) |

---

## 4. Multi-Agent System Architecture

```
                          [ Business Goal: ₹8k -> ₹10k ]
                                        │
                                        ▼
                             [ 1. Supervisor Agent ]
                                        │
                  ┌─────────────────────┴─────────────────────┐
                  ▼                                           ▼
        [ 2. Business Analyst ]                     [ 3. Strategy Planner ]
    (Revenue, COGS, RFM Segments)               (4 Actionable Growth Tasks)
                  │                                           │
                  └─────────────────────┬─────────────────────┘
                                        │
      ┌─────────────────────────────────┼─────────────────────────────────┐
      ▼                                 ▼                                 ▼
[ 4. Marketing Agent ]       [ 5. Inventory Agent ]             [ 6. Finance Agent ]
 - Breakfast Combo            - Low-stock detection              - Deterministic validation
 - Inactive Reactivation      - Expiry liquidation               - Blocks negative margins
 - Bilingual Kirana copy      - Restock simulation               - 15% discount cap
                                        │
                                        ▼
                         [ Human-in-the-Loop Interrupt ]
                      (LangGraph Checkpointer Pauses State)
                                        │
                         [ Approved / Rejected Decision ]
                                        │
                                        ▼
                        [ Sandbox Execution & Evaluation ]
```

---

## 5. Enterprise & Platform Features

### 5.1 Multi-Tenant Workspaces & RBAC
- Complete data isolation per store workspace (`store_id` discriminator column).
- JWT token authentication (HMAC-SHA256) with bcrypt password hashing.
- Four granular RBAC access levels: `OWNER`, `MANAGER`, `STAFF`, `VIEWER`.
- Dynamic workspace switching via dashboard header.

### 5.2 Zero-Cost First & Multi-Model AI Router
- Default execution in deterministic mode guarantees **100% uptime, 1.2ms latency, and ₹0 external cost**.
- Multi-tier fallback pipeline: `Primary Provider -> Fallback Provider -> Deterministic Engine`.
- Transparent token usage logging and cost estimation in USD and INR.
- Input sanitization against prompt injection attacks (`[FILTERED_INSTRUCTION]`).

### 5.3 External Integrations Framework
- **Google Sheets / CSV:** Live catalog preview, schema validation, negative margin detection, and atomic import.
- **Ranchi Weather Signals:** Autumn/monsoon meteorological demand advisories tailored to Jharkhand kirana buying habits.
- **WhatsApp Campaigns:** Sandboxed bilingual promotional copy generator (Hindi & English).

### 5.4 Observability, Telemetry & Health Checks
- Microsecond timing and correlation tracking (`X-Correlation-ID`, `X-Process-Time-Ms`).
- Diagnostic endpoints: `/api/health/live`, `/api/health/ready`, `/api/health/system`.
- In-memory process metrics (CPU %, RSS memory MB) and database latency probes.

### 5.5 Automated Zero-Downtime Backup & Restore
- Non-locking SQLite backups using C-level online backup API: `python scripts/backup_db.py`.
- Automated manifest creation (`backups/backup_manifest.json`) with SHA-256 hashes and table row counts.
- Pre-restore safety snapshots and verified restoration: `python scripts/restore_db.py`.

---

## 6. Dashboard Routes & Views

The frontend provides **15 dedicated pages** grouped into two operational suites:

### Core Growth Operations:
1. **Overview (`/`):** Financial health, goal progress, agent activity feed, customer segments.
2. **AI Worker (`/worker`):** Autonomous orchestration control room with live agent status.
3. **Approvals (`/approvals`):** Human-in-the-loop decision center with financial impact review.
4. **Executions (`/executions`):** Thread history and checkpoint timeline.
5. **Failures (`/failures`):** Guardrail tripwire monitoring and error resolution.
6. **Analytics (`/analytics`):** Revenue charts, expense breakdowns, and margin trends.
7. **Inventory (`/inventory`):** Stock levels, reorder thresholds, and price overrides.
8. **Customers (`/customers`):** RFM segmentation (Champions, Regulars, At-Risk, Dormant).
9. **Strategy (`/strategy`):** Decomposed initiatives and expected uplifts.
10. **Feedback (`/feedback`):** Variance reconciliation (expected vs actual simulated impact).

### Enterprise & Platform:
11. **AI Providers & Costs (`/providers`):** Model selection, connection testing, token billing ledger.
12. **Team & RBAC (`/team`):** Member role assignments and store workspace management.
13. **Integrations (`/integrations`):** Google Sheets CSV import, Weather signals, WhatsApp drafts.
14. **System Health (`/health`):** Server telemetry, database latency, and immutable audit logs.
15. **Authentication (`/login`):** Sign in, store registration, and demo session launcher.

---

## 7. Installation & Quick Start

### 7.1 Prerequisites
- Python 3.11+
- Node.js 20+ and npm

### 7.2 Local Development Setup

```bash
# 1. Clone repository
git clone https://github.com/your-org/dukaandostai.git
cd dukaandostai

# 2. Setup Python environment
python -m venv venv
# Linux / macOS:
source venv/bin/activate
# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# 3. Install backend dependencies
pip install -r backend/requirements.txt

# 4. Initialize database schema & seed initial tenant
python -c "from app.database.connection import init_db; init_db()"

# 5. Start FastAPI Backend (Port 8000)
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

In a second terminal:
```bash
# 6. Install frontend dependencies & start Vite dev server (Port 5173)
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Open your browser at **`http://localhost:5173`**.

### 7.3 Containerized Startup (Docker Compose)
```bash
# Start backend and frontend containers
docker-compose up -d --build

# Inspect status
docker-compose ps
```

---

## 8. Automated Testing & Verification

Run the full **40-test automated verification suite**:
```bash
$env:PYTHONPATH="backend"
pytest backend/tests/ -v
```

### Test Suite Distribution:
- **`test_dukaandost.py` (21 tests):** Baseline calculation, LangGraph planning, agent isolation, approval interrupts, checkpoint restoration, duplicate prevention, and financial reconciliation.
- **`test_auth_multitenancy.py` (9 tests):** Registration, duplicate email rejection, JWT login, profile extraction, token refresh, store creation, RBAC assignments, and cross-tenant data isolation.
- **`test_ai_providers_integrations.py` (10 tests):** Zero-cost registry, deterministic execution, prompt sanitization, AIRouter failover, CSV parsing & negative margin validation, weather signals, WhatsApp drafts, and telemetry endpoints.

```
============================= 40 passed in 3.89s ==============================
```

Frontend production build verification:
```bash
cd frontend
npm run build
# Output: 2,086 modules transformed, dist/ built with 0 errors.
```

---

## 9. Pre-Configured Demo Credentials

For immediate evaluation without manual sign-up:
- **Email:** `owner@sharmastore.com`
- **Password:** `SharmaStore2026!`
- **Store Name:** Sharma General Store (`STORE_001`)
- **Location:** Ranchi, Jharkhand
- **Role:** `OWNER`

---

## 10. Documentation Index

Comprehensive engineering documents are located in [`docs/`](file:///c:/Users/krish/OneDrive/Desktop/dukaandostai/docs/):
- [`docs/SYSTEM_ARCHITECTURE.md`](file:///c:/Users/krish/OneDrive/Desktop/dukaandostai/docs/SYSTEM_ARCHITECTURE.md) — Multi-tier system architecture, graph states, and data flow.
- [`docs/AUTHENTICATION.md`](file:///c:/Users/krish/OneDrive/Desktop/dukaandostai/docs/AUTHENTICATION.md) — JWT tokens, multi-tenant tenancy model, and RBAC matrix.
- [`docs/AI_PROVIDER_SETUP.md`](file:///c:/Users/krish/OneDrive/Desktop/dukaandostai/docs/AI_PROVIDER_SETUP.md) — Zero-cost setup, model registry, prompt sanitization, and fallback rules.
- [`docs/DATABASE_GUIDE.md`](file:///c:/Users/krish/OneDrive/Desktop/dukaandostai/docs/DATABASE_GUIDE.md) — Relational schema, Alembic migrations, and SQLite/PostgreSQL setup.
- [`docs/SECURITY.md`](file:///c:/Users/krish/OneDrive/Desktop/dukaandostai/docs/SECURITY.md) — Threat mitigation, prompt injection defense, and security checklist.
- [`docs/PRIVACY.md`](file:///c:/Users/krish/OneDrive/Desktop/dukaandostai/docs/PRIVACY.md) — Synthetic data declaration, customer PII protection, and sandboxed messaging.
- [`docs/DEPLOYMENT.md`](file:///c:/Users/krish/OneDrive/Desktop/dukaandostai/docs/DEPLOYMENT.md) — Bare-metal, Docker, and environment variable references.
- [`docs/BACKUP_AND_RECOVERY.md`](file:///c:/Users/krish/OneDrive/Desktop/dukaandostai/docs/BACKUP_AND_RECOVERY.md) — Online SQLite backups, manifest generation, and restore verification.
- [`docs/TROUBLESHOOTING.md`](file:///c:/Users/krish/OneDrive/Desktop/dukaandostai/docs/TROUBLESHOOTING.md) — Diagnostics for ports, locks, migrations, and provider failover.
- [`docs/PRODUCTION_READINESS.md`](file:///c:/Users/krish/OneDrive/Desktop/dukaandostai/docs/PRODUCTION_READINESS.md) — Final Phase Q verification scorecard.
- [`docs/DEMO_SCRIPT.md`](file:///c:/Users/krish/OneDrive/Desktop/dukaandostai/docs/DEMO_SCRIPT.md) — Step-by-step 5-7 minute demonstration guide for evaluators.

---

## 11. License & Attribution

Developed for the **Eko AI Engineering Internship Technical Assignment**.  
Licensed under the **MIT License**.
