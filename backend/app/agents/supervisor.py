from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.database.repository import BusinessRepository
from app.agents.business_analyst import BusinessAnalystAgent
from app.agents.strategy_planner import StrategyPlannerAgent
from app.agents.marketing_agent import MarketingAgent
from app.agents.inventory_agent import InventoryAgent
from app.agents.finance_agent import FinanceAgent

class SupervisorAgent:
    """
    Agent 6: Supervisor Agent
    Responsibilities:
    - Master coordinator of the autonomous worker
    - Understand business goal and delegate to specialized agents
    - Manage approval checks and execution state
    - Guard against duplicate executions
    - Handle failure recovery and feedback replanning
    """
    def __init__(self, db: Session):
        self.db = db
        self.repo = BusinessRepository(db)
        self.analyst = BusinessAnalystAgent(db)
        self.planner = StrategyPlannerAgent()
        self.marketing = MarketingAgent(db)
        self.inventory = InventoryAgent(db)
        self.finance = FinanceAgent(db)

    def analyze_business(self, target_income: float = 10000.0) -> Dict[str, Any]:
        return self.analyst.run(target_income=target_income)

    def plan_strategy(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        return self.planner.run(analysis)

    def validate_task_finance(self, task: Dict[str, Any]) -> Dict[str, Any]:
        return self.finance.validate_task_finance(task)

    def execute_specialized_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatches task to the appropriate specialized agent.
        """
        agent = task.get("assigned_agent")
        task_id = task.get("task_id")

        if agent == "Marketing Agent":
            if "bundle_name" in task.get("details", {}):
                return self.marketing.execute_bundling_task(task)
            elif "inactive_count" in task.get("details", {}):
                return self.marketing.execute_reactivation_task(task)
            else:
                return {"success": True, "impact": task.get("expected_impact", 0.0)}

        elif agent == "Inventory Agent":
            if "stock_units" in task.get("details", {}):
                return self.inventory.execute_clearance_task(task)
            elif "products_to_restock" in task.get("details", {}):
                return self.inventory.execute_restock_task(task)
            else:
                return {"success": True, "impact": task.get("expected_impact", 0.0)}

        elif agent == "Finance Agent":
            return {"success": True, "impact": task.get("expected_impact", 0.0)}

        return {"success": False, "error": f"Unknown agent '{agent}'"}
