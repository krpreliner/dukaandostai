from typing import TypedDict, List, Dict, Any, Optional

class DukaandostState(TypedDict, total=False):
    execution_id: str
    thread_id: str
    business_goal: str
    initial_income: float
    target_income: float
    current_income: float
    simulated_income: float
    business_analysis: Dict[str, Any]
    execution_plan: List[Dict[str, Any]]
    task_queue: List[Dict[str, Any]]
    completed_tasks: List[Dict[str, Any]]
    failed_tasks: List[Dict[str, Any]]
    pending_tasks: List[Dict[str, Any]]
    pending_approval: Optional[Dict[str, Any]]
    approval_result: Optional[Dict[str, Any]]
    execution_history: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]
    feedback: List[Dict[str, Any]]
    current_status: str
    current_agent: str
    current_task: str
    active_task: Optional[Dict[str, Any]]
    iteration_count: int
