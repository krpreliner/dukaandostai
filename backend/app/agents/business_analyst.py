from typing import Dict, Any
from sqlalchemy.orm import Session
from app.tools.sales_analyzer import SalesAnalyzer
from app.tools.customer_analyzer import CustomerAnalyzer
from app.tools.inventory_manager import InventoryManager

class BusinessAnalystAgent:
    """
    Agent 1: Business Analyst Agent
    Responsibilities:
    - Understand business goal
    - Analyze customer data, transaction history, product performance
    - Calculate revenue, expenses, net income, income gap
    - Detect inactive customers, slow-moving inventory, growth opportunities
    """
    def __init__(self, db: Session):
        self.db = db

    def run(self, target_income: float = 10000.0) -> Dict[str, Any]:
        sales = SalesAnalyzer.analyze_sales_performance(self.db)
        customers = CustomerAnalyzer.analyze_customers(self.db)
        inventory = InventoryManager.analyze_inventory(self.db)

        current_income = sales["net_income"]
        income_gap = max(0.0, round(target_income - current_income, 2))

        # Identified Growth Opportunities
        growth_opportunities = [
            {
                "id": "OPP_01",
                "title": "High Margin Breakfast Bundles",
                "description": "Combine daily bread with butter/spreads to increase average basket order value.",
                "potential_profit": 440.0,
                "domain": "marketing"
            },
            {
                "id": "OPP_02",
                "title": "Dormant Customer Reactivation Campaign",
                "description": f"Engage {customers['inactive_count']} inactive customers with personalized staple grocery vouchers.",
                "potential_profit": 810.0,
                "domain": "marketing"
            },
            {
                "id": "OPP_03",
                "title": "Perishable Stock Clearance",
                "description": f"Expedite liquidation of {inventory['expiring_soon_count']} perishable items (Paneer) to prevent inventory write-off.",
                "potential_profit": 418.0,
                "domain": "inventory"
            },
            {
                "id": "OPP_04",
                "title": "Stockout Prevention for Daily Staples",
                "description": f"Replenish {inventory['low_stock_count']} fast-moving low-stock items (Bread, Eggs) to prevent missed daily footfall sales.",
                "potential_profit": 480.0,
                "domain": "inventory"
            }
        ]

        business_risks = [
            f"{inventory['low_stock_count']} essential products currently under minimum stock threshold.",
            f"{customers['inactive_count']} customers have not made any purchase in over 45 days.",
            f"Gross margin in competitive staples is compressed; discount offers must strictly protect gross margins."
        ]

        return {
            "current_income": current_income,
            "target_income": target_income,
            "income_gap": income_gap,
            "revenue": sales["revenue"],
            "expenses": sales["operating_expenses"],
            "gross_profit": sales["gross_profit"],
            "gross_margin_pct": sales["gross_margin_pct"],
            "customer_insights": customers,
            "product_insights": {
                "top_products": sales["top_products"],
                "inventory": inventory
            },
            "growth_opportunities": growth_opportunities,
            "business_risks": business_risks
        }
