# DUKAANDOST AI - TECHNICAL IMPLEMENTATION NOTE
**Internship Assignment Submission for Eko**
**Author:** AI Engineering & Systems Candidate
**Date:** November 2026
**Target Scenario:** Sharma General Store, Ranchi, Jharkhand (Sharma Ji)

---

## 1. Executive Summary

DukaanDost AI is an autonomous AI Growth Manager engineered specifically for Indian small retail (kirana) stores. Rather than serving as a passive conversational chatbot or a static dashboard, DukaanDost AI operates as an active AI Worker: it accepts a strategic business objective (*"Increase Sharma General Store's monthly net income from ₹8,000 to ₹10,000"*), independently diagnoses underlying transactional and customer records, designs an actionable roadmap, orchestrates specialized agents, enforces deterministic financial guardrails, pauses for human owner approval via stateful interrupts, and resumes seamlessly from SQLite checkpoints.

---

## 2. What Works (Implemented & Verified Functionality)

1. **Synthetic Kirana Store Financial Reconciliation:**
   - 120 synthetic customers segmented by RFM criteria (Active, Inactive, Frequent, High-Value, At-Risk) across genuine Ranchi localities (Lalpur, Doranda, Kanke Road, Harmu, etc.).
   - 32 grocery products covering FMCG, dairy, staples, snacks, and personal care.
   - 320 synthetic transactions across 30 days.
   - Real Kirana operating expenses: Rent (₹4,500), Power/Utilities (₹1,800), Transit (₹900), Store Helper Wages (₹3,000), Misc (₹800) = ₹11,000.
   - Exact mathematical reconciliation:
     $$\text{Gross Profit} = \text{Revenue (₹95,000)} - \text{COGS (₹76,000)} = \text{₹19,000}$$
     $$\text{Net Income} = \text{Gross Profit (₹19,000)} - \text{Expenses (₹11,000)} = \text{₹8,000.00 EXACTLY}$$
   - Verified that ₹8,000 is not hardcoded but calculated from individual database rows.

2. **Six Specialized AI Agents:**
   - **Business Analyst Agent:** Computes store revenue, expenses, net income, churn risks, and identifies growth pools.
   - **Strategy Planner Agent:** Translates the ₹2,000 income gap into 4 concrete initiatives (Breakfast Combo, Inactive Reactivation, Perishable Clearance, Restocking).
   - **Marketing Agent:** Structures combos (Bread + Butter Combo @ ₹109), calculates margins, and drafts localized Hindi/English customer promotion copy without sending external messages.
   - **Inventory Agent:** Detects low-stock items and near-expiry items (Sudha Paneer expiring in 3 days) to salvage inventory capital.
   - **Finance Agent:** Enforces strict deterministic margin validation. Capped discounts at 15%. Immediately halts negative-margin proposals.
   - **Supervisor Agent:** Orchestrates graph progression, manages thread checkpoints, evaluates feedback, and coordinates fault recovery.

3. **LangGraph Autonomous State & Human-in-the-Loop Interrupts:**
   - Typed state schema (`DukaandostState`) capturing execution ID, thread ID, task queues, completed/failed tasks, approval requests, and feedback.
   - Stateful execution pausing: Uses LangGraph `interrupt()` in `human_approval_node` to safely pause when an action requires owner sign-off.
   - Persistent Resumption: Uses `Command(resume={"action": "APPROVE"})` on the exact same thread to resume execution without repeating previous operations.

4. **Persistence & Thread Idempotency:**
   - Backed by `langgraph-checkpoint-sqlite` (`checkpoints.db`) and SQLite database (`dukaandost.db`).
   - Idempotency guards ensure tasks marked `COMPLETED` in the state record are skipped if re-encountered.
   - Application reboot restores in-flight threads without data loss.

5. **Failure Detection & Supervised Recovery:**
   - Reproducible scenario: Product Butter set to Cost ₹60.00 > Selling Price ₹55.00.
   - Finance Agent detects negative gross margin (-₹5.00/unit), blocks promotional launch, and Supervisor logs failure to database.
   - Store owner can adjust pricing in the UI; Supervisor revalidates and resumes workflow.

6. **Full-Stack SaaS Command Centre:**
   - Built with React 18, TypeScript, Tailwind CSS, Recharts, and Lucide React.
   - 10 full pages/views: Overview, AI Worker, Business Analytics, Growth Strategies, Approval Centre, Inventory Intelligence, Customer Insights, Execution History, Failure Monitoring, and Settings.
   - Follows dark SaaS aesthetic (#050505 background, #22D3EE cyan accents, glassmorphic navigation).

---

## 3. What Does Not Work (Intentional Non-Implementations & Boundaries)

1. **No External Message Transmission:**
   - The application does NOT integrate live SMS (Twilio) or WhatsApp Business APIs. Sending actual messages to mock phone numbers would be irresponsible and unnecessary. All campaign copy is rendered in preview cards.
2. **No Real Monetary Transactions or Payment Gateway:**
   - The system does NOT integrate Razorpay/Stripe live keys. Procurement and sales are simulated in the deterministic business simulation engine.
3. **No LLM Fine-Tuning or Model Weight Updates:**
   - The feedback loop is execution-level (variance calculation and task reprioritization), not neural network gradient descent. We do not claim model weight adaptation.
4. **No Direct Production ERP Write Access:**
   - Simulated store database modifications are sandboxed to `dukaandost.db`.

---

## 4. Evaluation Methodology

The system was evaluated using 21 automated end-to-end and unit tests via Pytest (`backend/tests/test_dukaandost.py`):
1. **Financial Baseline Test:** Verified that Revenue - COGS - Expenses == ₹8,000.00.
2. **Strategy Generation Test:** Verified Strategy Planner produces valid tasks totaling > ₹2,000.00.
3. **Marketing Agent Analysis Test:** Verified combo proposition, pricing, and campaign copy generation.
4. **Inventory Agent Detection Test:** Verified detection of low-stock and near-expiry catalog items.
5. **Negative Margin Guardrail Test:** Verified Finance Agent blocks offers when cost exceeds proposed price.
6. **Supervisor Coordination Test:** Verified task dispatch across specialized sub-agents.
7. **Human Interrupt Test:** Verified `interrupt()` halts graph execution for human owner approval.
8. **Approval Resumption Test:** Verified `Command(resume=...)` resumes execution on the same thread.
9. **Rejection Safeguard Test:** Verified rejected tasks are aborted and prevented from executing.
10. **Persistence & Recovery Test:** Verified SQLite checkpoint state retrieval after process restart.
11. **Execution Idempotency Test:** Verified completed tasks within an execution cannot be duplicated.
12. **Supervised Fault Recovery Test:** Verified price correction allows workflow revalidation.
13. **Feedback Variance Test:** Verified calculation of execution variance and priority adjustments.
14. **Dashboard Data Retrieval Test:** Verified API endpoints return database records.
15. **Financial Reconciliation Test:** Verified underlying synthetic records reconcile mathematically to ₹8,000.00.
16. **External Action Safety Test:** Confirmed zero external payment/SMS environment variables.
17. **Approval History Retrieval Test:** Verified historical decisions persist with decision timestamps.
18. **Failure Resolution Endpoints Test:** Verified failure records can be resolved individually and globally.
19. **Strict Pydantic Input Validation Test:** Verified rejection of negative or zero prices via field validators.
20. **Thread Idempotency & Income Guardrail Test:** Verified metric updates ignore already-completed tasks to prevent duplicate profit crediting.
21. **System Evaluation Metrics Test:** Verified calculation of completion rate, failure rate, approval rate, and profit variance.

**Result:** All 21 automated tests passed in 1.67s with 0 errors and 0 warnings.

---

## 5. Key Architectural Decisions

| Decision | Rationale |
| :--- | :--- |
| **Deterministic Local Mode as Default** | Avoids fragile dependence on paid LLM APIs. Allows evaluators and reviewers to run the system 100% offline with zero API key configuration. |
| **Separation of Baseline vs Simulated** | Guarantees ethical AI principles: UI clearly distinguishes actual baseline data (₹8,000) from simulated outcomes (₹10,058). |
| **Deterministic Financial Validation** | Financial calculations (margins, discounts, net profit) are performed via deterministic Python arithmetic, never delegated to LLM prompt generation where hallucinations can cause severe business damage. |
| **SQLite Checkpointing with LangGraph** | Ensures persistent state survives process crashes and application restarts. Allows human approvals to remain pending indefinitely. |
| **Single-Page Application with 10 Deep Views** | Provides a comprehensive enterprise command centre rather than a toy chatbot prompt window. |

---

## 6. What Could Be Improved in Future Iterations

1. **Multi-Store Franchising:** Support multiple Kirana branches with cross-store supplier negotiation.
2. **Voice-First Kirana Interface:** Speech-to-text in Hindi and regional dialects (Bhojpuri, Khortha) for store owners who prefer voice over typing.
3. **Barcode Scanner / POS Hardware Integration:** Direct hook into optical barcode scanners for physical inventory check-in.
4. **Time-Series Footfall Forecasting:** ARIMA / Prophet seasonal models for festival surges (Diwali, Chhath Puja, Eid).
