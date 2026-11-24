from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(50), unique=True, index=True, nullable=False)
    customer_name = Column(String(100), nullable=False)
    area = Column(String(100), nullable=False)
    age_group = Column(String(20), nullable=False)
    total_orders = Column(Integer, default=0)
    total_spending = Column(Float, default=0.0)
    last_purchase_date = Column(String(20), nullable=False)
    preferred_category = Column(String(100), nullable=False)
    average_order_value = Column(Float, default=0.0)
    segment = Column(String(50), default="Active") # Active, Inactive, Frequent, Occasional, High Value, At Risk
    
    transactions = relationship("Transaction", back_populates="customer")


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(50), unique=True, index=True, nullable=False)
    product_name = Column(String(150), nullable=False)
    category = Column(String(100), nullable=False)
    cost_price = Column(Float, nullable=False)
    selling_price = Column(Float, nullable=False)
    current_stock = Column(Integer, default=0)
    minimum_stock = Column(Integer, default=10)
    monthly_units_sold = Column(Integer, default=0)
    expiry_date = Column(String(20), nullable=False)
    supplier_name = Column(String(150), nullable=False)
    status = Column(String(50), default="HEALTHY") # HEALTHY, LOW STOCK, SLOW MOVING, EXPIRING SOON, REORDER REQUIRED
    
    transactions = relationship("Transaction", back_populates="product")


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(50), unique=True, index=True, nullable=False)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False)
    product_id = Column(String(50), ForeignKey("products.product_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    transaction_date = Column(String(20), nullable=False)
    total_amount = Column(Float, nullable=False)
    cost_amount = Column(Float, nullable=False)
    gross_profit = Column(Float, nullable=False)
    
    customer = relationship("Customer", back_populates="transactions")
    product = relationship("Product", back_populates="transactions")


class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), nullable=False) # Rent, Electricity, Transportation, Employee, Miscellaneous
    amount = Column(Float, nullable=False)
    month = Column(String(20), default="Current Month")
    notes = Column(String(255), default="")


class ExecutionRecord(Base):
    __tablename__ = "execution_records"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String(100), unique=True, index=True, nullable=False)
    thread_id = Column(String(100), index=True, nullable=False)
    status = Column(String(50), default="IDLE") # IDLE, ANALYSING, PLANNING, EXECUTING, WAITING FOR APPROVAL, RECOVERING, COMPLETED, FAILED
    initial_income = Column(Float, default=8000.0)
    target_income = Column(Float, default=10000.0)
    current_income = Column(Float, default=8000.0)
    simulated_income = Column(Float, default=8000.0)
    variance = Column(Float, default=0.0)
    current_agent = Column(String(100), default="Supervisor")
    current_task = Column(String(255), default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class TaskRecord(Base):
    __tablename__ = "task_records"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String(100), index=True, nullable=False)
    task_id = Column(String(50), index=True, nullable=False)
    task_name = Column(String(200), nullable=False)
    assigned_agent = Column(String(100), nullable=False)
    priority = Column(String(20), default="MEDIUM") # HIGH, MEDIUM, LOW
    expected_impact = Column(Float, default=0.0)
    simulated_impact = Column(Float, default=0.0)
    risk_level = Column(String(20), default="LOW") # LOW, MEDIUM, HIGH
    approval_required = Column(Boolean, default=False)
    status = Column(String(50), default="PENDING") # PENDING, IN_PROGRESS, WAITING_APPROVAL, COMPLETED, FAILED, REJECTED
    execution_result = Column(Text, default="")
    failure_reason = Column(Text, default="")
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ApprovalRecord(Base):
    __tablename__ = "approval_records"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String(100), index=True, nullable=False)
    task_id = Column(String(50), index=True, nullable=False)
    action_description = Column(String(255), nullable=False)
    requesting_agent = Column(String(100), nullable=False)
    original_price = Column(Float, default=0.0)
    proposed_price = Column(Float, default=0.0)
    gross_margin_pct = Column(Float, default=0.0)
    expected_impact = Column(Float, default=0.0)
    justification = Column(Text, default="")
    risk_assessment = Column(Text, default="")
    status = Column(String(50), default="PENDING") # PENDING, APPROVED, REJECTED
    decided_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String(100), index=True, nullable=True)
    event_type = Column(String(100), nullable=False)
    agent_name = Column(String(100), nullable=False)
    details = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


class FailureRecord(Base):
    __tablename__ = "failure_records"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String(100), index=True, nullable=False)
    task_id = Column(String(50), index=True, nullable=False)
    agent_name = Column(String(100), nullable=False)
    error_description = Column(Text, nullable=False)
    root_cause = Column(Text, nullable=False)
    recovery_status = Column(String(50), default="UNRESOLVED") # UNRESOLVED, RESOLVED, BLOCKED
    retry_count = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)
