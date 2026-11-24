# DukaanDost AI - System Architecture Document

## 1. Executive Overview

**DukaanDost AI** ("Your AI Business Partner That Doesn't Just Advise. It Takes Action.") is an autonomous AI growth manager engineered specifically for Indian kirana store owners (demonstrated with Sharma General Store, Ranchi, Jharkhand).

The platform transforms passive business advice into verifiable autonomous business action by combining a multi-agent orchestration graph (LangGraph), multi-tenant enterprise isolation, zero-cost deterministic intelligence with optional cloud LLM providers, and strict human-in-the-loop oversight.

---

## 2. High-Level Multi-Tier System Diagram

```
+-----------------------------------------------------------------------------------+
|                            PRESENTATION TIER (SPA)                                |
|  React 18 + TypeScript + Vite + Tailwind CSS + Lucide React + Recharts           |
|                                                                                   |
|  - Growth Overview & Goals               - AI Provider & Cost Center             |
|  - 6 Specialized Agent Views             - External Integrations (Sheets/WhatsApp)|
|  - Interactive Human Approvals Modal     - System Telemetry & Health Dashboard    |
|  - Multi-Tenant Store & Team Switcher    - Persistent Execution & Audit Trail     |
+------------------------------------------+----------------------------------------+
                                           | Bearer JWT + X-Store-Id + Correlation ID
                                           v
+-----------------------------------------------------------------------------------+
|                          APPLICATION TIER (FastAPI)                               |
|                                                                                   |
|  +------------------------+  +--------------------------+  +-------------------+  |
|  | Authentication & RBAC  |  | Observability Middleware |  | Tenant Context    |  |
|  | (Owner/Manager/Viewer) |  | (Timing, Correlation ID)|  | Resolver          |  |
|  +------------------------+  +--------------------------+  +-------------------+  |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  |                          AGENTIC ORCHESTRATION                              |  |
|  |                                                                             |  |
|  |                           +---------------------+                           |  |
|  |                           |  Supervisor Agent   |                           |  |
|  |                           +----------+----------+                           |  |
|  |                                      |                                      |  |
|  |             +------------+-----------+-----------+------------+             |  |
|  |             |            |                       |            |             |  |
|  |             v            v                       v            v             |  |
|  |        +---------+  +---------+             +---------+  +---------+        |  |
|  |        |Business |  |Strategy |             |Marketing|  |Inventory|        |  |
|  |        | Analyst |  | Planner |             |  Agent  |  |  Agent  |        |  |
|  |        +---------+  +---------+             +---------+  +---------+        |  |
|  |                          |                       |            |             |  |
|  |                          +-----------+-----------+------------+             |  |
|  |                                      v                                      |  |
|  |                            +--------------------+                           |  |
|  |                            |   Finance Agent    |                           |  |
|  |                            | (Margin Guardian)  |                           |  |
|  |                            +---------+----------+                           |  |
|  |                                      |                                      |  |
|  |              [Low Risk Task]         v         [High Risk Task]             |  |
|  |             +----------------------------------------------------+          |  |
|  |             |             HUMAN APPROVAL INTERRUPT               |          |  |
|  |             |       (LangGraph Checkpointer Pauses Execution)    |          |  |
|  |             +----------------------------------------------------+          |  |
|  |                                      |                                      |  |
|  |                          Approved / Rejected Decision                       |  |
|  |                                      v                                      |  |
|  |                            +--------------------+                           |  |
|  |                            | Execution Service  |                           |  |
|  |                            | (Sandbox Executor) |                           |  |
|  |                            +---------+----------+                           |  |
|  |                                      v                                      |  |
|  |                            +--------------------+                           |  |
|  |                            | Evaluation Service |                           |  |
|  |                            | (Expected vs Actual|                           |  |
|  |                            +--------------------+                           |  |
|  +-----------------------------------------------------------------------------+  |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  |                           AI ROUTER SUBSYSTEM                               |  |
|  |  Primary Provider  --->  Fallback Provider  --->  Deterministic Offline     |  |
|  |  (OpenAI / Gemini / Groq / Ollama)                 (₹0 Cost, 1.2ms Latency) |  |
|  +-----------------------------------------------------------------------------+  |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                             DATA & PERSISTENCE TIER                               |
|                                                                                   |
|  +-----------------------------------------+  +--------------------------------+  |
|  |        Application Database             |  |    LangGraph Checkpoints       |  |
|  |  (SQLite / PostgreSQL Multi-Tenant)     |  |    (checkpoints.db)            |  |
|  |  - users, stores, store_members         |  |    - Thread Execution States   |  |
|  |  - customers, products, transactions    |  |    - Pause / Resume Memory     |  |
|  |  - tasks, approvals, audit_logs        |  |    - Replan Snapshots          |  |
|  +-----------------------------------------+  +--------------------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## 3. Core Subsystems

### 3.1 LangGraph Multi-Agent Workflow
The workflow is compiled as a stateful graph using LangGraph:
- **`analyst`**: Evaluates baseline revenues (₹95,000), expenses (₹11,000), and baseline net income (₹8,000) against the ₹10,000 target.
- **`planner`**: Identifies revenue/cost gaps and formulates 4 initiatives: Breakfast Combo, Customer Reactivation, Expiry Clearance, and Supplier Consolidation.
- **`supervisor`**: Prioritizes initiatives by ROI, schedules tasks, and coordinates specialist execution.
- **`finance`**: Enforces margin floor rules (e.g. rejects discounts if gross margin falls below 5%).
- **`approval`**: Checks task risk level. Tasks with high risk (price changes, campaign budgets > ₹500) trigger an `interrupt` pausing thread state.
- **`executor`**: Executes approved actions and rejects non-permitted actions.
- **`evaluator`**: Measures actual simulated financial uplift against expected uplift and feeds adjustments into future replanning cycles.

### 3.2 State Machine Transitions
```
[IDLE] 
  --> [ANALYZING] (Business Analyst)
  --> [PLANNING] (Strategy Planner)
  --> [COORDINATING] (Supervisor)
  --> [VALIDATING] (Finance Agent)
        |
        +---> If High Risk: [AWAITING_APPROVAL] (Workflow Suspended in Checkpointer)
        |          |
        |          +---> Approved: [EXECUTING]
        |          +---> Rejected: [ABORTED_SAFELY]
        |
        +---> If Low Risk: [EXECUTING]
  --> [UPDATING_METRICS] (Financial Ledger Update)
  --> [EVALUATING] (Variance Analysis)
  --> [COMPLETED]
```

### 3.3 Multi-Tenant Workspace Architecture
Every business record (`products`, `customers`, `transactions`, `expenses`, `tasks`, `approvals`, `audit_logs`) is bound by foreign key to `store_id`. API queries are tenant-scoped via the `X-Store-Id` header and authenticated through JWT store membership claims.
