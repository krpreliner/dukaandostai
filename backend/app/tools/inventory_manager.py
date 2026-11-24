from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from app.database.models import Product

class InventoryManager:
    @staticmethod
    def analyze_inventory(db: Session) -> Dict[str, Any]:
        """
        Detects stockout risks, slow-moving items, and expiry risks.
        """
        products = db.query(Product).all()
        low_stock = []
        slow_moving = []
        expiring_soon = []
        healthy = []

        total_inventory_value = 0.0

        for p in products:
            item_val = round(p.current_stock * p.cost_price, 2)
            total_inventory_value += item_val

            info = {
                "product_id": p.product_id,
                "product_name": p.product_name,
                "category": p.category,
                "cost_price": p.cost_price,
                "selling_price": p.selling_price,
                "margin_pct": round((p.selling_price - p.cost_price) / p.selling_price * 100, 1),
                "current_stock": p.current_stock,
                "minimum_stock": p.minimum_stock,
                "monthly_units_sold": p.monthly_units_sold,
                "expiry_date": p.expiry_date,
                "status": p.status
            }

            if p.current_stock <= p.minimum_stock:
                low_stock.append(info)
            if p.status == "SLOW MOVING" or (p.monthly_units_sold < 30 and p.current_stock > 15):
                slow_moving.append(info)
            if p.status == "EXPIRING SOON":
                expiring_soon.append(info)
            if p.status == "HEALTHY":
                healthy.append(info)

        return {
            "total_products": len(products),
            "total_inventory_value": round(total_inventory_value, 2),
            "low_stock_count": len(low_stock),
            "slow_moving_count": len(slow_moving),
            "expiring_soon_count": len(expiring_soon),
            "low_stock_items": low_stock,
            "slow_moving_items": slow_moving,
            "expiring_soon_items": expiring_soon
        }
