# DUKAANDOST AI 2.0 — API & INTEGRATION REFERENCE MANUAL
## Comprehensive REST Endpoint Specification, Schemas & Security Protocols

---

### 1. Architectural Standards
- **Base URL:** `http://127.0.0.1:8000/api`
- **Protocol:** HTTP/1.1 (JSON request / response)
- **Authentication:** Bearer JWT in `Authorization: Bearer <token>`
- **Multi-Tenancy:** `X-Store-Id: <store_id>` header (default: `STORE_001`)
- **Tracing:** `X-Correlation-ID` header returned with each response
- **Performance:** `X-Process-Time-Ms` returned on all responses

---

### 2. Core API Endpoints

#### A. Authentication & User Profile (`/api/auth`)
* `POST /api/auth/register`: Register new user with email, password (Argon2), and full name.
* `POST /api/auth/login`: Authenticate and receive `access_token` and `refresh_token`.
* `GET /api/auth/me`: Retrieve currently authenticated user and store memberships.
* `POST /api/auth/refresh`: Exchange valid refresh token for a new access token.
* `POST /api/auth/stores`: Create a new isolated store workspace.

#### B. Safety Guardrails & Failure Monitoring (`/api/failures`, `/api/demo`)
* `POST /api/demo/trigger-failure`:
  - Triggers controlled Amul Butter demonstration scenario (Cost ₹60.00 > Sell ₹55.00).
  - Deterministically rejected by Finance Agent.
  - Persists `FailureRecord` (UNRESOLVED) and emits `FINANCIAL_GUARDRAIL_VIOLATION` audit log.
* `GET /api/failures`:
  - Returns list of failure records filtered by `X-Store-Id` and optional `execution_id`.
* `POST /api/failures/{failure_id}/rectify`:
  - Request body: `{ "product_id": "PROD003", "new_cost_price": 60.0, "new_selling_price": 68.0 }`.
  - Re-validates gross margin deterministically.
  - Updates product price, marks status `HEALTHY`, sets `FailureRecord` to `RESOLVED`.
  - Emits `PRICE_RECTIFICATION_VALIDATED` audit log.
* `POST /api/failures/{failure_id}/resolve`: Resolves a failure record directly.
* `POST /api/failures/resolve-all`: Resolves all active unresolved failure records for the store.
* `POST /api/demo/reset`: Resets synthetic Kirana records, executions, and re-seeds baseline data.

#### C. Autonomous Multi-Agent Worker (`/api/worker`)
* `POST /api/worker/start`:
  - Request body: `{ "target_income": 10000.0, "business_goal": "..." }`.
  - Initiates 6-agent LangGraph workflow.
  - Returns initial status (`RUNNING` or `WAITING FOR APPROVAL`).
* `GET /api/worker/status/{execution_id}`:
  - Returns live execution status, current agent, current task, and task records.

#### D. Human Approval Centre (`/api/approvals`)
* `GET /api/approvals/pending`:
  - Returns all pending actions awaiting shopkeeper sign-off.
* `GET /api/approvals/history`:
  - Returns historical log of past approval and rejection decisions.
* `POST /api/approvals/{task_id}/approve`:
  - Resumes paused LangGraph thread with `Command(resume={'action': 'APPROVE'})`.
  - Emits `HUMAN_APPROVAL_DECISION` audit log.
* `POST /api/approvals/{task_id}/reject`:
  - Halts task execution and records human rejection.

#### E. Conversational AI Assistant & Daily Briefing (`/api/assistant`, `/api/briefing`)
* `POST /api/assistant/chat`:
  - Request body: `{ "message": "Mere store mein kaun se products low stock mein hain?", "language": "hi" }`.
  - Executes deterministic backend tools and returns structured natural response.
* `GET /api/assistant/tools`:
  - Returns catalog of all 9 deterministic assistant tools.
* `GET /api/briefing/today`:
  - Returns today's synthesized business briefing comparing today vs yesterday metrics.
* `POST /api/briefing/generate`:
  - Forces real-time recalculation of store audio briefing.

#### F. Business Analytics & Intelligence (`/api/overview`, `/api/analytics`, `/api/products`, `/api/customers`)
* `GET /api/overview`: Overview KPIs, worker status, pending approval count, top products.
* `GET /api/analytics`: Reconciled revenue, COGS, gross margin, operating expenses, and net profit.
* `GET /api/products`: Catalog with cost price, selling price, current stock, and status.
* `PUT /api/products/{product_id}`: Updates price and status for a catalog product.
* `GET /api/customers`: Customers with RFM segmentation and purchase history.

#### G. System Health & Observability (`/api/health`, `/api/audit-logs`)
* `GET /api/health/live`: Liveness probe (HTTP 200).
* `GET /api/health/ready`: Readiness probe verifying database connection latency.
* `GET /api/health/system`: Detailed telemetry: database latency (ms), process memory (MB), CPU, uptime.
* `GET /api/audit-logs`: Immutable audit trail with search and limit filters.

#### H. AI Provider Router & Integrations (`/api/ai`, `/api/integrations`)
* `GET /api/ai/providers`: Registered providers (Groq, OpenAI, Gemini, Ollama, Deterministic).
* `POST /api/ai/test-connection`: Verifies API key connectivity against external LLM provider.
* `POST /api/ai/settings`: Saves primary/fallback provider routing preferences.
* `GET /api/ai/usage`: Token consumption, estimated cost, and circuit breaker status.
* `GET /api/integrations/weather/signals`: Hyperlocal weather signals for Ranchi.
* `POST /api/integrations/sheets/preview`: CSV import preview with negative price validation.
* `POST /api/integrations/whatsapp/draft`: Drafts promotional campaigns with human consent enforcement.
