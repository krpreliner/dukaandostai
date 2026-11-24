from typing import Dict, Any, List

class StrategyPlannerAgent:
    """
    Agent 2: Strategy Planner Agent
    Responsibilities:
    - Receive Business Analyst findings
    - Structure profitable growth plan to bridge the net income gap
    - Prioritise tasks and assign to specialised agents
    - Tag risk levels and human approval requirements
    """
    def __init__(self):
        pass

    def run(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        income_gap = analysis.get("income_gap", 2000.0)

        # Build prioritized actionable tasks
        tasks = [
            {
                "task_id": "TASK_001",
                "task_name": "Launch Breakfast Combo (Bread + Butter)",
                "assigned_agent": "Marketing Agent",
                "priority": "HIGH",
                "expected_impact": 440.0,
                "simulated_impact": 0.0,
                "risk_level": "MEDIUM",
                "approval_required": True, # Bundle promotional pricing requires owner approval
                "status": "PENDING",
                "execution_result": "",
                "details": {
                    "bundle_name": "Sharma Ji Special Breakfast Combo (Bread + Butter)",
                    "products": ["PROD002", "PROD003"], # Bread + Butter
                    "discount_pct": 5.22, # ₹115 down to ₹109
                    "target_units": 40
                }
            },
            {
                "task_id": "TASK_002",
                "task_name": "Reactivate 25 Dormant Kirana Customers",
                "assigned_agent": "Marketing Agent",
                "priority": "HIGH",
                "expected_impact": 810.0,
                "simulated_impact": 0.0,
                "risk_level": "LOW",
                "approval_required": False, # Standard personalized staple coupon within policy
                "status": "PENDING",
                "execution_result": "",
                "details": {
                    "target_segment": "Inactive",
                    "inactive_count": analysis["customer_insights"]["inactive_count"],
                    "discount_pct": 8.0,
                    "avg_basket": 450.0
                }
            },
            {
                "task_id": "TASK_003",
                "task_name": "Liquidate Perishable Sudha Paneer Before Expiry",
                "assigned_agent": "Inventory Agent",
                "priority": "MEDIUM",
                "expected_impact": 418.0,
                "simulated_impact": 0.0,
                "risk_level": "LOW",
                "approval_required": False,
                "status": "PENDING",
                "execution_result": "",
                "details": {
                    "product_id": "PROD005",
                    "product_name": "Sudha Special Fresh Paneer 200g",
                    "discount_pct": 10.0,
                    "stock_units": 14
                }
            },
            {
                "task_id": "TASK_004",
                "task_name": "Restock High Velocity Staples (Bread & Eggs)",
                "assigned_agent": "Inventory Agent",
                "priority": "HIGH",
                "expected_impact": 480.0,
                "simulated_impact": 0.0,
                "risk_level": "MEDIUM",
                "approval_required": True, # Inventory procurement requires human sign-off
                "status": "PENDING",
                "execution_result": "",
                "details": {
                    "products_to_restock": ["PROD002", "PROD004"],
                    "reorder_units": 50
                }
            }
        ]

        return tasks
