from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.database.repository import BusinessRepository
from app.data.synthetic_data.generator import seed_database
from app.tools.sales_analyzer import SalesAnalyzer
from app.tools.customer_analyzer import CustomerAnalyzer
from app.tools.inventory_manager import InventoryManager
from app.config import settings

class BusinessService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = BusinessRepository(db)

    def get_overview(self) -> Dict[str, Any]:
        fin = self.repo.get_financial_summary()
        customers = self.repo.get_customers()
        products = self.repo.get_products()
        latest_exec = self.repo.get_latest_execution()

        initial_income = settings.INITIAL_NET_INCOME
        target_income = settings.TARGET_NET_INCOME
        current_calculated = fin["net_income"]

        simulated_income = latest_exec.simulated_income if latest_exec else current_calculated
        simulated_improvement = round(simulated_income - initial_income, 2)
        percentage_achieved = round(min(100.0, max(0.0, (simulated_income - initial_income) / (target_income - initial_income) * 100)), 1) if (target_income > initial_income) else 100.0

        return {
            "store_name": settings.STORE_NAME,
            "store_location": settings.STORE_LOCATION,
            "store_owner": settings.STORE_OWNER,
            "initial_net_income": initial_income,
            "target_net_income": target_income,
            "current_net_income": current_calculated,
            "simulated_net_income": simulated_income,
            "simulated_improvement": simulated_improvement,
            "percentage_achieved": percentage_achieved,
            "income_gap": max(0.0, round(target_income - simulated_income, 2)),
            "revenue": fin["revenue"],
            "cogs": fin["cogs"],
            "gross_profit": fin["gross_profit"],
            "operating_expenses": fin["operating_expenses"],
            "total_customers": len(customers),
            "total_products": len(products),
            "worker_status": latest_exec.status if latest_exec else "IDLE",
            "active_execution_id": latest_exec.execution_id if latest_exec else None
        }

    def get_analytics(self) -> Dict[str, Any]:
        sales = SalesAnalyzer.analyze_sales_performance(self.db)
        custs = CustomerAnalyzer.analyze_customers(self.db)
        inv = InventoryManager.analyze_inventory(self.db)
        expenses = self.repo.get_expenses_breakdown()

        return {
            "sales_analytics": sales,
            "customer_analytics": custs,
            "inventory_analytics": inv,
            "expenses_breakdown": expenses
        }

    def get_customers(self, segment: Optional[str] = None) -> List[Dict[str, Any]]:
        customers = self.repo.get_customers(segment)
        return [
            {
                "customer_id": c.customer_id,
                "customer_name": c.customer_name,
                "area": c.area,
                "age_group": c.age_group,
                "total_orders": c.total_orders,
                "total_spending": c.total_spending,
                "last_purchase_date": c.last_purchase_date,
                "preferred_category": c.preferred_category,
                "average_order_value": c.average_order_value,
                "segment": c.segment
            }
            for c in customers
        ]

    def get_products(self, category: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        products = self.repo.get_products(category, status)
        return [
            {
                "product_id": p.product_id,
                "product_name": p.product_name,
                "category": p.category,
                "cost_price": p.cost_price,
                "selling_price": p.selling_price,
                "current_stock": p.current_stock,
                "minimum_stock": p.minimum_stock,
                "monthly_units_sold": p.monthly_units_sold,
                "expiry_date": p.expiry_date,
                "supplier_name": p.supplier_name,
                "profit_margin": round((p.selling_price - p.cost_price) / p.selling_price * 100, 1) if p.selling_price > 0 else 0.0,
                "status": p.status
            }
            for p in products
        ]

    def reset_synthetic_data(self) -> Dict[str, Any]:
        seed_database(self.db, force_reset=True)
        return {"status": "SUCCESS", "message": "Synthetic Kirana store records successfully reset."}
