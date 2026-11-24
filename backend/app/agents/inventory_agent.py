from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.database.models import Product
from app.tools.inventory_manager import InventoryManager
from app.tools.promotion_simulator import PromotionSimulator

class InventoryAgent:
    """
    Agent 4: Inventory Agent
    Responsibilities:
    - Identify low stock & stockout vulnerability
    - Detect expiry risks & slow moving dead capital
    - Propose replenishment quantities and markdown liquidation
    - Strictly simulated; no external orders placed.
    """
    def __init__(self, db: Session):
        self.db = db

    def check_health(self) -> Dict[str, Any]:
        return InventoryManager.analyze_inventory(self.db)

    def execute_clearance_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        details = task.get("details", {})
        pid = details.get("product_id", "PROD005") # Sudha Paneer
        p = self.db.query(Product).filter_by(product_id=pid).first()

        cost_price = p.cost_price if p else 80.0
        selling_price = p.selling_price if p else 95.0
        stock = p.current_stock if p else 14
        pname = p.product_name if p else "Sudha Special Fresh Paneer 200g"

        discount_pct = details.get("discount_pct", 10.0)

        sim_res = PromotionSimulator.simulate_inventory_clearance(
            product_name=pname,
            cost_price=cost_price,
            regular_price=selling_price,
            stock_units=stock,
            clearance_discount_pct=discount_pct
        )
        return sim_res

    def execute_restock_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        details = task.get("details", {})
        pids = details.get("products_to_restock", ["PROD002", "PROD004"])
        prods = self.db.query(Product).filter(Product.product_id.in_(pids)).all()
        prod_dicts = [
            {"product_id": p.product_id, "name": p.product_name, "stock": p.current_stock, "min": p.minimum_stock}
            for p in prods
        ]

        sim_res = PromotionSimulator.simulate_stockout_prevention(prod_dicts)
        sim_res["restocked_products"] = prod_dicts
        return sim_res
