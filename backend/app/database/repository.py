from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional, Dict, Any
from app.database.models import (
    User, Store, StoreMember,
    Customer, Product, Transaction, Expense,
    ExecutionRecord, TaskRecord, ApprovalRecord, AuditLog, FailureRecord,
    AIProviderSetting, AIUsageLog, IntegrationSetting
)

class BusinessRepository:
    def __init__(self, db: Session):
        self.db = db

    # ----------------------------------------------------
    # Multi-tenant & User Management
    # ----------------------------------------------------
    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email.lower().strip()).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, email: str, password_hash: str, full_name: str) -> User:
        user = User(
            email=email.lower().strip(),
            password_hash=password_hash,
            full_name=full_name.strip()
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_stores(self, user_id: int) -> List[Dict[str, Any]]:
        memberships = self.db.query(StoreMember).filter_by(user_id=user_id).all()
        result = []
        for m in memberships:
            store = self.db.query(Store).filter_by(store_id=m.store_id).first()
            if store:
                result.append({
                    "store_id": store.store_id,
                    "name": store.name,
                    "location": store.location,
                    "owner_name": store.owner_name,
                    "role": m.role,
                    "initial_net_income": store.initial_net_income,
                    "target_net_income": store.target_net_income,
                    "current_net_income": store.current_net_income,
                    "simulated_net_income": store.simulated_net_income
                })
        return result

    def get_store_by_id(self, store_id: str) -> Optional[Store]:
        return self.db.query(Store).filter_by(store_id=store_id).first()

    def create_store(self, store_id: str, name: str, location: str, owner_name: str) -> Store:
        store = Store(
            store_id=store_id,
            name=name,
            location=location,
            owner_name=owner_name
        )
        self.db.add(store)
        self.db.commit()
        self.db.refresh(store)
        return store

    def add_store_member(self, user_id: int, store_id: str, role: str = "OWNER") -> StoreMember:
        member = self.db.query(StoreMember).filter_by(user_id=user_id, store_id=store_id).first()
        if not member:
            member = StoreMember(user_id=user_id, store_id=store_id, role=role)
            self.db.add(member)
        else:
            member.role = role
        self.db.commit()
        self.db.refresh(member)
        return member

    def get_store_members(self, store_id: str) -> List[Dict[str, Any]]:
        members = self.db.query(StoreMember).filter_by(store_id=store_id).all()
        result = []
        for m in members:
            u = self.db.query(User).filter_by(id=m.user_id).first()
            if u:
                result.append({
                    "user_id": u.id,
                    "email": u.email,
                    "full_name": u.full_name,
                    "role": m.role,
                    "created_at": m.created_at.isoformat() if m.created_at else None
                })
        return result

    # ----------------------------------------------------
    # Financial Analytics (Tenant-Scoped)
    # ----------------------------------------------------
    def get_financial_summary(self, store_id: str = "STORE_001") -> Dict[str, float]:
        total_rev = self.db.query(func.sum(Transaction.total_amount)).filter(Transaction.store_id == store_id).scalar() or 0.0
        total_cogs = self.db.query(func.sum(Transaction.cost_amount)).filter(Transaction.store_id == store_id).scalar() or 0.0
        total_exp = self.db.query(func.sum(Expense.amount)).filter(Expense.store_id == store_id).scalar() or 0.0
        gross_profit = total_rev - total_cogs
        net_income = gross_profit - total_exp
        return {
            "revenue": round(total_rev, 2),
            "cogs": round(total_cogs, 2),
            "gross_profit": round(gross_profit, 2),
            "operating_expenses": round(total_exp, 2),
            "net_income": round(net_income, 2)
        }

    def get_expenses_breakdown(self, store_id: str = "STORE_001") -> List[Dict[str, Any]]:
        expenses = self.db.query(Expense).filter(Expense.store_id == store_id).all()
        return [{"category": e.category, "amount": e.amount, "notes": e.notes} for e in expenses]

    # ----------------------------------------------------
    # Customers & Products (Tenant-Scoped)
    # ----------------------------------------------------
    def get_customers(self, segment: Optional[str] = None, store_id: str = "STORE_001") -> List[Customer]:
        q = self.db.query(Customer).filter(Customer.store_id == store_id)
        if segment:
            q = q.filter(Customer.segment == segment)
        return q.all()

    def get_customer_by_id(self, customer_id: str, store_id: str = "STORE_001") -> Optional[Customer]:
        return self.db.query(Customer).filter(Customer.customer_id == customer_id, Customer.store_id == store_id).first()

    def get_products(self, category: Optional[str] = None, status: Optional[str] = None, store_id: str = "STORE_001") -> List[Product]:
        q = self.db.query(Product).filter(Product.store_id == store_id)
        if category:
            q = q.filter(Product.category == category)
        if status:
            q = q.filter(Product.status == status)
        return q.all()

    def get_product_by_id(self, product_id: str, store_id: str = "STORE_001") -> Optional[Product]:
        return self.db.query(Product).filter(Product.product_id == product_id, Product.store_id == store_id).first()

    def update_product_price(self, product_id: str, new_cost: Optional[float] = None, new_sell: Optional[float] = None, store_id: str = "STORE_001") -> Optional[Product]:
        prod = self.get_product_by_id(product_id, store_id=store_id)
        if prod:
            if new_cost is not None:
                prod.cost_price = new_cost
            if new_sell is not None:
                prod.selling_price = new_sell
            if prod.selling_price >= prod.cost_price and prod.status == "NEGATIVE MARGIN":
                prod.status = "HEALTHY"
            self.db.commit()
            self.db.refresh(prod)
        return prod

    def get_transactions(self, limit: int = 100, store_id: str = "STORE_001") -> List[Transaction]:
        return self.db.query(Transaction).filter(Transaction.store_id == store_id).order_by(desc(Transaction.id)).limit(limit).all()

    # ----------------------------------------------------
    # Executions & Tasks
    # ----------------------------------------------------
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

    def get_latest_execution(self, store_id: str = "STORE_001") -> Optional[ExecutionRecord]:
        return self.db.query(ExecutionRecord).filter_by(store_id=store_id).order_by(desc(ExecutionRecord.id)).first()

    def get_all_executions(self, store_id: str = "STORE_001") -> List[ExecutionRecord]:
        return self.db.query(ExecutionRecord).filter_by(store_id=store_id).order_by(desc(ExecutionRecord.id)).all()

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

    # ----------------------------------------------------
    # Approvals
    # ----------------------------------------------------
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

    def get_approval(self, execution_id: str, task_id: str) -> Optional[ApprovalRecord]:
        return self.db.query(ApprovalRecord).filter_by(execution_id=execution_id, task_id=task_id).first()

    def get_pending_approvals(self, execution_id: Optional[str] = None, store_id: str = "STORE_001") -> List[ApprovalRecord]:
        q = self.db.query(ApprovalRecord).filter_by(status="PENDING", store_id=store_id)
        if execution_id:
            q = q.filter_by(execution_id=execution_id)
        return q.all()

    def get_all_approvals(self, execution_id: Optional[str] = None, store_id: str = "STORE_001") -> List[ApprovalRecord]:
        q = self.db.query(ApprovalRecord).filter_by(store_id=store_id)
        if execution_id:
            q = q.filter_by(execution_id=execution_id)
        return q.order_by(desc(ApprovalRecord.id)).all()

    # ----------------------------------------------------
    # Audit Logs & Failure Monitoring
    # ----------------------------------------------------
    def log_audit(self, event_type: str, agent_name: str, details: str, execution_id: Optional[str] = None, store_id: str = "STORE_001"):
        log = AuditLog(
            store_id=store_id,
            execution_id=execution_id,
            event_type=event_type,
            agent_name=agent_name,
            details=details
        )
        self.db.add(log)
        self.db.commit()

    def get_audit_logs(self, execution_id: Optional[str] = None, store_id: str = "STORE_001", limit: int = 50) -> List[AuditLog]:
        q = self.db.query(AuditLog).filter_by(store_id=store_id)
        if execution_id:
            q = q.filter_by(execution_id=execution_id)
        return q.order_by(desc(AuditLog.id)).limit(limit).all()

    def log_failure(self, failure_data: Dict[str, Any]) -> FailureRecord:
        record = FailureRecord(**failure_data)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_failures(self, execution_id: Optional[str] = None, store_id: str = "STORE_001") -> List[FailureRecord]:
        q = self.db.query(FailureRecord).filter_by(store_id=store_id)
        if execution_id:
            q = q.filter_by(execution_id=execution_id)
        return q.order_by(desc(FailureRecord.id)).all()

    def resolve_failure(self, failure_id: int) -> Optional[FailureRecord]:
        record = self.db.query(FailureRecord).filter_by(id=failure_id).first()
        if record:
            record.recovery_status = "RESOLVED"
            self.db.commit()
            self.db.refresh(record)
        return record

    def resolve_failures_for_task(self, task_id: str) -> int:
        records = self.db.query(FailureRecord).filter_by(task_id=task_id, recovery_status="UNRESOLVED").all()
        for r in records:
            r.recovery_status = "RESOLVED"
        self.db.commit()
        return len(records)

    def resolve_all_failures(self, store_id: str = "STORE_001") -> int:
        records = self.db.query(FailureRecord).filter_by(store_id=store_id, recovery_status="UNRESOLVED").all()
        for r in records:
            r.recovery_status = "RESOLVED"
        self.db.commit()
        return len(records)

    # ----------------------------------------------------
    # AI Provider Settings & Usage Tracking
    # ----------------------------------------------------
    def get_ai_provider_settings(self, store_id: str = "STORE_001") -> List[AIProviderSetting]:
        return self.db.query(AIProviderSetting).filter_by(store_id=store_id).all()

    def get_ai_provider_setting(self, provider_name: str, store_id: str = "STORE_001") -> Optional[AIProviderSetting]:
        return self.db.query(AIProviderSetting).filter_by(store_id=store_id, provider_name=provider_name).first()

    def save_ai_provider_setting(self, setting_data: Dict[str, Any]) -> AIProviderSetting:
        store_id = setting_data.get("store_id", "STORE_001")
        provider_name = setting_data["provider_name"]
        setting = self.get_ai_provider_setting(provider_name, store_id=store_id)
        if not setting:
            setting = AIProviderSetting(**setting_data)
            self.db.add(setting)
        else:
            for k, v in setting_data.items():
                setattr(setting, k, v)
        self.db.commit()
        self.db.refresh(setting)
        return setting

    def log_ai_usage(self, usage_data: Dict[str, Any]) -> AIUsageLog:
        log = AIUsageLog(**usage_data)
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_ai_usage_stats(self, store_id: str = "STORE_001") -> Dict[str, Any]:
        logs = self.db.query(AIUsageLog).filter_by(store_id=store_id).all()
        total_requests = len(logs)
        total_prompt_tokens = sum(l.prompt_tokens for l in logs)
        total_completion_tokens = sum(l.completion_tokens for l in logs)
        total_tokens = sum(l.total_tokens for l in logs)
        total_cost_usd = round(sum(l.estimated_cost_usd for l in logs), 4)
        avg_latency_ms = round(sum(l.latency_ms for l in logs) / total_requests, 1) if total_requests > 0 else 0.0

        return {
            "total_requests": total_requests,
            "total_prompt_tokens": total_prompt_tokens,
            "total_completion_tokens": total_completion_tokens,
            "total_tokens": total_tokens,
            "total_cost_usd": total_cost_usd,
            "avg_latency_ms": avg_latency_ms
        }

    # ----------------------------------------------------
    # Integration Settings
    # ----------------------------------------------------
    def get_integration_settings(self, store_id: str = "STORE_001") -> List[IntegrationSetting]:
        return self.db.query(IntegrationSetting).filter_by(store_id=store_id).all()

    def get_integration_setting(self, integration_type: str, store_id: str = "STORE_001") -> Optional[IntegrationSetting]:
        return self.db.query(IntegrationSetting).filter_by(store_id=store_id, integration_type=integration_type).first()

    def save_integration_setting(self, integration_type: str, is_enabled: bool, status: str, config_json: str, store_id: str = "STORE_001") -> IntegrationSetting:
        setting = self.get_integration_setting(integration_type, store_id=store_id)
        if not setting:
            setting = IntegrationSetting(
                store_id=store_id,
                integration_type=integration_type,
                is_enabled=is_enabled,
                status=status,
                config_json=config_json
            )
            self.db.add(setting)
        else:
            setting.is_enabled = is_enabled
            setting.status = status
            setting.config_json = config_json
        self.db.commit()
        self.db.refresh(setting)
        return setting
