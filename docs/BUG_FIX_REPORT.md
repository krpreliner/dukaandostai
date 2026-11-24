# DUKAANDOST AI 2.0 — BUG FIX AND REPAIR REPORT
## Detailed Catalog of Discovered Bugs, Root Causes, and Engineering Resolutions

**Date:** November 25, 2026  
**Auditor:** Principal Software & Security Engineer  

---

### Bug 1: Demo Failure Button Did Not Persist Failure Records or Execute Finance Agent Validation
- **Subsystem:** Failure Monitoring (`backend/app/api/routes/demo.py`, `frontend/src/pages/FailureMonitoring.tsx`)
- **Severity:** High
- **Root Cause:**
  The `/api/demo/trigger-failure` endpoint merely set `butter.cost_price = 60.0` and `butter.selling_price = 55.0` on the `Product` table in memory, but did not execute Finance Agent deterministic validation, did not persist a `FailureRecord`, did not create an `ExecutionRecord`, and did not record an `AuditLog`. Consequently, when a user clicked "Demo Failure", the Failure Monitoring page table remained in the empty state ("No Logged Failures").
- **Fix Implemented:**
  1. Updated `/api/demo/trigger-failure` to invoke `FinanceAgent.validate_task_finance()`.
  2. Created and persisted `FailureRecord` with task ID, error description, root cause, and recovery status `UNRESOLVED`.
  3. Added idempotency controls: if an unresolved failure for the Butter scenario already exists, it updates timestamps and retries instead of creating duplicate clutter.
  4. Created an immutable `AuditLog` event (`FINANCIAL_GUARDRAIL_VIOLATION`).
  5. Updated frontend `App.tsx` to automatically route to `/failures` upon clicking "Demo Failure".

---

### Bug 2: Missing Price Rectification & Revalidation API Endpoint
- **Subsystem:** Safety Guardrails (`backend/app/api/routes/executions.py`, `frontend/src/services/api.ts`)
- **Severity:** High
- **Root Cause:**
  There was no dedicated API endpoint to rectify product prices, re-validate margins deterministically, emit audit records, and mark failures as resolved in a single atomic transaction. The frontend had a hardcoded call to set Amul Butter to ₹245/₹275.
- **Fix Implemented:**
  1. Created `POST /api/failures/{failure_id}/rectify` with payload `{ product_id, new_cost_price, new_selling_price }`.
  2. Enforced deterministic arithmetic: selling price must strictly exceed cost price and yield at least +5.0% gross margin.
  3. Atomically updated `Product` status to `HEALTHY`, failure record to `RESOLVED`, and emitted `PRICE_RECTIFICATION_VALIDATED` audit log.
  4. Added interactive "Rectify Price & Revalidate" modal in `FailureMonitoring.tsx` with live margin preview.

---

### Bug 3: Zero-Margin Pricing Allowed by Float Comparison
- **Subsystem:** Financial Gatekeeper (`backend/app/tools/profit_calculator.py`)
- **Severity:** Medium
- **Root Cause:**
  `ProfitCalculator.validate_pricing()` checked `if proposed_price < cost_price:`. When cost price equaled selling price (zero margin, ₹0.00 unit profit), the validation passed, violating Kirana store profitability guardrails.
- **Fix Implemented:**
  Changed condition to `if proposed_price <= cost_price:` with explicit rejection for non-positive unit margins and negative gross margins.

---

### Bug 4: Synthetic Database Reset Threw AttributeError
- **Subsystem:** Demonstration Controls (`backend/app/api/routes/demo.py`)
- **Severity:** Medium
- **Root Cause:**
  The `/api/demo/reset` endpoint attempted to call `svc.reset_synthetic_data()`, which did not exist on `BusinessService`.
- **Fix Implemented:**
  Replaced with direct invocation of `seed_database(db, force_reset=True)` and initialized baseline bootstrap audit logs (`SYSTEM_BOOTSTRAP_INITIALIZED`, `BASELINE_FINANCIALS_RECONCILED`).

---

### Bug 5: Audit Log Counter Showed Zero on Initial Clean Start
- **Subsystem:** System Health & Audits (`backend/app/memory/audit_log.py`, `backend/app/api/routes/demo.py`)
- **Severity:** Low
- **Root Cause:**
  The `AuditLogger.log()` method did not accept or store `store_id`, causing multi-tenant audit queries filtering by `X-Store-Id` to miss unassigned records. Additionally, initial store seeding lacked bootstrap audit records.
- **Fix Implemented:**
  Added explicit `store_id="STORE_001"` parameter to `AuditLogger.log()` and added bootstrap audit logs on database initialization.

---

### Bug 6: Growth Strategies Displayed Permanent "No Plan Generated" Empty State
- **Subsystem:** Autonomous Strategy Roadmap (`frontend/src/pages/GrowthStrategies.tsx`)
- **Severity:** Medium
- **Root Cause:**
  The Growth Strategies page only fetched tasks from active graph executions. If no execution had been started, it displayed a static empty screen without goal specification controls.
- **Fix Implemented:**
  1. Added Strategic Goal Input Header (Target Goal: "Increase monthly net income from ₹8,000 to ₹10,000", Target Income: ₹10,000).
  2. Displayed 4 pre-calculated autonomous growth pillars derived directly from Sharma General Store's ledger when tasks are idle.
  3. Added instant "Generate Strategies" button that triggers graph execution.

---

### Bug 7: ExecutionRecord Construction Raised Invalid Keyword Argument
- **Subsystem:** Database Models (`backend/app/database/models.py`, `backend/app/api/routes/demo.py`)
- **Severity:** High
- **Root Cause:**
  `demo.py` passed `business_goal` into `ExecutionRecord()`, which is mapped to `current_task` and `thread_id`.
- **Fix Implemented:**
  Mapped execution arguments correctly to `current_task` and `thread_id`.

---

### Bug 8: Whole Viewport Horizontal Scroll Pushed Sidebar Off-Screen
- **Subsystem:** Frontend Layout (`frontend/src/index.css`, `frontend/src/App.tsx`, `frontend/src/components/layout/Header.tsx`, `Sidebar.tsx`)
- **Severity:** High
- **Root Cause:**
  The header contained numerous badges and buttons exceeding 1400px width on smaller desktop screens. Without `overflow-x: hidden` on viewport roots, the entire layout shifted horizontally, hiding the navigation sidebar.
- **Fix Implemented:**
  Locked sidebar with `w-64 shrink-0`, set `overflow-x: hidden` on `html, body, #root`, set `h-screen w-screen overflow-hidden` on `App.tsx`, and isolated horizontal scrolling inside `Header.tsx` (`overflow-x-auto overflow-y-hidden`).
