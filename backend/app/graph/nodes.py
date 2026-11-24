from typing import Dict, Any, List
from datetime import datetime
from langgraph.types import interrupt
from app.graph.state import DukaandostState
from app.database.connection import SessionLocal
from app.database.repository import BusinessRepository
from app.agents.supervisor import SupervisorAgent
from app.memory.state_manager import StateManager
from app.memory.audit_log import AuditLogger

def goal_understanding_node(state: DukaandostState) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        exec_id = state.get("execution_id", "EXEC_INIT")
        AuditLogger.log(
            db,
            event_type="GOAL_INITIALIZED",
            agent_name="Supervisor",
            details=f"Goal received: '{state.get('business_goal')}' targeting net income ₹{state.get('target_income', 10000.0):,.2f}",
            execution_id=exec_id
        )
        return {
            "current_status": "ANALYSING",
            "current_agent": "Business Analyst Agent",
            "current_task": "Analyzing Kirana store transactional and inventory records",
            "iteration_count": 0,
            "completed_tasks": state.get("completed_tasks", []),
            "failed_tasks": state.get("failed_tasks", []),
            "feedback": state.get("feedback", []),
            "execution_history": state.get("execution_history", [])
        }
    finally:
        db.close()


def business_analysis_node(state: DukaandostState) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        exec_id = state.get("execution_id", "EXEC_INIT")
        supervisor = SupervisorAgent(db)
        analysis = supervisor.analyze_business(target_income=state.get("target_income", 10000.0))

        AuditLogger.log(
            db,
            event_type="BUSINESS_ANALYSIS_COMPLETED",
            agent_name="Business Analyst Agent",
            details=f"Baseline Net Income: ₹{analysis['current_income']:.2f}. Income Gap: ₹{analysis['income_gap']:.2f}. Identified {len(analysis['growth_opportunities'])} strategic opportunities.",
            execution_id=exec_id
        )

        return {
            "business_analysis": analysis,
            "current_income": analysis["current_income"],
            "simulated_income": analysis["current_income"],
            "current_status": "PLANNING",
            "current_agent": "Strategy Planner Agent",
            "current_task": "Formulating actionable growth strategies to bridge ₹2,000 gap"
        }
    finally:
        db.close()


def strategy_planning_node(state: DukaandostState) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        exec_id = state.get("execution_id", "EXEC_INIT")
        supervisor = SupervisorAgent(db)
        analysis = state.get("business_analysis", {})
        tasks = supervisor.plan_strategy(analysis)

        state_mgr = StateManager(db)
        for t in tasks:
            state_mgr.sync_task(exec_id, t)

        AuditLogger.log(
            db,
            event_type="STRATEGY_PLAN_FORMULATED",
            agent_name="Strategy Planner Agent",
            details=f"Created {len(tasks)} actionable tasks across Product Bundling, Customer Reactivation, Expiry Clearance, and Restocking.",
            execution_id=exec_id
        )

        return {
            "execution_plan": tasks,
            "task_queue": list(tasks),
            "pending_tasks": list(tasks),
            "current_status": "PLANNING",
            "current_agent": "Supervisor",
            "current_task": "Prioritizing tasks and coordinating agent execution"
        }
    finally:
        db.close()


def task_prioritisation_node(state: DukaandostState) -> Dict[str, Any]:
    queue = list(state.get("task_queue", []))
    # Sort queue by priority: HIGH first, then MEDIUM, then LOW
    priority_weights = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
    queue.sort(key=lambda t: priority_weights.get(t.get("priority", "MEDIUM"), 1), reverse=True)

    return {
        "task_queue": queue,
        "current_status": "EXECUTING",
        "current_agent": "Supervisor",
        "current_task": f"Ready to execute top priority task from queue ({len(queue)} pending)"
    }


def supervisor_decision_node(state: DukaandostState) -> Dict[str, Any]:
    queue = list(state.get("task_queue", []))
    if not queue:
        return {
            "active_task": None,
            "current_status": "COMPLETING",
            "current_agent": "Supervisor",
            "current_task": "All strategy tasks processed"
        }

    # Pop next task
    next_task = queue.pop(0)

    # Idempotency check: If task is already completed, skip it
    completed_ids = [t["task_id"] for t in state.get("completed_tasks", [])]
    if next_task["task_id"] in completed_ids:
        return {
            "task_queue": queue,
            "active_task": None,
            "current_status": "EXECUTING",
            "current_agent": "Supervisor",
            "current_task": f"Skipping already completed task {next_task['task_id']}"
        }

    return {
        "task_queue": queue,
        "active_task": next_task,
        "current_status": "EXECUTING",
        "current_agent": next_task.get("assigned_agent", "Supervisor"),
        "current_task": f"Processing task: {next_task.get('task_name')}"
    }


def financial_validation_node(state: DukaandostState) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        active_task = state.get("active_task")
        if not active_task:
            return {"active_task": None}

        exec_id = state.get("execution_id", "EXEC_INIT")
        supervisor = SupervisorAgent(db)
        repo = BusinessRepository(db)

        # Run deterministic financial validation
        val_result = supervisor.validate_task_finance(active_task)

        if not val_result.get("is_approved", False):
            # Failure detected! Log failure record
            err_msg = val_result.get("message", "Financial validation failed.")
            fail_record = {
                "execution_id": exec_id,
                "task_id": active_task.get("task_id", ""),
                "agent_name": "Finance Agent",
                "error_description": err_msg,
                "root_cause": val_result.get("error_type", "FINANCIAL_VIOLATION"),
                "recovery_status": "UNRESOLVED",
                "retry_count": active_task.get("retry_count", 0) + 1
            }
            repo.log_failure(fail_record)
            AuditLogger.log(
                db,
                event_type="FINANCIAL_VALIDATION_FAILED",
                agent_name="Finance Agent",
                details=err_msg,
                execution_id=exec_id
            )

            # Mark task failed in DB
            active_task["status"] = "FAILED"
            active_task["failure_reason"] = err_msg
            repo.create_or_update_task({
                "execution_id": exec_id,
                "task_id": active_task["task_id"],
                "task_name": active_task["task_name"],
                "assigned_agent": active_task["assigned_agent"],
                "status": "FAILED",
                "failure_reason": err_msg
            })

            return {
                "active_task": active_task,
                "current_status": "RECOVERING",
                "current_agent": "Finance Agent",
                "current_task": f"Blocked task {active_task['task_id']} due to financial policy violation"
            }

        # If financially valid
        AuditLogger.log(
            db,
            event_type="FINANCIAL_VALIDATION_PASSED",
            agent_name="Finance Agent",
            details=f"Task {active_task['task_id']} '{active_task['task_name']}' passed financial guardrails.",
            execution_id=exec_id
        )

        return {
            "active_task": active_task,
            "current_status": "WAITING FOR APPROVAL" if active_task.get("approval_required") else "EXECUTING",
            "current_agent": active_task.get("assigned_agent", "Supervisor")
        }
    finally:
        db.close()


def human_approval_node(state: DukaandostState) -> Dict[str, Any]:
    """
    CRITICAL: No side effects before interrupt!
    When paused, interrupt() yields to human approval.
    When resumed with Command(resume={'action': 'APPROVE'/'REJECT'}),
    we record the decision and proceed idempotently.
    """
    active_task = state.get("active_task")
    if not active_task:
        return {"active_task": None}

    exec_id = state.get("execution_id", "EXEC_INIT")
    task_id = active_task.get("task_id", "")
    task_name = active_task.get("task_name", "")

    # Prepare interrupt payload
    approval_payload = {
        "execution_id": exec_id,
        "task_id": task_id,
        "task_name": task_name,
        "action_description": f"Authorize execution of {task_name}",
        "requesting_agent": active_task.get("assigned_agent", "Supervisor"),
        "expected_impact": active_task.get("expected_impact", 0.0),
        "risk_level": active_task.get("risk_level", "MEDIUM"),
        "details": active_task.get("details", {})
    }

    # Sync pending approval to DB for visibility in dashboard
    db = SessionLocal()
    try:
        repo = BusinessRepository(db)
        repo.create_approval_request({
            "execution_id": exec_id,
            "task_id": task_id,
            "action_description": approval_payload["action_description"],
            "requesting_agent": approval_payload["requesting_agent"],
            "original_price": active_task.get("details", {}).get("original_price", 115.0),
            "proposed_price": active_task.get("details", {}).get("proposed_price", 109.0),
            "gross_margin_pct": 10.09,
            "expected_impact": active_task.get("expected_impact", 0.0),
            "justification": "Increase basket order size and boost Kirana profitability.",
            "risk_assessment": "Financially verified positive margin.",
            "status": "PENDING"
        })
        repo.create_or_update_task({
            "execution_id": exec_id,
            "task_id": task_id,
            "task_name": task_name,
            "assigned_agent": active_task.get("assigned_agent", "Supervisor"),
            "status": "WAITING_APPROVAL"
        })
        AuditLogger.log(
            db,
            event_type="APPROVAL_REQUESTED",
            agent_name="Supervisor",
            details=f"Human approval requested for Task {task_id}: {task_name}",
            execution_id=exec_id
        )
    finally:
        db.close()

    # Pause execution at interrupt!
    resume_signal = interrupt(approval_payload)

    # === RESUMED EXECUTION STARTS HERE ===
    decision = "APPROVE"
    if isinstance(resume_signal, dict):
        decision = resume_signal.get("action", "APPROVE").upper()
    elif isinstance(resume_signal, str):
        decision = resume_signal.upper()

    db = SessionLocal()
    try:
        repo = BusinessRepository(db)
        is_approved = (decision == "APPROVE" or decision == "APPROVED")
        new_status = "APPROVED" if is_approved else "REJECTED"

        repo.create_approval_request({
            "execution_id": exec_id,
            "task_id": task_id,
            "action_description": approval_payload["action_description"],
            "requesting_agent": approval_payload["requesting_agent"],
            "status": new_status,
            "decided_at": datetime.utcnow()
        })

        AuditLogger.log(
            db,
            event_type="APPROVAL_DECIDED",
            agent_name="Human Owner (Sharma Ji)",
            details=f"Task {task_id} {new_status} by business owner.",
            execution_id=exec_id
        )

        active_task["approval_status"] = new_status
        if not is_approved:
            active_task["status"] = "REJECTED"
            active_task["execution_result"] = "Rejected by store owner."
            repo.create_or_update_task({
                "execution_id": exec_id,
                "task_id": task_id,
                "task_name": task_name,
                "assigned_agent": active_task.get("assigned_agent", "Supervisor"),
                "status": "REJECTED",
                "execution_result": "Rejected by store owner."
            })
            return {
                "active_task": active_task,
                "approval_result": {"status": "REJECTED", "task_id": task_id},
                "current_status": "EXECUTING",
                "current_agent": "Supervisor",
                "current_task": f"Task {task_id} was rejected; resuming supervisor coordination"
            }

        active_task["status"] = "IN_PROGRESS"
        return {
            "active_task": active_task,
            "approval_result": {"status": "APPROVED", "task_id": task_id},
            "current_status": "EXECUTING",
            "current_agent": active_task.get("assigned_agent", "Supervisor"),
            "current_task": f"Approved: executing {task_name}"
        }
    finally:
        db.close()


def agent_execution_node(state: DukaandostState) -> Dict[str, Any]:
    active_task = state.get("active_task")
    if not active_task:
        return {"active_task": None}

    db = SessionLocal()
    try:
        exec_id = state.get("execution_id", "EXEC_INIT")
        supervisor = SupervisorAgent(db)

        # Dispatch execution to specialized agent
        result = supervisor.execute_specialized_task(active_task)

        sim_impact = result.get("simulated_impact", active_task.get("expected_impact", 0.0))
        active_task["simulated_impact"] = sim_impact
        active_task["execution_result"] = str(result)
        active_task["status"] = "EXECUTED"

        AuditLogger.log(
            db,
            event_type="AGENT_EXECUTION_COMPLETED",
            agent_name=active_task.get("assigned_agent", "Specialized Agent"),
            details=f"Executed task {active_task['task_id']}. Simulated Impact: +₹{sim_impact:.2f}",
            execution_id=exec_id
        )

        return {
            "active_task": active_task,
            "current_status": "VALIDATING",
            "current_agent": "Supervisor",
            "current_task": f"Validating results of {active_task['task_id']}"
        }
    finally:
        db.close()


def result_validation_node(state: DukaandostState) -> Dict[str, Any]:
    active_task = state.get("active_task")
    if not active_task:
        return {"active_task": None}

    expected = active_task.get("expected_impact", 0.0)
    simulated = active_task.get("simulated_impact", 0.0)
    variance = round(simulated - expected, 2)
    active_task["variance"] = variance

    return {
        "active_task": active_task,
        "current_status": "UPDATING_METRICS",
        "current_agent": "Supervisor"
    }


def business_metric_update_node(state: DukaandostState) -> Dict[str, Any]:
    active_task = state.get("active_task")
    if not active_task:
        return {"active_task": None}

    exec_id = state.get("execution_id", "EXEC_INIT")
    simulated_impact = active_task.get("simulated_impact", 0.0)

    curr_sim_income = state.get("simulated_income", state.get("initial_income", 8000.0))
    new_sim_income = round(curr_sim_income + simulated_impact, 2)

    active_task["status"] = "COMPLETED"

    completed = list(state.get("completed_tasks", []))
    # Idempotency check before appending
    if not any(t["task_id"] == active_task["task_id"] for t in completed):
        completed.append(active_task)

    # Sync to DB
    db = SessionLocal()
    try:
        repo = BusinessRepository(db)
        repo.create_or_update_task({
            "execution_id": exec_id,
            "task_id": active_task["task_id"],
            "task_name": active_task["task_name"],
            "assigned_agent": active_task["assigned_agent"],
            "status": "COMPLETED",
            "simulated_impact": simulated_impact,
            "execution_result": str(active_task.get("execution_result", ""))
        })
        AuditLogger.log(
            db,
            event_type="BUSINESS_METRIC_UPDATED",
            agent_name="Supervisor",
            details=f"Updated simulated income to ₹{new_sim_income:.2f} (+₹{simulated_impact:.2f} from {active_task['task_id']}).",
            execution_id=exec_id
        )
    finally:
        db.close()

    return {
        "simulated_income": new_sim_income,
        "completed_tasks": completed,
        "active_task": active_task,
        "current_status": "EVALUATING",
        "current_agent": "Supervisor",
        "current_task": f"Evaluating performance feedback for {active_task['task_id']}"
    }


def feedback_evaluation_node(state: DukaandostState) -> Dict[str, Any]:
    active_task = state.get("active_task")
    if not active_task:
        return {"active_task": None}

    expected = active_task.get("expected_impact", 0.0)
    simulated = active_task.get("simulated_impact", 0.0)
    variance = active_task.get("variance", 0.0)

    feedback_list = list(state.get("feedback", []))
    feedback_entry = {
        "task_id": active_task["task_id"],
        "strategy": active_task["task_name"],
        "expected_impact": expected,
        "simulated_impact": simulated,
        "variance": variance,
        "learning": (
            f"Strategy achieved {round((simulated/expected)*100, 1)}% of projection. "
            f"Market uptake realistic; prioritize complementary high-velocity staples in subsequent replenishment."
            if expected > 0 else "Neutral baseline impact."
        ),
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }
    feedback_list.append(feedback_entry)

    db = SessionLocal()
    try:
        AuditLogger.log(
            db,
            event_type="FEEDBACK_RECORDED",
            agent_name="Supervisor",
            details=f"Variance recorded for {active_task['task_id']}: ₹{variance:.2f}. Adaptive priorities updated.",
            execution_id=state.get("execution_id", "EXEC_INIT")
        )
    finally:
        db.close()

    return {
        "feedback": feedback_list,
        "active_task": None, # Clean active task
        "current_status": "EXECUTING",
        "current_agent": "Supervisor",
        "current_task": "Selecting next prioritized task"
    }


def handle_failure_node(state: DukaandostState) -> Dict[str, Any]:
    active_task = state.get("active_task")
    failed_list = list(state.get("failed_tasks", []))
    if active_task and not any(t["task_id"] == active_task["task_id"] for t in failed_list):
        failed_list.append(active_task)

    db = SessionLocal()
    try:
        AuditLogger.log(
            db,
            event_type="FAILURE_HANDLED",
            agent_name="Supervisor",
            details=f"Supervisor registered failure for task {active_task.get('task_id') if active_task else 'UNKNOWN'}. Strategy isolated, proceeding with remaining viable tasks.",
            execution_id=state.get("execution_id", "EXEC_INIT")
        )
    finally:
        db.close()

    return {
        "failed_tasks": failed_list,
        "active_task": None,
        "current_status": "EXECUTING",
        "current_agent": "Supervisor",
        "current_task": "Isolated failure, continuing remaining queue"
    }


def replanning_or_completion_node(state: DukaandostState) -> Dict[str, Any]:
    simulated_income = state.get("simulated_income", 8000.0)
    target_income = state.get("target_income", 10000.0)
    completed = state.get("completed_tasks", [])
    failed = state.get("failed_tasks", [])

    total_added = round(simulated_income - state.get("initial_income", 8000.0), 2)
    success_rate = round(len(completed) / (len(completed) + len(failed)) * 100, 1) if (completed or failed) else 100.0

    perf = {
        "initial_income": state.get("initial_income", 8000.0),
        "target_income": target_income,
        "simulated_income": simulated_income,
        "total_added_profit": total_added,
        "goal_achieved": simulated_income >= target_income,
        "tasks_completed": len(completed),
        "tasks_failed": len(failed),
        "success_rate_pct": success_rate
    }

    db = SessionLocal()
    try:
        exec_id = state.get("execution_id", "EXEC_INIT")
        AuditLogger.log(
            db,
            event_type="WORKFLOW_COMPLETED",
            agent_name="Supervisor",
            details=f"Growth cycle complete. Income moved from ₹{perf['initial_income']:.2f} to ₹{perf['simulated_income']:.2f} (+₹{total_added:.2f}). Goal Achieved: {perf['goal_achieved']}.",
            execution_id=exec_id
        )
        repo = BusinessRepository(db)
        repo.create_or_update_execution({
            "execution_id": exec_id,
            "thread_id": state.get("thread_id", exec_id),
            "status": "COMPLETED",
            "simulated_income": simulated_income,
            "variance": total_added,
            "current_agent": "Supervisor",
            "current_task": "Cycle Completed Successfully",
            "completed_at": datetime.utcnow()
        })
    finally:
        db.close()

    return {
        "current_status": "COMPLETED",
        "current_agent": "Supervisor",
        "current_task": "Growth cycle finalized",
        "performance_metrics": perf
    }
