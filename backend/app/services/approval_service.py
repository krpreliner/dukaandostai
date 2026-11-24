from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from langgraph.types import Command
from app.graph.workflow import build_dukaandost_graph
from app.database.repository import BusinessRepository
from app.database.models import ApprovalRecord

class ApprovalService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = BusinessRepository(db)

    def get_pending_approvals(self, execution_id: Optional[str] = None) -> List[Dict[str, Any]]:
        approvals = self.repo.get_pending_approvals(execution_id)
        return [
            {
                "id": a.id,
                "execution_id": a.execution_id,
                "task_id": a.task_id,
                "action_description": a.action_description,
                "requesting_agent": a.requesting_agent,
                "original_price": a.original_price,
                "proposed_price": a.proposed_price,
                "gross_margin_pct": a.gross_margin_pct,
                "expected_impact": a.expected_impact,
                "justification": a.justification,
                "risk_assessment": a.risk_assessment,
                "status": a.status,
                "created_at": a.created_at.isoformat() if a.created_at else None
            }
            for a in approvals
        ]

    def handle_decision(self, task_id: str, action: str, execution_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Resumes LangGraph execution on the exact thread using Command(resume=...).
        action: 'APPROVE' or 'REJECT'
        """
        # Find pending approval record
        q = self.db.query(ApprovalRecord).filter_by(task_id=task_id, status="PENDING")
        if execution_id:
            q = q.filter_by(execution_id=execution_id)
        approval_rec = q.first()

        if not approval_rec:
            # Fallback to any recent approval record with that task_id
            approval_rec = self.db.query(ApprovalRecord).filter_by(task_id=task_id).first()
            if not approval_rec:
                return {"success": False, "error": f"No approval request found for task '{task_id}'"}

        exec_id = approval_rec.execution_id
        thread_id = exec_id

        # Update DB approval record status immediately
        approval_rec.status = "APPROVED" if action.upper() == "APPROVE" else "REJECTED"
        approval_rec.decided_at = datetime.utcnow()
        self.db.commit()

        # Build graph and resume thread via Command
        graph = build_dukaandost_graph()
        config = {"configurable": {"thread_id": thread_id}}

        resume_payload = {"action": action.upper(), "task_id": task_id}

        try:
            # Resume graph with Command
            graph.invoke(Command(resume=resume_payload), config)
        except Exception as e:
            self.repo.log_audit("RESUME_ERROR", "Supervisor", str(e), execution_id=exec_id)

        # Check post-resume state
        snapshot = graph.get_state(config)
        is_interrupted = len(snapshot.tasks) > 0 if snapshot else False
        current_state = snapshot.values if snapshot else {}

        new_status = "WAITING FOR APPROVAL" if is_interrupted else current_state.get("current_status", "COMPLETED")

        # Sync DB execution record
        self.repo.create_or_update_execution({
            "execution_id": exec_id,
            "thread_id": thread_id,
            "status": new_status,
            "current_agent": current_state.get("current_agent", "Supervisor"),
            "current_task": current_state.get("current_task", ""),
            "simulated_income": current_state.get("simulated_income", 8000.0)
        })

        return {
            "success": True,
            "task_id": task_id,
            "decision": action.upper(),
            "execution_id": exec_id,
            "workflow_status": new_status,
            "is_interrupted": is_interrupted,
            "simulated_income": current_state.get("simulated_income")
        }
