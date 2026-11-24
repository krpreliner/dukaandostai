from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.database.models import TaskRecord, ApprovalRecord, FailureRecord, ExecutionRecord
from app.config import settings

class EvaluationService:
    def __init__(self, db: Session):
        self.db = db

    def evaluate_system(self, execution_id: str = None) -> Dict[str, Any]:
        task_q = self.db.query(TaskRecord)
        app_q = self.db.query(ApprovalRecord)
        fail_q = self.db.query(FailureRecord)
        exec_q = self.db.query(ExecutionRecord)

        if execution_id:
            task_q = task_q.filter_by(execution_id=execution_id)
            app_q = app_q.filter_by(execution_id=execution_id)
            fail_q = fail_q.filter_by(execution_id=execution_id)
            exec_q = exec_q.filter_by(execution_id=execution_id)

        tasks = task_q.all()
        approvals = app_q.all()
        failures = fail_q.all()
        executions = exec_q.all()

        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.status == "COMPLETED")
        failed_tasks = sum(1 for t in tasks if t.status in ["FAILED", "REJECTED"])

        completion_rate = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0.0
        failure_rate = round((failed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0.0

        # Approval metrics
        total_approvals = len(approvals)
        approved_count = sum(1 for a in approvals if a.status == "APPROVED")
        rejected_count = sum(1 for a in approvals if a.status == "REJECTED")
        approval_rate = round((approved_count / total_approvals * 100), 1) if total_approvals > 0 else 0.0

        # Recovery rate
        total_failures = len(failures)
        recovered_count = sum(1 for f in failures if f.recovery_status == "RESOLVED")
        recovery_rate = round((recovered_count / total_failures * 100), 1) if total_failures > 0 else 100.0

        # Financial accuracy: Expected vs Simulated Profit
        total_expected = round(sum(t.expected_impact for t in tasks if t.status == "COMPLETED"), 2)
        total_simulated = round(sum(t.simulated_impact for t in tasks if t.status == "COMPLETED"), 2)
        profit_variance = round(total_simulated - total_expected, 2)

        # Baseline vs Target vs Simulated Net Income
        latest_exec = executions[-1] if executions else None
        sim_income = latest_exec.simulated_income if latest_exec else settings.INITIAL_NET_INCOME
        income_improvement = round(sim_income - settings.INITIAL_NET_INCOME, 2)
        target_achievement_pct = round((income_improvement / settings.REQUIRED_GROWTH) * 100, 1)

        # Duplicate execution prevention
        task_id_counts = {}
        for t in tasks:
            task_id_counts[t.task_id] = task_id_counts.get(t.task_id, 0) + 1
        duplicate_prevented = all(c <= 1 for c in task_id_counts.values())

        return {
            "execution_id": execution_id,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "completion_rate_pct": completion_rate,
            "failure_rate_pct": failure_rate,
            "total_approval_requests": total_approvals,
            "approved_count": approved_count,
            "rejected_count": rejected_count,
            "approval_rate_pct": approval_rate,
            "total_failures": total_failures,
            "recovery_rate_pct": recovery_rate,
            "total_expected_profit": total_expected,
            "total_simulated_profit": total_simulated,
            "profit_variance": profit_variance,
            "initial_net_income": settings.INITIAL_NET_INCOME,
            "target_net_income": settings.TARGET_NET_INCOME,
            "simulated_net_income": sim_income,
            "income_improvement": income_improvement,
            "target_achievement_pct": target_achievement_pct,
            "duplicate_execution_prevented": duplicate_prevented
        }
