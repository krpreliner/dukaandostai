# DUKAANDOST AI 2.0 — FAILURE RECOVERY & GUARDRAILS SPECIFICATION
## Deterministic Safety Protocols and Fault Isolation Architecture

---

### 1. Architectural Philosophy
In small retail operating systems, autonomous AI agents must never be permitted to execute actions that violate business viability or inflict financial loss. 

DukaanDost AI enforces an independent, deterministic **Financial Gatekeeper** (the Finance Agent) that validates every action before execution or human presentation.

---

### 2. Failure Detection Flow
```
[Marketing / Inventory Agent]
          │
          ▼
   Proposes Action
 (e.g. Promotional Bundle)
          │
          ▼
[Finance Agent Gatekeeper]
          │
          ├── Cost Price > Selling Price? ────► [REJECTED: Negative Gross Margin]
          ├── Margin < 5.0%?              ────► [REJECTED: Sub-Threshold Policy]
          ├── Discount > 15.0%?           ────► [REJECTED: Discount Cap Exceeded]
          └── Product Missing in Stock?   ────► [REJECTED: Inventory Missing]
          │
          ▼
[Supervisor Agent]
          │
   Isolates Fault & Logs FailureRecord
          │
          ├── Recovery Status: UNRESOLVED
          ├── Emits Immutable AuditLog
          └── Halts Unsafe Execution
```

---

### 3. The Controlled Demonstration Scenario
- **Product:** Amul Butter 500g (`PROD003`)
- **Cost Price:** ₹60.00
- **Selling Price:** ₹55.00
- **Unit Loss:** -₹5.00/unit
- **Calculated Margin:** -9.09%
- **Violation Category:** `NEGATIVE_GROSS_MARGIN_VIOLATION`
- **Rejection Reason:** "FINANCIAL VALIDATION FAILED: Product 'Amul Butter 500g' has cost price ₹60.00 exceeding selling price ₹55.00 (Loss: -₹5.00/unit). Promotions on negative-margin products are strictly prohibited."

---

### 4. Idempotency Controls
When "Demo Failure" is clicked repeatedly:
1. The backend inspects `failure_records` for an existing record matching `task_id="TASK_PROMO_PROD003"` with `recovery_status="UNRESOLVED"`.
2. If found, it increments `retry_count` and updates `timestamp` rather than creating duplicate records.
3. The response returns `"idempotent": true`.

---

### 5. Genuine Price Rectification & Revalidation Workflow
```
[Human Store Manager]
          │
   Opens "Rectify Price & Revalidate" Modal
          │
   Inspects Cost (₹60.00) & Inputs New Sell (e.g. ₹68.00)
          │
   Frontend displays Live Margin: +11.76% (Unit Profit: ₹8.00)
          │
   Clicks "Confirm & Revalidate"
          │
          ▼
[POST /api/failures/{id}/rectify]
          │
          ├── 1. Validates strictly positive prices (> ₹0.00)
          ├── 2. Validates new_sell > new_cost (Rejects if <=)
          ├── 3. Enforces minimum 5.0% gross margin policy
          ├── 4. Updates Product record (status = "HEALTHY")
          ├── 5. Marks FailureRecord recovery_status = "RESOLVED"
          └── 6. Emits AuditLog ("PRICE_RECTIFICATION_VALIDATED")
          │
          ▼
[UI Refreshes Automatically]
Failure row displays "Rectified" badge with green indicator.
```

---

### 6. Automated Failure Tests Verification
The test suite `backend/tests/test_failure_guardrails_recovery.py` validates all 11 failure scenarios:
1. Negative margin auto-rejection.
2. Zero margin auto-rejection.
3. Positive margin verification.
4. Missing product rejection.
5. Invalid negative price rejection.
6. FailureRecord and AuditLog persistence.
7. Idempotency control on duplicate triggers.
8. Price rectification to positive margin.
9. Failed rectification rejection when still below cost.
10. Recovery state persistence in database queries.
11. Demo reset cleanup and baseline re-seeding.
