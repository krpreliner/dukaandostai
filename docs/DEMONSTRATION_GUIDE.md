# DUKAANDOST AI 2.0 — LIVE DEMONSTRATION SCRIPT
## Step-by-Step Evaluator & Investor Walkthrough

**Business:** Sharma General Store, Harmu Road, Ranchi, Jharkhand  
**Proprietor:** Sharma Ji  
**Objective:** Bridge monthly net operating income from ₹8,000.00 to ₹10,000.00 (+₹2,000.00)  

---

### Step 1: Open the Application
- Open URL: `http://localhost:5173/`
- Notice the **Black (`#050505`) and Cyan (`#22D3EE`)** interface.
- Point out the **Header Status Bar**:
  - Live Store Indicator: `Sharma General Store • Harmu Road, Ranchi`
  - Bilingual Switcher: `हिंदी` / `English`
  - Worker Status: `IDLE`
  - Demo Failure Button
  - Reset Synthetic Data Button
  - AI Assistant Button
  - Start AI Worker CTA

---

### Step 2: Experience the Bilingual Daily Business Briefing
- Look at the top hero card on the **Overview** page: `Daily Business Briefing`.
- Click **"हिंदी"** to toggle language.
- Click **"Read Aloud"**.
- Listen to the browser-native speech synthesis speaking natural Hindi with correct rupee pronunciation:
  > *"नमस्ते शर्मा जी! आज आपके शर्मा जनरल स्टोर की बिक्री 3,450 रुपये रही..."*
- Test **Pause**, **Resume**, and **Stop** audio controls.

---

### Step 3: Trigger the Controlled Safety Failure (Section 3)
1. Click the red **"Demo Failure"** button in the top navigation bar.
2. The system automatically navigates to **Failure Monitoring & Safety Guardrails** (`/failures`).
3. Point out the live logged failure in the table:
   - **Task ID:** `TASK_PROMO_PROD003`
   - **Detecting Agent:** `Finance Agent`
   - **Root Cause:** `NEGATIVE_GROSS_MARGIN_VIOLATION`
   - **Error Description:** Shows Amul Butter @ Cost ₹60.00 > Sell ₹55.00 with -9.09% negative margin.
   - **Status:** `UNRESOLVED` (Red badge)
4. Click **"Details"** to inspect the full audit trail and execution reference.

---

### Step 4: Rectify Price & Deterministically Revalidate
1. Click **"Rectify Price & Revalidate"** (or click "Rectify" on the table row).
2. The **Rectify Price & Revalidate Modal** opens:
   - Target Product: `Amul Butter 500g (PROD003)`
   - Cost Price: `₹60.00`
   - Proposed Selling Price: `₹68.00`
   - Observe the live **Deterministic Margin Preview**: `+11.8%`, Unit Profit: `₹8.00/unit`.
   - Notice the green checkmark: *"✓ Verified: Proposed price satisfies financial guardrails."*
3. Click **"Confirm & Revalidate"**.
4. The modal validates the price, updates the database, emits an audit event, and marks the failure as **"RESOLVED"**!
5. In the table, the status updates to **Resolved / Rectified**.

---

### Step 5: Ask the Conversational AI Assistant
1. Click the **"AI Assistant"** button in the header.
2. Type or speak (via microphone icon):
   - *"Mere store mein kaun se products low stock mein hain?"*
   - *"Is month ka profit kitna hai?"*
   - *"Mere top selling products kaun se hain?"*
3. Observe how the assistant executes real backend tools (`get_inventory_alerts`, `get_financial_summary`) and replies with verified database numbers without hallucinating.

---

### Step 6: Review Autonomous Growth Strategies
1. Navigate to **Growth Strategies** in the sidebar.
2. Observe the **Strategic Target Goal** input bar:
   - Target Goal: `Increase monthly net income from ₹8,000 to ₹10,000`
   - Baseline: `₹8,000.00`, Target: `₹10,000.00`, Gap: `+₹2,000.00`.
3. Inspect the **4 Autonomous Growth Pillars**:
   - 1. High-Margin Breakfast & Dairy Bundle Promotion (+₹540/month)
   - 2. Emergency Stock Replenishment for High-Velocity Spices (+₹650/month)
   - 3. Dormant High-Value Customer Reactivation (+₹580/month)
   - 4. Dead-Stock Clearance for Near-Expiry Snacks (+₹230/month)
4. Click **"Launch Strategy Planner Cycle"** or **"Start AI Worker"** to execute the multi-agent orchestration.

---

### Step 7: Inspect System Health & Telemetry
1. Navigate to **System Health** in the sidebar.
2. Observe live system telemetry:
   - Database Latency: `< 2.0 ms`
   - Process Memory: `~124 MB`
   - Server Health: `HEALTHY`
3. Scroll to the **Immutable Audit Trail**:
   - Inspect logged events: `PRICE_RECTIFICATION_VALIDATED`, `FINANCIAL_GUARDRAIL_VIOLATION`, `SYSTEM_BOOTSTRAP_INITIALIZED`.
   - Use the real-time search box to filter by agent or event type.
