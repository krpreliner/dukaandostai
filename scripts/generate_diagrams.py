import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.makedirs('architecture', exist_ok=True)

DARK_BG = '#0B0F19'
CARD_BG = '#111827'
BORDER_COLOR = '#1F2937'
CYAN = '#22D3EE'
EMERALD = '#10B981'
AMBER = '#F59E0B'
RED = '#EF4444'
PURPLE = '#A855F7'
WHITE = '#F9FAFB'
GRAY = '#9CA3AF'

def draw_box(ax, x, y, w, h, title, subtitle="", color=CYAN, bg=CARD_BG, fontsize=10):
    rect = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        linewidth=1.5, edgecolor=color, facecolor=bg, zorder=2
    )
    ax.add_patch(rect)
    if subtitle:
        ax.text(x + w/2, y + h*0.62, title, color=WHITE, fontsize=fontsize, fontweight='bold', ha='center', va='center', zorder=3)
        ax.text(x + w/2, y + h*0.28, subtitle, color=GRAY, fontsize=fontsize*0.78, ha='center', va='center', zorder=3)
    else:
        ax.text(x + w/2, y + h*0.5, title, color=WHITE, fontsize=fontsize, fontweight='bold', ha='center', va='center', zorder=3)

def draw_arrow(ax, x1, y1, x2, y2, color=CYAN, text=""):
    ax.annotate(
        text, xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(facecolor=color, edgecolor=color, arrowstyle="-|>", lw=1.8, mutation_scale=15),
        color=color, fontsize=8, fontweight='semibold', ha='center', va='center', zorder=4
    )

# -------------------------------------------------------------
# 1. System Architecture Diagram
# -------------------------------------------------------------
def generate_system_architecture():
    fig, ax = plt.subplots(figsize=(14, 10), facecolor=DARK_BG)
    ax.set_facecolor(DARK_BG)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')

    plt.title("DUKAANDOST AI 2.0 — END-TO-END SYSTEM ARCHITECTURE", color=CYAN, fontsize=16, fontweight='bold', pad=20)

    # 1. Client Layer
    ax.text(0.5, 9.2, "CLIENT & VOICE LAYER", color=CYAN, fontsize=11, fontweight='bold')
    draw_box(ax, 0.5, 8.0, 3.8, 1.0, "React 18 + TS Web Dashboard", "Full-width desktop UI • 14 routes", CYAN)
    draw_box(ax, 4.8, 8.0, 4.2, 1.0, "Conversational AI Modal", "Hindi / English / Hinglish speech & text", CYAN)
    draw_box(ax, 9.5, 8.0, 4.0, 1.0, "Daily Business Briefing", "W3C Web Speech API • Read Aloud", CYAN)

    # 2. Gateway Layer
    ax.text(0.5, 7.3, "FASTAPI GATEWAY & SECURITY LAYER", color=PURPLE, fontsize=11, fontweight='bold')
    draw_box(ax, 0.5, 6.1, 3.8, 1.0, "CORS & Request Correlation", "UUID tracking & Process latency", PURPLE)
    draw_box(ax, 4.8, 6.1, 4.2, 1.0, "JWT Auth & RBAC Engine", "Owner, Manager, Staff • Argon2", PURPLE)
    draw_box(ax, 9.5, 6.1, 4.0, 1.0, "Multi-Tenant Isolation", "Strict X-Store-Id query filtration", PURPLE)

    # 3. Core Multi-Agent Orchestration
    ax.text(0.5, 5.4, "SIX-AGENT AUTONOMOUS MULTI-AGENT LAYER (LANGGRAPH)", color=EMERALD, fontsize=11, fontweight='bold')
    draw_box(ax, 0.5, 4.2, 2.0, 1.0, "Supervisor", "Goal routing", EMERALD)
    draw_box(ax, 2.7, 4.2, 2.0, 1.0, "Analyst", "Ledger retrieval", EMERALD)
    draw_box(ax, 4.9, 4.2, 2.0, 1.0, "Planner", "4-Pillar roadmap", EMERALD)
    draw_box(ax, 7.1, 4.2, 2.0, 1.0, "Marketing", "Bundle & Churn", EMERALD)
    draw_box(ax, 9.3, 4.2, 2.0, 1.0, "Inventory", "Stock replenishment", EMERALD)
    draw_box(ax, 11.5, 4.2, 2.0, 1.0, "Finance", "Margin Gatekeeper", RED)

    # 4. AI Provider Router & Tools
    ax.text(0.5, 3.5, "AI PROVIDER ROUTER & DETERMINISTIC ENGINE", color=AMBER, fontsize=11, fontweight='bold')
    draw_box(ax, 0.5, 2.3, 4.0, 1.0, "Deterministic Local Engine", "Offline • Rs 0.00 • 1.2ms latency", EMERALD)
    draw_box(ax, 4.8, 2.3, 4.2, 1.0, "Groq Cloud API (Primary)", "Llama 3.3 70B & Qwen 2.5 32B", AMBER)
    draw_box(ax, 9.5, 2.3, 4.0, 1.0, "Assistant Tools Engine", "9 Deterministic Python tools", CYAN)

    # 5. Persistence & Observability
    ax.text(0.5, 1.6, "DATA PERSISTENCE, MIGRATIONS & AUDIT TRAIL", color=WHITE, fontsize=11, fontweight='bold')
    draw_box(ax, 0.5, 0.4, 4.0, 1.0, "SQLite / PostgreSQL", "11 relational tables • Alembic", WHITE)
    draw_box(ax, 4.8, 0.4, 4.2, 1.0, "LangGraph Checkpoints", "checkpoints.db thread persistence", WHITE)
    draw_box(ax, 9.5, 0.4, 4.0, 1.0, "Immutable Audit Trail", "System health & guardrail log", WHITE)

    # Vertical Connecting Arrows
    draw_arrow(ax, 2.4, 8.0, 2.4, 7.1, CYAN)
    draw_arrow(ax, 6.9, 8.0, 6.9, 7.1, CYAN)
    draw_arrow(ax, 11.5, 8.0, 11.5, 7.1, CYAN)

    draw_arrow(ax, 2.4, 6.1, 2.4, 5.2, PURPLE)
    draw_arrow(ax, 6.9, 6.1, 6.9, 5.2, PURPLE)
    draw_arrow(ax, 11.5, 6.1, 11.5, 5.2, RED)

    draw_arrow(ax, 6.9, 4.2, 6.9, 3.3, EMERALD)
    draw_arrow(ax, 11.5, 4.2, 11.5, 3.3, RED)

    draw_arrow(ax, 2.5, 2.3, 2.5, 1.4, WHITE)
    draw_arrow(ax, 6.9, 2.3, 6.9, 1.4, WHITE)
    draw_arrow(ax, 11.5, 2.3, 11.5, 1.4, WHITE)

    plt.tight_layout()
    plt.savefig("architecture/dukaandost_system_architecture.png", dpi=300, facecolor=DARK_BG)
    plt.close()
    print("Generated: architecture/dukaandost_system_architecture.png")

# -------------------------------------------------------------
# 2. Multi-Agent Architecture
# -------------------------------------------------------------
def generate_multi_agent_architecture():
    fig, ax = plt.subplots(figsize=(13, 9), facecolor=DARK_BG)
    ax.set_facecolor(DARK_BG)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 9)
    ax.axis('off')

    plt.title("DUKAANDOST AI 2.0 — SIX-AGENT MULTI-AGENT ORCHESTRATION", color=CYAN, fontsize=15, fontweight='bold', pad=15)

    draw_box(ax, 4.0, 7.5, 5.0, 1.0, "Agent 1: Supervisor Agent", "Master Coordinator • Decomposes Goal • Fault Isolator", CYAN, fontsize=11)

    draw_box(ax, 0.5, 5.5, 3.6, 1.1, "Agent 2: Business Analyst", "Ledger retrieval • Net income gap\nAOV & category velocity", EMERALD)
    draw_box(ax, 4.7, 5.5, 3.6, 1.1, "Agent 3: Strategy Planner", "4-Pillar growth roadmap\nPrioritization & risk assessment", PURPLE)
    draw_box(ax, 8.9, 5.5, 3.6, 1.1, "Agent 4: Marketing Agent", "Cross-sell bundle proposals\nDormant customer reactivation", AMBER)

    draw_box(ax, 1.5, 3.3, 4.5, 1.1, "Agent 5: Inventory Agent", "Stockout alerts • Reorder quantities\nDead-stock liquidation proposals", CYAN)
    draw_box(ax, 7.0, 3.3, 4.5, 1.1, "Agent 6: Finance Agent (Gatekeeper)", "Strict non-negative margin check\n15% discount cap • Policy guardrail", RED)

    draw_box(ax, 1.5, 1.0, 4.5, 1.1, "Supervisor Fault Isolation", "Log FailureRecord (UNRESOLVED)\nPersist to DB • Prompt human repair", RED)
    draw_box(ax, 7.0, 1.0, 4.5, 1.1, "Human Approval Interrupt", "interrupt() pauses LangGraph thread\nShopkeeper sign-off via Web UI", EMERALD)

    # Connections
    draw_arrow(ax, 5.0, 7.5, 2.3, 6.6, CYAN)
    draw_arrow(ax, 6.5, 7.5, 6.5, 6.6, CYAN)
    draw_arrow(ax, 8.0, 7.5, 10.5, 6.6, CYAN)

    draw_arrow(ax, 6.5, 5.5, 3.7, 4.4, PURPLE)
    draw_arrow(ax, 6.5, 5.5, 9.2, 4.4, PURPLE)

    draw_arrow(ax, 3.7, 3.3, 8.0, 3.3, AMBER, "Propose")
    draw_arrow(ax, 9.2, 3.3, 3.7, 2.1, RED, "If Margin < 0")
    draw_arrow(ax, 9.2, 3.3, 9.2, 2.1, EMERALD, "If Margin > 5%")

    plt.tight_layout()
    plt.savefig("architecture/dukaandost_multi_agent_architecture.png", dpi=300, facecolor=DARK_BG)
    plt.close()
    print("Generated: architecture/dukaandost_multi_agent_architecture.png")

# -------------------------------------------------------------
# 3. LangGraph Workflow
# -------------------------------------------------------------
def generate_langgraph_workflow():
    fig, ax = plt.subplots(figsize=(14, 9), facecolor=DARK_BG)
    ax.set_facecolor(DARK_BG)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis('off')

    plt.title("DUKAANDOST AI 2.0 — LANGGRAPH STATEGRAPH EXECUTION LIFECYCLE", color=CYAN, fontsize=15, fontweight='bold', pad=15)

    draw_box(ax, 0.5, 7.2, 3.8, 1.1, "1. goal_understanding_node", "Goal: Rs 8k -> Rs 10k Target\nInit state, thread & execution ID", CYAN)
    draw_box(ax, 5.1, 7.2, 3.8, 1.1, "2. business_analysis_node", "Audit 320 txns & 32 products\nBaseline: Rs 8,000 | Gap: Rs 2,000", CYAN)
    draw_box(ax, 9.7, 7.2, 3.8, 1.1, "3. strategy_planning_node", "Formulate 4 growth pillars\nRank by expected income contribution", CYAN)

    draw_box(ax, 0.5, 4.6, 3.8, 1.1, "4. task_execution_node", "Iterate through planned tasks\nRoute to Marketing or Inventory", PURPLE)
    draw_box(ax, 5.1, 4.6, 3.8, 1.1, "5. finance_validation_node", "Deterministic margin check\nEnforce profit & discount ceiling", RED)
    draw_box(ax, 9.7, 4.6, 3.8, 1.1, "6. approval_interrupt_node", "Call interrupt() on high impact\nSave checkpoint to checkpoints.db", AMBER)

    draw_box(ax, 0.5, 1.8, 3.8, 1.1, "7. approval_resume_node", "Command(resume={'action': 'APPROVE'})\nExecute verified action atomically", EMERALD)
    draw_box(ax, 5.1, 1.8, 3.8, 1.1, "8. evaluation_node", "Measure simulated vs actual\nReconcile income variance", EMERALD)
    draw_box(ax, 9.7, 1.8, 3.8, 1.1, "9. Workflow Completion", "Persist final execution record\nEmit audit events to ledger", WHITE)

    # Connecting Flow
    draw_arrow(ax, 4.3, 7.7, 5.1, 7.7, CYAN)
    draw_arrow(ax, 8.9, 7.7, 9.7, 7.7, CYAN)
    draw_arrow(ax, 11.6, 7.2, 2.4, 5.7, CYAN)
    draw_arrow(ax, 4.3, 5.1, 5.1, 5.1, PURPLE)
    draw_arrow(ax, 8.9, 5.1, 9.7, 5.1, AMBER)
    draw_arrow(ax, 11.6, 4.6, 2.4, 2.9, AMBER)
    draw_arrow(ax, 4.3, 2.3, 5.1, 2.3, EMERALD)
    draw_arrow(ax, 8.9, 2.3, 9.7, 2.3, WHITE)

    plt.tight_layout()
    plt.savefig("architecture/dukaandost_langgraph_workflow.png", dpi=300, facecolor=DARK_BG)
    plt.close()
    print("Generated: architecture/dukaandost_langgraph_workflow.png")

# -------------------------------------------------------------
# 4. Database ER Diagram
# -------------------------------------------------------------
def generate_database_er():
    fig, ax = plt.subplots(figsize=(14, 9), facecolor=DARK_BG)
    ax.set_facecolor(DARK_BG)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis('off')

    plt.title("DUKAANDOST AI 2.0 — MULTI-TENANT RELATIONAL DATABASE SCHEMA", color=CYAN, fontsize=15, fontweight='bold', pad=15)

    draw_box(ax, 5.0, 7.2, 4.0, 1.2, "STORES", "store_id (PK), name, location\ninitial_income, target_income, current_income", CYAN)

    draw_box(ax, 0.5, 5.0, 3.8, 1.2, "PRODUCTS", "id, store_id (FK), product_id (UK)\ncost_price, selling_price, stock, status", EMERALD)
    draw_box(ax, 5.0, 5.0, 4.0, 1.2, "CUSTOMERS", "id, store_id (FK), customer_id (UK)\nname, segment, lifetime_spend, last_order", EMERALD)
    draw_box(ax, 9.7, 5.0, 3.8, 1.2, "TRANSACTIONS", "id, store_id (FK), txn_id (UK)\ncustomer_id (FK), amount, gross_profit", EMERALD)

    draw_box(ax, 0.5, 2.8, 3.8, 1.2, "EXECUTION_RECORDS", "id, store_id (FK), execution_id (UK)\nthread_id, status, target_income, current_agent", PURPLE)
    draw_box(ax, 5.0, 2.8, 4.0, 1.2, "TASK_RECORDS", "id, execution_id (FK), task_id\nassigned_agent, priority, status, impact", PURPLE)
    draw_box(ax, 9.7, 2.8, 3.8, 1.2, "EXPENSES", "id, store_id (FK), category\namount, frequency, date", PURPLE)

    draw_box(ax, 0.5, 0.6, 3.8, 1.2, "FAILURE_RECORDS", "id, store_id (FK), execution_id\ntask_id, root_cause, recovery_status, retries", RED)
    draw_box(ax, 5.0, 0.6, 4.0, 1.2, "APPROVAL_RECORDS", "id, store_id (FK), execution_id\ntask_id, original_price, proposed_price, status", AMBER)
    draw_box(ax, 9.7, 0.6, 3.8, 1.2, "AUDIT_LOGS", "id, store_id (FK), execution_id\nevent_type, agent_name, details, timestamp", WHITE)

    # Relationship Links
    draw_arrow(ax, 6.0, 7.2, 2.4, 6.2, CYAN)
    draw_arrow(ax, 7.0, 7.2, 7.0, 6.2, CYAN)
    draw_arrow(ax, 8.0, 7.2, 11.6, 6.2, CYAN)

    draw_arrow(ax, 7.0, 5.0, 7.0, 4.0, EMERALD)
    draw_arrow(ax, 2.4, 2.8, 2.4, 1.8, RED)
    draw_arrow(ax, 7.0, 2.8, 7.0, 1.8, AMBER)
    draw_arrow(ax, 11.6, 2.8, 11.6, 1.8, WHITE)

    plt.tight_layout()
    plt.savefig("architecture/dukaandost_database_er.png", dpi=300, facecolor=DARK_BG)
    plt.close()
    print("Generated: architecture/dukaandost_database_er.png")

# -------------------------------------------------------------
# 5. Approval & Recovery Flow
# -------------------------------------------------------------
def generate_approval_recovery():
    fig, ax = plt.subplots(figsize=(14, 9), facecolor=DARK_BG)
    ax.set_facecolor(DARK_BG)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis('off')

    plt.title("DUKAANDOST AI 2.0 — SAFETY GUARDRAIL & APPROVAL LIFECYCLE", color=CYAN, fontsize=15, fontweight='bold', pad=15)

    # Track 1: Failure & Rectification
    ax.text(0.5, 8.2, "TRACK 1: FINANCIAL GUARDRAIL AUTO-REJECTION & RECTIFICATION", color=RED, fontsize=11, fontweight='bold')
    draw_box(ax, 0.5, 6.8, 3.8, 1.1, "1. Trigger Failure Condition", "Butter: Cost Rs 60.00 > Sell Rs 55.00\nLoss: -Rs 5.00/unit • Margin: -9.09%", RED)
    draw_box(ax, 5.1, 6.8, 3.8, 1.1, "2. Finance Agent Halt", "Deterministic Gatekeeper rejection\nInsert FailureRecord (UNRESOLVED)", RED)
    draw_box(ax, 9.7, 6.8, 3.8, 1.1, "3. Rectify Price & Revalidate", "Shopkeeper rectifies to Sell Rs 68.00\nMargin +11.8% • Status: RESOLVED", EMERALD)

    # Track 2: Human Approval & Resumption
    ax.text(0.5, 4.8, "TRACK 2: HUMAN-IN-THE-LOOP APPROVAL & GRAPH RESUMPTION", color=AMBER, fontsize=11, fontweight='bold')
    draw_box(ax, 0.5, 3.4, 3.8, 1.1, "1. LangGraph Interrupt", "High-impact campaign generated\nThread paused in checkpoints.db", AMBER)
    draw_box(ax, 5.1, 3.4, 3.8, 1.1, "2. Owner Review in Web UI", "Card stack displays impact & risk\nShopkeeper clicks 'Approve' or 'Reject'", CYAN)
    draw_box(ax, 9.7, 3.4, 3.8, 1.1, "3. Atomic Graph Resumption", "Command(resume=APPROVED)\nResume thread & record audit log", EMERALD)

    # Track 3: Final Outcomes
    ax.text(0.5, 1.8, "TRACK 3: IMMUTABLE AUDIT TRAIL & LEDGER RECONCILIATION", color=WHITE, fontsize=11, fontweight='bold')
    draw_box(ax, 0.5, 0.5, 6.0, 1.0, "Immutable Audit Trail (audit_logs)", "Records event_type, actor, details & timestamp", WHITE)
    draw_box(ax, 7.5, 0.5, 6.0, 1.0, "Autonomous Re-planning & Learning", "Updates evaluation metrics & recalibrates gap", WHITE)

    # Track 1 Arrows
    draw_arrow(ax, 4.3, 7.3, 5.1, 7.3, RED)
    draw_arrow(ax, 8.9, 7.3, 9.7, 7.3, EMERALD)

    # Track 2 Arrows
    draw_arrow(ax, 4.3, 3.9, 5.1, 3.9, AMBER)
    draw_arrow(ax, 8.9, 3.9, 9.7, 3.9, EMERALD)

    plt.tight_layout()
    plt.savefig("architecture/dukaandost_approval_recovery.png", dpi=300, facecolor=DARK_BG)
    plt.close()
    print("Generated: architecture/dukaandost_approval_recovery.png")

if __name__ == "__main__":
    generate_system_architecture()
    generate_multi_agent_architecture()
    generate_langgraph_workflow()
    generate_database_er()
    generate_approval_recovery()
    print("ALL 5 ARCHITECTURE DIAGRAMS GENERATED SUCCESSFULLY!")
