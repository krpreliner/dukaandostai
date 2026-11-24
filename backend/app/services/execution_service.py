import uuid
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.graph.workflow import build_dukaandost_graph
from app.memory.state_manager import StateManager
from app.database.repository import BusinessRepository
from app.config import settings

class ExecutionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = BusinessRepository(db)
        self.state_mgr = StateManager(db)

    def start_worker(self, custom_target: Optional[float] = None) -> Dict[str, Any]:
        target = custom_target if custom_target is not None else settings.TARGET_NET_INCOME
        exec_id = f"EXEC_{uuid.uuid4().hex[:8].upper()}"
        thread_id = exec_id

        initial_state = {
            "execution_id": exec_id,
            "thread_id": thread_id,
            "business_goal": f"Increase Sharma General Store's monthly net income from ₹{settings.INITIAL_NET_INCOME:,.0f} to ₹{target:,.0f} by identifying business opportunities, improving customer purchases, optimising inventory and reducing avoidable business expenses.",
            "initial_income": settings.INITIAL_NET_INCOME,
            "target_income": target,
            "current_income": settings.INITIAL_NET_INCOME,
            "simulated_income": settings.INITIAL_NET_INCOME,
            "completed_tasks": [],
            "failed_tasks": [],
            "feedback": [],
            "execution_history": [],
            "current_status": "ANALYSING",
            "current_agent": "Business Analyst Agent",
            "current_task": "Starting autonomous growth workflow",
            "iteration_count": 0
        }

        # Initialize DB ExecutionRecord
        self.repo.create_or_update_execution({
            "execution_id": exec_id,
            "thread_id": thread_id,
            "status": "ANALYSING",
            "initial_income": settings.INITIAL_NET_INCOME,
            "target_income": target,
            "current_income": settings.INITIAL_NET_INCOME,
            "simulated_income": settings.INITIAL_NET_INCOME,
            "current_agent": "Business Analyst Agent",
            "current_task": "Analyzing business data"
        })

        graph = build_dukaandost_graph()
        config = {"configurable": {"thread_id": thread_id}}

        # Execute graph (runs up to human approval interrupt or completion)
        try:
            graph.invoke(initial_state, config)
        except Exception as e:
            # If unexpected error occurs
            self.repo.log_audit("GRAPH_ERROR", "Supervisor", str(e), execution_id=exec_id)

        # Check state from checkpointer
        state_snapshot = graph.get_state(config)
        current_state = state_snapshot.values if state_snapshot else initial_state

        is_interrupted = len(state_snapshot.tasks) > 0 if state_snapshot else False
        status = "WAITING FOR APPROVAL" if is_interrupted else current_state.get("current_status", "COMPLETED")

        # Update DB status
        self.repo.create_or_update_execution({
            "execution_id": exec_id,
            "thread_id": thread_id,
            "status": status,
            "current_agent": current_state.get("current_agent", "Supervisor"),
            "current_task": current_state.get("current_task", ""),
            "simulated_income": current_state.get("simulated_income", settings.INITIAL_NET_INCOME)
        })

        return {
            "execution_id": exec_id,
            "thread_id": thread_id,
            "status": status,
            "is_interrupted": is_interrupted,
            "current_agent": current_state.get("current_agent"),
            "current_task": current_state.get("current_task"),
            "simulated_income": current_state.get("simulated_income"),
            "completed_tasks": current_state.get("completed_tasks", []),
            "pending_tasks": current_state.get("pending_tasks", [])
        }

    def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        exec_record = self.repo.get_execution(execution_id)
        if not exec_record:
            return {"error": "Execution not found", "execution_id": execution_id}

        tasks = self.repo.get_tasks_for_execution(execution_id)
        approvals = self.repo.get_pending_approvals(execution_id)
        failures = self.repo.get_failures(execution_id)

        # Check checkpointer state for interrupt
        graph = build_dukaandost_graph()
        config = {"configurable": {"thread_id": exec_record.thread_id}}
        snapshot = graph.get_state(config)
        is_paused = len(snapshot.tasks) > 0 if snapshot else False

        current_status = "WAITING FOR APPROVAL" if is_paused else exec_record.status

        return {
            "execution_id": exec_record.execution_id,
            "thread_id": exec_record.thread_id,
            "status": current_status,
            "initial_income": exec_record.initial_income,
            "target_income": exec_record.target_income,
            "current_income": exec_record.current_income,
            "simulated_income": exec_record.simulated_income,
            "variance": exec_record.variance,
            "current_agent": exec_record.current_agent,
            "current_task": exec_record.current_task,
            "is_paused": is_paused,
            "tasks": [
                {
                    "task_id": t.task_id,
                    "task_name": t.task_name,
                    "assigned_agent": t.assigned_agent,
                    "priority": t.priority,
                    "expected_impact": t.expected_impact,
                    "simulated_impact": t.simulated_impact,
                    "risk_level": t.risk_level,
                    "approval_required": t.approval_required,
                    "status": t.status,
                    "execution_result": t.execution_result,
                    "failure_reason": t.failure_reason
                }
                for t in tasks
            ],
            "pending_approvals": [
                {
                    "task_id": a.task_id,
                    "action_description": a.action_description,
                    "requesting_agent": a.requesting_agent,
                    "original_price": a.original_price,
                    "proposed_price": a.proposed_price,
                    "gross_margin_pct": a.gross_margin_pct,
                    "expected_impact": a.expected_impact,
                    "justification": a.justification,
                    "risk_assessment": a.risk_assessment,
                    "status": a.status
                }
                for a in approvals
            ],
            "failures": [
                {
                    "task_id": f.task_id,
                    "agent_name": f.agent_name,
                    "error_description": f.error_description,
                    "root_cause": f.root_cause,
                    "recovery_status": f.recovery_status,
                    "retry_count": f.retry_count
                }
                for f in failures
            ]
        }
