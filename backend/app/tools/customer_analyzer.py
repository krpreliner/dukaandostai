from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.models import Customer

class CustomerAnalyzer:
    @staticmethod
    def analyze_customers(db: Session) -> Dict[str, Any]:
        """
        Segments customers and highlights churn risks and reactivation pools.
        """
        customers = db.query(Customer).all()
        total_customers = len(customers)

        segments_count = {}
        inactive_customers = []
        at_risk_customers = []

        total_aov = 0.0
        for c in customers:
            segments_count[c.segment] = segments_count.get(c.segment, 0) + 1
            total_aov += c.average_order_value
            if c.segment == "Inactive":
                inactive_customers.append({
                    "customer_id": c.customer_id,
                    "customer_name": c.customer_name,
                    "area": c.area,
                    "last_purchase_date": c.last_purchase_date,
                    "preferred_category": c.preferred_category,
                    "average_order_value": c.average_order_value
                })
            elif c.segment == "At Risk":
                at_risk_customers.append({
                    "customer_id": c.customer_id,
                    "customer_name": c.customer_name,
                    "area": c.area,
                    "last_purchase_date": c.last_purchase_date,
                    "preferred_category": c.preferred_category,
                    "average_order_value": c.average_order_value
                })

        avg_aov = round(total_aov / total_customers, 2) if total_customers > 0 else 0.0

        return {
            "total_customers": total_customers,
            "average_aov": avg_aov,
            "segments_breakdown": segments_count,
            "inactive_count": len(inactive_customers),
            "at_risk_count": len(at_risk_customers),
            "inactive_sample": inactive_customers[:10],
            "at_risk_sample": at_risk_customers[:10]
        }
