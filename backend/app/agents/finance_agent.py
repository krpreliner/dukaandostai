from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.tools.profit_calculator import ProfitCalculator
from app.config import settings

class FinanceAgent:
    """
    Agent 5: Finance Agent
    Responsibilities:
    - Independent deterministic financial gatekeeper
    - Enforce business margin policies & maximum discount caps
    - Strictly block any action yielding negative gross margin
    - Never allow LLMs or other agents to bypass validation
    """
    def __init__(self, db: Session):
        self.db = db
        self.max_discount = settings.MAX_PROMOTIONAL_DISCOUNT_PCT

    def validate_offer(
        self,
        cost_price: float,
        proposed_price: float,
        original_price: float
    ) -> Dict[str, Any]:
        """
        Validates an individual or bundle pricing proposal.
        """
        validation = ProfitCalculator.validate_pricing(
            cost_price=cost_price,
            proposed_price=proposed_price,
            original_price=original_price,
            max_discount_pct=self.max_discount
        )
        return validation

    def validate_task_finance(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interrogates a task before execution or approval request.
        If task involves negative margin (e.g. Butter test scenario),
        immediately blocks execution with actionable financial reasoning.
        """
        task_id = task.get("task_id", "")
        task_name = task.get("task_name", "")
        details = task.get("details", {})

        # If it's a bundling task
        if "bundle_name" in details:
            # Check products in bundle
            from app.database.models import Product
            products = self.db.query(Product).filter(
                Product.product_id.in_(details.get("products", []))
            ).all()

            # Check individual product margins first to prevent negative margin loss-leaders
            for p in products:
                if p.selling_price < p.cost_price:
                    return {
                        "is_approved": False,
                        "error_type": "NEGATIVE_GROSS_MARGIN",
                        "product_id": p.product_id,
                        "product_name": p.product_name,
                        "cost_price": p.cost_price,
                        "selling_price": p.selling_price,
                        "loss_per_unit": round(p.cost_price - p.selling_price, 2),
                        "message": (
                            f"FINANCIAL VALIDATION FAILED: Product '{p.product_name}' has cost price ₹{p.cost_price:.2f} "
                            f"exceeding selling price ₹{p.selling_price:.2f} (Loss: -₹{p.cost_price - p.selling_price:.2f}/unit). "
                            f"Promotions on negative-margin products are strictly prohibited."
                        )
                    }

            # Check bundle level
            orig_price = sum(p.selling_price for p in products)
            cost_price = sum(p.cost_price for p in products)
            discount_pct = details.get("discount_pct", 5.0)
            proposed_price = round(orig_price * (1.0 - discount_pct / 100.0), 2)

            val = self.validate_offer(cost_price, proposed_price, orig_price)
            if not val["is_valid"]:
                return {
                    "is_approved": False,
                    "error_type": "POLICY_VIOLATION",
                    "details": val,
                    "message": " ; ".join(val["reasons"])
                }

            return {
                "is_approved": True,
                "cost_price": cost_price,
                "original_price": orig_price,
                "proposed_price": proposed_price,
                "gross_margin_pct": val["gross_margin_pct"],
                "unit_profit": val["unit_profit"]
            }

        # If it's clearance
        elif "stock_units" in details:
            from app.database.models import Product
            p = self.db.query(Product).filter_by(product_id=details.get("product_id")).first()
            if p and p.selling_price < p.cost_price:
                return {
                    "is_approved": False,
                    "error_type": "NEGATIVE_GROSS_MARGIN",
                    "product_id": p.product_id,
                    "product_name": p.product_name,
                    "cost_price": p.cost_price,
                    "selling_price": p.selling_price,
                    "message": f"Cannot clear product {p.product_name} at negative base margin."
                }
            return {"is_approved": True}

        # Otherwise general valid task
        return {"is_approved": True}
