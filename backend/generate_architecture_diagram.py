from PIL import Image, ImageDraw, ImageFont
import os

def create_diagram():
    width = 1600
    height = 1100
    img = Image.new("RGB", (width, height), color="#080808")
    draw = ImageDraw.Draw(img)

    # Load system font
    try:
        font_title = ImageFont.truetype("arial.ttf", 26)
        font_subtitle = ImageFont.truetype("arial.ttf", 14)
        font_section = ImageFont.truetype("arialbd.ttf", 16)
        font_box_title = ImageFont.truetype("arialbd.ttf", 14)
        font_box_text = ImageFont.truetype("arial.ttf", 12)
        font_small = ImageFont.truetype("arial.ttf", 10)
    except Exception:
        font_title = ImageFont.load_default()
        font_subtitle = font_title
        font_section = font_title
        font_box_title = font_title
        font_box_text = font_title
        font_small = font_title

    # Top Header Banner
    draw.rectangle([(40, 30), (1560, 110)], fill="#111111", outline="#22D3EE", width=2)
    draw.text((60, 45), "DUKAANDOST AI - COMPLETE SYSTEM ARCHITECTURE", fill="#FFFFFF", font=font_title)
    draw.text((60, 80), "Autonomous Multi-Agent Kirana Growth Engine | LangGraph Orchestration | Human-in-the-Loop | SQLite Checkpointing", fill="#A1A1AA", font=font_subtitle)

    def draw_card(x, y, w, h, title, subtitle, items, border_color="#22D3EE", fill="#141414"):
        draw.rectangle([(x, y), (x + w, y + h)], fill=fill, outline=border_color, width=1)
        # title bar
        draw.rectangle([(x, y), (x + w, y + 32)], fill="#1A1A1A", outline=border_color, width=1)
        draw.text((x + 12, y + 8), title, fill="#FFFFFF", font=font_box_title)
        if subtitle:
            draw.text((x + 12, y + 38), subtitle, fill="#22D3EE", font=font_small)
        
        curr_y = y + 54 if subtitle else y + 40
        for item in items:
            draw.text((x + 12, curr_y), f"• {item}", fill="#D4D4D8", font=font_box_text)
            curr_y += 18

    # 1. Frontend Section (Left Top)
    draw_card(
        60, 140, 320, 200,
        "FRONTEND INTERFACE",
        "React + TypeScript + Vite + Tailwind CSS",
        [
            "Overview Command Centre",
            "AI Worker Live Control Matrix",
            "Business Analytics (Recharts)",
            "Growth Strategy Visualizer",
            "Approval Centre (Approve / Reject)",
            "Inventory & Customer Intelligence",
            "Failure Monitoring & System Settings"
        ],
        border_color="#404040"
    )

    # 2. FastAPI Backend API (Left Middle)
    draw_card(
        60, 370, 320, 190,
        "FASTAPI BACKEND GATEWAY",
        "Python 3.11+ • REST Endpoints",
        [
            "GET /api/business/overview",
            "GET /api/business/analytics",
            "POST /api/worker/start",
            "GET /api/worker/status/{exec_id}",
            "POST /api/approvals/{task_id}/approve",
            "POST /api/approvals/{task_id}/reject",
            "POST /api/demo/trigger-failure"
        ],
        border_color="#818CF8"
    )

    # 3. Persistent Memory & Database (Left Bottom)
    draw_card(
        60, 590, 320, 240,
        "PERSISTENT STORAGE",
        "SQLite Database & State Persistence",
        [
            "dukaandost.db: Customers, Products",
            "Transactions (320 rows, ₹95k Rev)",
            "Expenses (₹11k: Rent, Power, Wages)",
            "Net Income = ₹8,000 Reconciled",
            "checkpoints.db (LangGraph State)",
            "Thread Idempotency & Task Checkpoints",
            "Audit Logs & Safety Failure Records"
        ],
        border_color="#22C55E"
    )

    # 4. Central Multi-Agent Orchestration (Center Column)
    # Business Goal
    draw_card(
        430, 140, 720, 80,
        "1. BUSINESS GOAL INPUT",
        "Deterministic Objective Formulation",
        [
            "Target: Increase Sharma General Store net income from ₹8,000 to ₹10,000 (+25% growth)",
            "Scope: 120 synthetic customers, 32 products, identify opportunities without external spending"
        ],
        border_color="#22D3EE"
    )

    # Supervisor Agent
    draw_card(
        430, 245, 720, 85,
        "2. SUPERVISOR AGENT (Master Orchestrator)",
        "LangGraph StateGraph Root Node",
        [
            "Coordinates specialized agents, monitors thread status, delegates tasks, maintains execution state",
            "Guards idempotency: prevents duplicate task runs, coordinates bounded recovery workflows"
        ],
        border_color="#22D3EE"
    )

    # Business Analyst & Strategy Planner
    draw_card(
        430, 355, 345, 125,
        "3. BUSINESS ANALYST",
        "Financial & RFM Diagnostics",
        [
            "Calculates Rev (₹95k), COGS (₹76k)",
            "Computes exact ₹8,000 Net Income",
            "Detects 25 inactive customers",
            "Identifies 14 expiring paneer units"
        ],
        border_color="#818CF8"
    )

    draw_card(
        805, 355, 345, 125,
        "4. STRATEGY PLANNER",
        "Actionable Growth Roadmap",
        [
            "Formulates 4 prioritized initiatives",
            "TASK 1: Bread+Butter combo (₹440)",
            "TASK 2: Dormant reactivation (₹810)",
            "TASK 3: Expiry markdown (₹418)",
            "TASK 4: Bread/Eggs restock (₹480)"
        ],
        border_color="#818CF8"
    )

    # 3 Specialized Execution Agents
    draw_card(
        430, 505, 230, 140,
        "MARKETING AGENT",
        "Promotions & Churn",
        [
            "Segments customers",
            "Generates combo deals",
            "Drafts Kirana copy",
            "Simulates uptake"
        ],
        border_color="#22D3EE"
    )

    draw_card(
        675, 505, 230, 140,
        "INVENTORY AGENT",
        "Stock & Markdown",
        [
            "Monitors low stock",
            "Liquidates near-expiry",
            "Calculates carrying cost",
            "Prevents stockouts"
        ],
        border_color="#22D3EE"
    )

    draw_card(
        920, 505, 230, 140,
        "FINANCE AGENT",
        "Deterministic Gatekeeper",
        [
            "Calculates gross margin",
            "Blocks negative margins",
            "Enforces 15% discount cap",
            "Verifies incremental profit"
        ],
        border_color="#EF4444"
    )

    # Deterministic Tools
    draw_card(
        430, 670, 720, 85,
        "DETERMINISTIC PYTHON TOOLS",
        "Zero LLM Hallucination • Verified Math",
        [
            "SalesAnalyzer • CustomerAnalyzer • InventoryManager • ProfitCalculator • PromotionSimulator",
            "Calculates exact margins, price elasticities, and non-overlapping customer basket projections"
        ],
        border_color="#818CF8"
    )

    # Human-in-the-Loop & Approval (Center Bottom)
    draw_card(
        430, 780, 720, 125,
        "HUMAN-IN-THE-LOOP APPROVAL (LangGraph interrupt & resume)",
        "Controlled Autonomy with Zero Unapproved Financial Side Effects",
        [
            "PAUSE: interrupt(approval_payload) pauses graph when action requires store owner authorization",
            "PERSIST: State checkpointed in SQLite; pending approval surfaced in dashboard for Sharma Ji",
            "RESUME: Command(resume={'action': 'APPROVE'}) resumes EXACT thread without restarting workflow",
            "REJECT: Rejection isolates task, notifies supervisor, and triggers alternative replanning"
        ],
        border_color="#F59E0B"
    )

    # Feedback & Evaluation (Right Column)
    draw_card(
        1180, 140, 360, 220,
        "FEEDBACK & REPLANNING",
        "Execution-Level Adaptive Feedback",
        [
            "Variance Analysis: Expected vs Simulated",
            "TASK 1 Expected: ₹440 | Simulated: ₹418",
            "Adaptive Task Prioritization",
            "Replanning if goal gap remains",
            "Zero false claims of model fine-tuning",
            "Pure execution-level parameter tuning"
        ],
        border_color="#22D3EE"
    )

    draw_card(
        1180, 385, 360, 250,
        "FAILURE RECOVERY MATRIX",
        "Reproducible Safety Scenario (Sec 9)",
        [
            "Butter Condition: Cost ₹60 > Sell ₹55",
            "1. Marketing Agent proposes combo",
            "2. Finance Agent blocks negative margin",
            "3. Supervisor registers isolated failure",
            "4. Alert displayed in Failure Monitoring",
            "5. Human rectifies Butter price",
            "6. Supervisor revalidates and resumes!",
            "Bounded retries; zero unhandled crashes"
        ],
        border_color="#EF4444"
    )

    draw_card(
        1180, 660, 360, 245,
        "SYSTEM EVALUATION SCORECARD",
        "Automated Verification (Sec 10 & 26)",
        [
            "Task Completion Rate: 100.0%",
            "Task Failure Rate: 0.0% (Post recovery)",
            "Approval Rate: 100.0%",
            "Recovery Rate: 100.0%",
            "Baseline Income: ₹8,000.00",
            "Target Income: ₹10,000.00",
            "Simulated Outcome: ₹10,058.68",
            "Duplicate Execution Prevention: Verified"
        ],
        border_color="#22C55E"
    )

    # Bottom Legend / Footer
    draw.rectangle([(40, 930), (1560, 1060)], fill="#111111", outline="#333333", width=1)
    draw.text((60, 945), "ARCHITECTURAL GUARANTEES & SAFEGUARDS", fill="#FFFFFF", font=font_box_title)
    draw.text((60, 975), "1. Deterministic Local Execution: Runs completely offline without paid LLM API keys.", fill="#A1A1AA", font=font_box_text)
    draw.text((60, 995), "2. Strict Safety Guardrails: No negative-margin offers; discounts strictly capped at 15%; no unapproved inventory procurement.", fill="#A1A1AA", font=font_box_text)
    draw.text((60, 1015), "3. Persistent Thread Resumption: LangGraph SQLite saver preserves state across reboots; completed tasks are never executed twice.", fill="#A1A1AA", font=font_box_text)
    draw.text((60, 1035), "4. Ethical Separation: Clearly separates actual baseline Kirana data from simulated growth improvements.", fill="#A1A1AA", font=font_box_text)

    # Save to architecture/architecture.png
    os.makedirs("architecture", exist_ok=True)
    img.save("architecture/architecture.png")
    print("Saved architecture diagram to architecture/architecture.png")

if __name__ == "__main__":
    create_diagram()
