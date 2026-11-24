from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.tools.profit_calculator import ProfitCalculator
from app.config import settings

class FinanceAgent:
    """
    Agent 5: Finance Agent
    Responsibilities:
    - Independent deterministic financial gatekeeper
    - Enforce business margin policies & maximum discount caps (15%)
    - Strictly block any action yielding negative gross margin or invalid pricing
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
        If task involves negative margin, invalid pricing, or policy breach,
        immediately blocks execution with actionable financial reasoning.
        """
        task_id = task.get("task_id", "")
        task_name = task.get("task_name", "")
        details = task.get("details", {})
        from app.database.models import Product

        # 1. Product Bundling Validation
        if "bundle_name" in details or "products" in details:
            prod_ids = details.get("products", [])
            products = self.db.query(Product).filter(Product.product_id.in_(prod_ids)).all()

            if len(products) != len(prod_ids):
                missing = set(prod_ids) - {p.product_id for p in products}
                return {
                    "is_approved": False,
                    "error_type": "MISSING_PRODUCT_INVENTORY",
                    "message": f"Inventory verification failed: Products {missing} not found in catalog."
                }

            # Check individual product margins and invalid pricing
            for p in products:
                if p.cost_price <= 0:
                    return {
                        "is_approved": False,
                        "error_type": "INVALID_PRODUCT_COST",
                        "product_id": p.product_id,
                        "message": f"FINANCIAL VALIDATION FAILED: Product '{p.product_name}' has non-positive cost price ₹{p.cost_price:.2f}."
                    }
                if p.selling_price <= 0:
                    return {
                        "is_approved": False,
                        "error_type": "INVALID_SELLING_PRICE",
                        "product_id": p.product_id,
                        "message": f"FINANCIAL VALIDATION FAILED: Product '{p.product_name}' has non-positive selling price ₹{p.selling_price:.2f}."
                    }
                if p.selling_price < p.cost_price:
                    loss = round(p.cost_price - p.selling_price, 2)
                    return {
                        "is_approved": False,
                        "error_type": "NEGATIVE_GROSS_MARGIN",
                        "product_id": p.product_id,
                        "product_name": p.product_name,
                        "cost_price": p.cost_price,
                        "selling_price": p.selling_price,
                        "loss_per_unit": loss,
                        "message": (
                            f"FINANCIAL VALIDATION FAILED: Product '{p.product_name}' has cost price ₹{p.cost_price:.2f} "
                            f"exceeding selling price ₹{p.selling_price:.2f} (Loss: -₹{loss:.2f}/unit). "
                            f"Promotions on negative-margin products are strictly prohibited."
                        )
                    }

            # Check bundle level discount and margin
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

        # 2. Inventory Clearance Validation
        elif "product_id" in details and "stock_units" in details:
            p = self.db.query(Product).filter_by(product_id=details.get("product_id")).first()
            if not p:
                return {
                    "is_approved": False,
                    "error_type": "PRODUCT_NOT_FOUND",
                    "message": f"Product '{details.get('product_id')}' not found for clearance."
                }
            if p.selling_price < p.cost_price:
                return {
                    "is_approved": False,
                    "error_type": "NEGATIVE_GROSS_MARGIN",
                    "product_id": p.product_id,
                    "message": f"Cannot clear product {p.product_name} at negative base margin."
                }
            if details.get("stock_units", 0) <= 0:
                return {
                    "is_approved": False,
                    "error_type": "INSUFFICIENT_INVENTORY",
                    "message": f"No inventory units available to liquidate for {p.product_name}."
                }
            return {"is_approved": True}

        # 3. Restocking Validation
        elif "products_to_restock" in details:
            reorder_units = details.get("reorder_units", 0)
            if reorder_units <= 0:
                return {
                    "is_approved": False,
                    "error_type": "INVALID_REORDER_QUANTITY",
                    "message": "Restock replenishment quantity must be greater than zero."
                }
            return {"is_approved": True}

        # 4. Customer Reactivation Validation
        elif "inactive_count" in details:
            discount_pct = details.get("discount_pct", 8.0)
            if discount_pct > self.max_discount:
                return {
                    "is_approved": False,
                    "error_type": "DISCOUNT_CEILING_EXCEEDED",
                    "message": f"Reactivation discount {discount_pct}% exceeds policy cap {self.max_discount}%."
                }
            return {"is_approved": True}

        return {"is_approved": True}
