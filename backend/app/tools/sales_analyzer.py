from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.database.models import Transaction, Product, Expense

class SalesAnalyzer:
    @staticmethod
    def analyze_sales_performance(db: Session) -> Dict[str, Any]:
        """
        Calculates store financial figures, category performance, and velocity.
        """
        total_rev = db.query(func.sum(Transaction.total_amount)).scalar() or 0.0
        total_cogs = db.query(func.sum(Transaction.cost_amount)).scalar() or 0.0
        total_exp = db.query(func.sum(Expense.amount)).scalar() or 0.0
        
        gross_profit = round(total_rev - total_cogs, 2)
        net_income = round(gross_profit - total_exp, 2)
        gross_margin_pct = round((gross_profit / total_rev * 100.0), 2) if total_rev > 0 else 0.0

        # Top 5 products by revenue
        top_prods_query = (
            db.query(
                Product.product_id,
                Product.product_name,
                Product.category,
                func.sum(Transaction.quantity).label("units_sold"),
                func.sum(Transaction.total_amount).label("total_sales"),
                func.sum(Transaction.gross_profit).label("total_profit")
            )
            .join(Transaction, Product.product_id == Transaction.product_id)
            .group_by(Product.product_id)
            .order_by(desc("total_sales"))
            .limit(5)
            .all()
        )

        top_products = [
            {
                "product_id": r.product_id,
                "product_name": r.product_name,
                "category": r.category,
                "units_sold": int(r.units_sold),
                "total_sales": round(float(r.total_sales), 2),
                "total_profit": round(float(r.total_profit), 2)
            }
            for r in top_prods_query
        ]

        # Category sales distribution
        cat_query = (
            db.query(
                Product.category,
                func.sum(Transaction.total_amount).label("category_sales"),
                func.sum(Transaction.gross_profit).label("category_profit")
            )
            .join(Transaction, Product.product_id == Transaction.product_id)
            .group_by(Product.category)
            .all()
        )

        category_breakdown = [
            {
                "category": r.category,
                "sales": round(float(r.category_sales), 2),
                "profit": round(float(r.category_profit), 2),
                "margin_pct": round((float(r.category_profit) / float(r.category_sales) * 100), 1) if float(r.category_sales) > 0 else 0.0
            }
            for r in cat_query
        ]

        # 30-Day Daily Sales & Profit Trend from actual database records
        daily_query = (
            db.query(
                Transaction.transaction_date,
                func.sum(Transaction.total_amount).label("daily_sales"),
                func.sum(Transaction.gross_profit).label("daily_profit")
            )
            .group_by(Transaction.transaction_date)
            .order_by(Transaction.transaction_date.asc())
            .all()
        )

        daily_trends = [
            {
                "date": r.transaction_date.strftime("%d %b") if hasattr(r.transaction_date, "strftime") else str(r.transaction_date)[5:],
                "sales": round(float(r.daily_sales), 2),
                "profit": round(float(r.daily_profit), 2)
            }
            for r in daily_query
        ]

        return {
            "revenue": round(total_rev, 2),
            "cogs": round(total_cogs, 2),
            "operating_expenses": round(total_exp, 2),
            "gross_profit": gross_profit,
            "net_income": net_income,
            "gross_margin_pct": gross_margin_pct,
            "top_products": top_products,
            "category_breakdown": category_breakdown,
            "daily_trends": daily_trends
        }
