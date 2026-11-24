# DukaanDost AI - Security & Threat Mitigation Policy

## 1. Zero-Cost & Credential Protection

- **No Hardcoded Secrets:** Application secrets (JWT secret key, database credentials, optional provider API keys) are managed strictly via environment variables (`.env`) and encrypted database fields.
- **Git Hygiene:** `.env`, `*.db`, `checkpoints.db`, and `backups/` are strictly excluded from source control via `.gitignore`.
- **Zero Financial Risk:** The default execution mode enforces ₹0 spend. The system cannot initiate paid API calls without an explicit user-supplied API key and store-level authorization.

---

## 2. Threat Modeling & Defensive Controls

### 2.1 SQL Injection Defense
- All database operations utilize SQLAlchemy 2.0 ORM query builders and parameterized statements.
- Dynamic table queries avoid raw string formatting or unsafe SQL interpolation.

### 2.2 Prompt Injection Defense
- Untrusted user and customer data (e.g., customer names from WhatsApp lists, custom inventory descriptions) pass through `PromptManager.sanitize_untrusted_input()` before entering LLM system prompts.
- Prohibited patterns (`ignore previous instructions`, `developer mode`, `system prompt override`) are intercepted and neutralized.

### 2.3 Cross-Tenant Data Leakage Prevention
- Every tenant query is scoped to `store_id`.
- The `require_store_access` dependency cross-references the requesting user's JWT identity against store membership tables before executing any store-specific business logic.
- Automated tests (`test_auth_multitenancy.py::test_09_multi_tenant_data_isolation`) continually verify that Tenant A cannot query Tenant B's catalog or financials.

### 2.4 Autonomous Action Safety Boundaries
The agentic system does not have unfettered authority:
- **Finance Agent Margin Floor:** Automatically aborts any pricing strategy that reduces gross margin below 5%.
- **Human Approval Gate:** High-risk tasks (product price modifications, promotional campaign triggers) trigger LangGraph `interrupt()`, suspending workflow state until a store Owner or Manager approves the proposed action via the dashboard.
- **Sandboxed Messaging:** All WhatsApp / SMS promotional messages are generated strictly as drafts. No automated external message dispatch occurs without explicit human dispatch.

---

## 3. Observability & Audit Traceability

- **Correlation Tracking:** The `ObservabilityMiddleware` injects a unique UUID `X-Correlation-ID` header into every HTTP request and response cycle, linking frontend user actions to backend agent graph traces.
- **Audit Logging:** Every critical system event (initiating growth runs, approvals, rejections, catalog imports, price edits) writes an immutable record to the `audit_logs` database table.

---

## 4. Security Verification Checklist

- [x] Passwords hashed using standard `bcrypt` with salt rounds >= 12.
- [x] JWT access tokens signed with HMAC-SHA256 (`HS256`) and enforced expiration.
- [x] Security headers enabled in Nginx: `X-Frame-Options: SAMEORIGIN`, `X-Content-Type-Options: nosniff`.
- [x] Pydantic models validate all incoming API payloads.
- [x] All 40 unit and integration tests passing in CI without security warnings.
