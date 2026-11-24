from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
from app.database.repository import BusinessRepository
from app.graph.state import DukaandostState

class StateManager:
    """
    Synchronizes in-flight LangGraph state with persistent application database records.
    Ensures that dashboard and frontend can query live state, tasks, and historical logs.
    """
    def __init__(self, db: Session):
        self.db = db
        self.repo = BusinessRepository(db)

    def sync_execution_state(self, state: DukaandostState) -> None:
        exec_id = state.get("execution_id")
        if not exec_id:
            return

        exec_data = {
            "execution_id": exec_id,
            "thread_id": state.get("thread_id", exec_id),
            "status": state.get("current_status", "IDLE"),
            "initial_income": state.get("initial_income", 8000.0),
            "target_income": state.get("target_income", 10000.0),
            "current_income": state.get("current_income", 8000.0),
            "simulated_income": state.get("simulated_income", 8000.0),
            "variance": round(state.get("simulated_income", 8000.0) - state.get("initial_income", 8000.0), 2),
            "current_agent": state.get("current_agent", "Supervisor"),
            "current_task": state.get("current_task", ""),
        }
        if state.get("current_status") == "COMPLETED":
            exec_data["completed_at"] = datetime.utcnow()

        self.repo.create_or_update_execution(exec_data)

    def sync_task(self, execution_id: str, task: Dict[str, Any]) -> None:
        task_data = {
            "execution_id": execution_id,
            "task_id": task.get("task_id", ""),
            "task_name": task.get("task_name", ""),
            "assigned_agent": task.get("assigned_agent", "Supervisor"),
            "priority": task.get("priority", "MEDIUM"),
            "expected_impact": task.get("expected_impact", 0.0),
            "simulated_impact": task.get("simulated_impact", 0.0),
            "risk_level": task.get("risk_level", "LOW"),
            "approval_required": task.get("approval_required", False),
            "status": task.get("status", "PENDING"),
            "execution_result": str(task.get("execution_result", "")),
            "failure_reason": str(task.get("failure_reason", "")),
            "retry_count": task.get("retry_count", 0),
        }
        self.repo.create_or_update_task(task_data)
