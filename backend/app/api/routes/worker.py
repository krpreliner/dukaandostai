from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.execution_service import ExecutionService
from app.api.schemas.api_models import WorkerStartRequest
from app.graph.workflow import build_dukaandost_graph

router = APIRouter(prefix="/api", tags=["Worker"])

@router.post("/worker/start")
def start_worker(
    req: WorkerStartRequest = None,
    x_store_id: str = Header("STORE_001", alias="X-Store-Id"),
    db: Session = Depends(get_db)
):
    svc = ExecutionService(db)
    target = req.target_income if req else 10000.0
    return svc.start_worker(custom_target=target, store_id=x_store_id)

@router.get("/worker/status/{execution_id}")
def get_worker_status(execution_id: str, db: Session = Depends(get_db)):
    svc = ExecutionService(db)
    res = svc.get_execution_status(execution_id)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res

@router.get("/worker/state/{execution_id}")
def get_worker_full_state(execution_id: str, db: Session = Depends(get_db)):
    svc = ExecutionService(db)
    status = svc.get_execution_status(execution_id)
    if "error" in status:
        raise HTTPException(status_code=404, detail=status["error"])

    graph = build_dukaandost_graph()
    thread_id = status.get("thread_id", execution_id)
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = graph.get_state(config)

    return {
        "execution_id": execution_id,
        "thread_id": thread_id,
        "is_interrupted": len(snapshot.tasks) > 0 if snapshot else False,
        "interrupted_tasks": [t.name for t in snapshot.tasks] if snapshot else [],
        "state_values": snapshot.values if snapshot else {},
        "status_summary": status
    }

@router.get("/agents/status")
def get_agents_status(
    x_store_id: str = Header("STORE_001", alias="X-Store-Id"),
    db: Session = Depends(get_db)
):
    svc = ExecutionService(db)
    latest = svc.repo.get_latest_execution(store_id=x_store_id)
    active_agent = latest.current_agent if latest else "Supervisor"
    worker_status = latest.status if latest else "IDLE"

    agents = [
        {
            "id": "agent-1",
            "name": "Business Analyst Agent",
            "role": "Financial & Customer Diagnostics",
            "status": "ACTIVE" if active_agent == "Business Analyst Agent" else ("READY" if worker_status != "IDLE" else "IDLE"),
            "responsibility": "Analyzes synthetic sales, COGS, margins, customer segments, and computes baseline income.",
            "last_action": "Analyzed 320 transactions across 120 customers and 32 items"
        },
        {
            "id": "agent-2",
            "name": "Strategy Planner Agent",
            "role": "Autonomous Growth Strategy",
            "status": "ACTIVE" if active_agent == "Strategy Planner Agent" else ("READY" if worker_status != "IDLE" else "IDLE"),
            "responsibility": "Translates net income gap into prioritized actionable initiatives with risk tags.",
            "last_action": "Generated 4 prioritized tasks to bridge ₹2,000 net income gap"
        },
        {
            "id": "agent-3",
            "name": "Marketing Agent",
            "role": "Promotions & Customer Reactivation",
            "status": "ACTIVE" if active_agent == "Marketing Agent" else ("READY" if worker_status != "IDLE" else "IDLE"),
            "responsibility": "Simulates customer reactivation, product combos, and drafts Kirana promotions.",
            "last_action": "Formulated Breakfast Combo (Bread + Butter) with Hindi Kirana copy"
        },
        {
            "id": "agent-4",
            "name": "Inventory Agent",
            "role": "Stockout & Expiry Intelligence",
            "status": "ACTIVE" if active_agent == "Inventory Agent" else ("READY" if worker_status != "IDLE" else "IDLE"),
            "responsibility": "Detects stockouts, perishable expiry risks, and calculates inventory markdown savings.",
            "last_action": "Detected perishable Sudha Paneer; scheduled liquidation"
        },
        {
            "id": "agent-5",
            "name": "Finance Agent",
            "role": "Deterministic Financial Gatekeeper",
            "status": "ACTIVE" if active_agent == "Finance Agent" else ("READY" if worker_status != "IDLE" else "IDLE"),
            "responsibility": "Enforces business policies, calculates incremental net profit, and blocks negative margins.",
            "last_action": "Enforced non-negative gross profit policy and 15% discount limit"
        },
        {
            "id": "agent-6",
            "name": "Supervisor Agent",
            "role": "Orchestrator & Resilience Coordinator",
            "status": "ACTIVE" if (active_agent == "Supervisor" or worker_status in ["ANALYSING", "PLANNING", "EXECUTING"]) else "IDLE",
            "responsibility": "Coordinates specialized agents, triggers interrupts, handles failure recovery.",
            "last_action": "Monitored execution thread and synchronized state checkpointer"
        }
    ]
    return {"worker_status": worker_status, "agents": agents}
