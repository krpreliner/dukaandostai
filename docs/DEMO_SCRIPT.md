# DUKAANDOST AI - 5-7 MINUTE DEMONSTRATION SCRIPT
**Project Demonstration & Video Recording Guide**
**Internship Assignment for Eko**
**Store:** Sharma General Store, Ranchi, Jharkhand (Sharma Ji)

---

## Demonstration Overview Timeline

| Time | Demonstration Segment | Key Screen / Endpoint |
| :--- | :--- | :--- |
| **0:00 - 1:00** | Introduction & Kirana Baseline Setup | Overview Page (`/`) |
| **1:00 - 2:00** | Autonomous Worker Launch & Strategic Planning | AI Worker Page (`/worker`) |
| **2:00 - 3:00** | Specialized Multi-Agent Collaboration | AI Worker & Growth Strategies (`/strategies`) |
| **3:00 - 4:00** | Human-in-the-Loop Sign-off & Resumption | Approval Centre (`/approvals`) |
| **4:00 - 5:00** | Application Restart & SQLite Thread Persistence | Terminal reboot & History (`/history`) |
| **5:00 - 6:00** | Negative-Margin Failure & Guardrail Recovery | Failure Monitoring (`/failures`) & Inventory (`/inventory`) |
| **6:00 - 7:00** | Final Reconciled Income & Technical Conclusion | Settings (`/settings`) & Overview (`/`) |

---

## Detailed Step-by-Step Script

### Minute 0:00 - 1:00 | The Kirana Challenge & Baseline Verification
**Visual:** Open browser at `http://localhost:5173/` (Overview Command Centre).
**Talking Points:**
> "Hello everyone! This is **DukaanDost AI**, an autonomous AI growth manager for small Indian retail businesses. Our tagline is: *'Your AI Business Partner That Doesn't Just Advise. It Takes Action.'*
> 
> Let's look at our business scenario: **Sharma General Store**, a neighbourhood kirana store in **Ranchi, Jharkhand**, owned by **Sharma Ji**.
> Notice the top metric cards:
> - **Monthly Net Income: ₹8,000.00**
> - **Target Monthly Net Income: ₹10,000.00**
> - **Income Gap to bridge: ₹2,000.00 (+25% growth)**
> - **Synthetic Customers: 120 customers** across Ranchi localities like Lalpur, Doranda, and Harmu.
> 
> Crucially, this ₹8,000 is **not hardcoded**. Looking at the Financial Reconciliation waterfall below:
> 320 atomic transactions generate **Revenue: ₹95,000**, **COGS: ₹76,000**, leaving **Gross Profit: ₹19,000**. Deducting **₹11,000 in Operating Expenses** (Rent ₹4,500, Electricity ₹1,800, Helper wages ₹3,000, Transit ₹900, Misc ₹800), the baseline calculates to **exactly ₹8,000.00**."

---

### Minute 1:00 - 2:00 | Launching the Autonomous AI Worker
**Visual:** Click **"AI Worker"** in the sidebar (`/worker`).
**Talking Points:**
> "Now, let's watch the worker take action. I will click the prominent **'START AI WORKER'** button.
> Notice the live status transition: **IDLE → ANALYSING → PLANNING**.
> 
> Behind the scenes, LangGraph executes the workflow:
> 1. The **Business Analyst Agent** inspects sales velocity, profit margins, and finds that 25 customers have churned and 14 packs of perishable Sudha Paneer are expiring in 3 days.
> 2. The **Strategy Planner Agent** receives these findings and constructs a prioritized growth roadmap:
>    - Launch a Breakfast Combo (Bread + Butter)
>    - Reactivate 25 Dormant Customers with staple vouchers
>    - Clear perishable Paneer before expiry
>    - Restock high-velocity daily essentials (Bread & Eggs)."

---

### Minute 2:00 - 3:00 | Specialized Multi-Agent Coordination
**Visual:** Inspect the 6 agent cards on `/worker`, then switch to **"Growth Strategies"** (`/strategies`).
**Talking Points:**
> "Let's examine how our 6 specialized agents coordinate:
> - **Marketing Agent** formulates the Bread + Butter combo: regular price ₹115 reduced to ₹109. It drafts personalized promotional copy in conversational Hindi for Sharma Ji.
> - **Inventory Agent** analyzes stock thresholds and detects that Bread and Eggs are below minimum safety stock, calculating potential stockout loss.
> - **Finance Agent** sits as an independent deterministic gatekeeper. Before any promotion can proceed, it calculates unit margin (10.09%) and confirms the discount is within the 15% ceiling.
> - **Supervisor Agent** monitors overall execution and checks risk policies."

---

### Minute 3:00 - 4:00 | Human-in-the-Loop Approval & Thread Resumption
**Visual:** Notice the worker status changes to **WAITING FOR APPROVAL**. An orange badge appears on the **Approval Centre** tab (`/approvals`). Click it.
**Talking Points:**
> "Here is our core mandatory feature: **Human-in-the-Loop Controlled Autonomy**.
> The system does not unilaterally launch pricing changes that impact margins without owner sign-off.
> In LangGraph, the execution has paused at an `interrupt()` node.
> 
> Looking at the approval card:
> - **Action:** Launch Breakfast Combo (Bread + Butter)
> - **Price:** ₹115 → ₹109 (5.2% discount)
> - **Gross Margin:** 10.09% verified positive
> - **Expected Financial Impact:** +₹440.00 incremental net profit
> 
> Let's click **APPROVE**.
> When I click approve, the backend dispatches a LangGraph `Command(resume={"action": "APPROVE"})` on the **exact same execution thread**. The worker resumes immediately, executes the simulated campaign, updates metrics, and moves to the next tasks."

---

### Minute 4:00 - 5:00 | Application Restart & SQLite Persistence Proof
**Visual:** Switch to **Execution History** (`/history`). Show terminal restart.
**Talking Points:**
> "Let's demonstrate **Persistence and Execution Continuity**.
> DukaanDost AI uses SQLite checkpointing (`checkpoints.db`).
> 
> If we stop the backend process in our terminal right now and restart it:
> `Get-WorkerStatus` restores the exact in-flight execution ID.
> The completed tasks (TASK_001, TASK_002, TASK_003) are preserved in state, and our idempotency check ensures that previously completed actions are **never executed twice**.
> There is zero duplicate revenue booking, zero double counting."

---

### Minute 5:00 - 6:00 | Reproducible Failure & Supervised Recovery
**Visual:** Click the top bar **"Demo Failure"** button, then navigate to **"Failure Monitoring"** (`/failures`).
**Talking Points:**
> "Now let's examine Section 9: **Failure Detection and Recovery**.
> I will click 'Demo Failure'. This simulates a realistic retail error:
> - Product: **Amul Butter**
> - Cost Price: **₹60.00**
> - Selling Price accidentally set to: **₹55.00**
> 
> When the Marketing Agent proposes a promotion, the **Finance Agent immediately detects a negative gross margin (-₹5.00 loss per unit)**.
> Instead of silently executing or hallucinating, the Finance Agent **blocks the promotion**.
> The Supervisor records a structured failure: `FINANCIAL_VALIDATION_FAILED: Product 'Butter' has negative gross margin`.
> 
> Now, how does recovery work?
> The store owner can navigate to **Inventory Intelligence** (`/inventory`), click **Edit** on Butter, and correct the selling price back to healthy margin (e.g., Cost ₹245, Sell ₹275).
> Clicking **'Rectify Price & Revalidate'** allows the Supervisor to re-evaluate the task. The guardrail clears, and the workflow resumes seamlessly!"

---

### Minute 6:00 - 7:00 | Final Reconciled Income & System Evaluation
**Visual:** Return to **Overview** (`/`) and **Settings** (`/settings`).
**Talking Points:**
> "Looking at our final simulated performance:
> - **Baseline Net Income:** ₹8,000.00
> - **Target Net Income:** ₹10,000.00
> - **Simulated Net Income:** **₹10,058.68**
> - **Net Income Improvement:** **+₹2,058.68 (+25.7% growth)**
> - **Milestone Status:** Target Achieved!
> 
> Navigating to **Settings**, our **System Evaluation Scorecard** shows:
> - **100% Task Completion Rate**
> - **100% Fault Recovery Rate**
> - **Zero Duplicate Executions**
> - **Deterministic Local Mode:** 100% operational offline without any paid LLM API key.
> 
> DukaanDost AI demonstrates that an autonomous AI Worker can understand business goals, respect financial boundaries, collaborate with human owners, and deliver verifiable business growth. Thank you!"
