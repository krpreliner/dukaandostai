from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional, Dict, Any
from app.database.models import (
    Customer, Product, Transaction, Expense,
    ExecutionRecord, TaskRecord, ApprovalRecord, AuditLog, FailureRecord
)

class BusinessRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_financial_summary(self) -> Dict[str, float]:
        total_rev = self.db.query(func.sum(Transaction.total_amount)).scalar() or 0.0
        total_cogs = self.db.query(func.sum(Transaction.cost_amount)).scalar() or 0.0
        total_exp = self.db.query(func.sum(Expense.amount)).scalar() or 0.0
        gross_profit = total_rev - total_cogs
        net_income = gross_profit - total_exp
        return {
            "revenue": round(total_rev, 2),
            "cogs": round(total_cogs, 2),
            "gross_profit": round(gross_profit, 2),
            "operating_expenses": round(total_exp, 2),
            "net_income": round(net_income, 2)
        }

    def get_expenses_breakdown(self) -> List[Dict[str, Any]]:
        expenses = self.db.query(Expense).all()
        return [{"category": e.category, "amount": e.amount, "notes": e.notes} for e in expenses]

    def get_customers(self, segment: Optional[str] = None) -> List[Customer]:
        q = self.db.query(Customer)
        if segment:
            q = q.filter(Customer.segment == segment)
        return q.all()

    def get_customer_by_id(self, customer_id: str) -> Optional[Customer]:
        return self.db.query(Customer).filter(Customer.customer_id == customer_id).first()

    def get_products(self, category: Optional[str] = None, status: Optional[str] = None) -> List[Product]:
        q = self.db.query(Product)
        if category:
            q = q.filter(Product.category == category)
        if status:
            q = q.filter(Product.status == status)
        return q.all()

    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        return self.db.query(Product).filter(Product.product_id == product_id).first()

    def update_product_price(self, product_id: str, new_cost: Optional[float] = None, new_sell: Optional[float] = None) -> Optional[Product]:
        prod = self.get_product_by_id(product_id)
        if prod:
            if new_cost is not None:
                prod.cost_price = new_cost
            if new_sell is not None:
                prod.selling_price = new_sell
            self.db.commit()
            self.db.refresh(prod)
        return prod

    def get_transactions(self, limit: int = 100) -> List[Transaction]:
        return self.db.query(Transaction).order_by(desc(Transaction.id)).limit(limit).all()

    def create_or_update_execution(self, exec_data: Dict[str, Any]) -> ExecutionRecord:
        record = self.db.query(ExecutionRecord).filter_by(execution_id=exec_data["execution_id"]).first()
        if not record:
            record = ExecutionRecord(**exec_data)
            self.db.add(record)
        else:
            for k, v in exec_data.items():
                setattr(record, k, v)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_execution(self, execution_id: str) -> Optional[ExecutionRecord]:
        return self.db.query(ExecutionRecord).filter_by(execution_id=execution_id).first()

    def get_latest_execution(self) -> Optional[ExecutionRecord]:
        return self.db.query(ExecutionRecord).order_by(desc(ExecutionRecord.id)).first()

    def create_or_update_task(self, task_data: Dict[str, Any]) -> TaskRecord:
        record = self.db.query(TaskRecord).filter_by(
            execution_id=task_data["execution_id"],
            task_id=task_data["task_id"]
        ).first()
        if not record:
            record = TaskRecord(**task_data)
            self.db.add(record)
        else:
            for k, v in task_data.items():
                setattr(record, k, v)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_tasks_for_execution(self, execution_id: str) -> List[TaskRecord]:
        return self.db.query(TaskRecord).filter_by(execution_id=execution_id).all()

    def get_task_by_id(self, execution_id: str, task_id: str) -> Optional[TaskRecord]:
        return self.db.query(TaskRecord).filter_by(execution_id=execution_id, task_id=task_id).first()

    def create_approval_request(self, approval_data: Dict[str, Any]) -> ApprovalRecord:
        record = self.db.query(ApprovalRecord).filter_by(
            execution_id=approval_data["execution_id"],
            task_id=approval_data["task_id"]
        ).first()
        if not record:
            record = ApprovalRecord(**approval_data)
            self.db.add(record)
        else:
            for k, v in approval_data.items():
                setattr(record, k, v)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_pending_approvals(self, execution_id: Optional[str] = None) -> List[ApprovalRecord]:
        q = self.db.query(ApprovalRecord).filter_by(status="PENDING")
        if execution_id:
            q = q.filter_by(execution_id=execution_id)
        return q.all()

    def log_audit(self, event_type: str, agent_name: str, details: str, execution_id: Optional[str] = None):
        log = AuditLog(
            execution_id=execution_id,
            event_type=event_type,
            agent_name=agent_name,
            details=details
        )
        self.db.add(log)
        self.db.commit()

    def log_failure(self, failure_data: Dict[str, Any]) -> FailureRecord:
        record = FailureRecord(**failure_data)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_failures(self, execution_id: Optional[str] = None) -> List[FailureRecord]:
        q = self.db.query(FailureRecord)
        if execution_id:
            q = q.filter_by(execution_id=execution_id)
        return q.order_by(desc(FailureRecord.id)).all()
