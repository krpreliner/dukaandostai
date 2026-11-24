from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from langgraph.types import Command
from app.graph.workflow import build_dukaandost_graph
from app.database.repository import BusinessRepository
from app.database.models import ApprovalRecord

class ApprovalService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = BusinessRepository(db)

    def get_pending_approvals(self, execution_id: Optional[str] = None, store_id: str = "STORE_001") -> List[Dict[str, Any]]:
        approvals = self.repo.get_pending_approvals(execution_id, store_id=store_id)
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

    def get_approval_history(self, execution_id: Optional[str] = None, store_id: str = "STORE_001") -> List[Dict[str, Any]]:
        return self.get_all_approvals_history(execution_id, store_id=store_id)

    def get_all_approvals_history(self, execution_id: Optional[str] = None, store_id: str = "STORE_001") -> List[Dict[str, Any]]:
        approvals = self.repo.get_all_approvals(execution_id, store_id=store_id)
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
                "decided_at": a.decided_at.isoformat() if a.decided_at else None,
                "created_at": a.created_at.isoformat() if a.created_at else None
            }
            for a in approvals
        ]

    def handle_decision(self, task_id: str, action: str, execution_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Resumes LangGraph execution on the exact thread using Command(resume=...).
        action: 'APPROVE' or 'REJECT'
        """
        decision_str = action.upper()
        if decision_str not in ["APPROVE", "REJECT", "APPROVED", "REJECTED"]:
            return {"success": False, "error": f"Invalid approval decision '{action}'. Must be 'APPROVE' or 'REJECT'."}

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
            if approval_rec.status in ["APPROVED", "REJECTED"]:
                return {
                    "success": False,
                    "error": f"Task '{task_id}' was already decided as {approval_rec.status} on {approval_rec.decided_at}."
                }

        exec_id = approval_rec.execution_id
        thread_id = exec_id

        # Update DB approval record status immediately
        approval_rec.status = "APPROVED" if "APPROV" in decision_str else "REJECTED"
        approval_rec.decided_at = datetime.now(timezone.utc)
        self.db.commit()

        # Log audit record
        self.repo.log_audit(
            event_type="HUMAN_APPROVAL_DECISION",
            agent_name="Shopkeeper / Human Owner",
            details=f"Task '{task_id}' was {approval_rec.status} by human management.",
            execution_id=exec_id,
            store_id=getattr(approval_rec, "store_id", "STORE_001")
        )

        # Build graph and resume thread via Command
        graph = build_dukaandost_graph()
        config = {"configurable": {"thread_id": thread_id}}

        resume_payload = {"action": approval_rec.status, "task_id": task_id}

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
            "decision": approval_rec.status,
            "execution_id": exec_id,
            "workflow_status": new_status,
            "is_interrupted": is_interrupted,
            "simulated_income": current_state.get("simulated_income")
        }
