from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def get_utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)
    
    memberships = relationship("StoreMember", back_populates="user", cascade="all, delete-orphan")


class Store(Base):
    __tablename__ = "stores"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    location = Column(String(100), default="Ranchi, Jharkhand")
    owner_name = Column(String(100), default="Sharma Ji")
    currency = Column(String(10), default="INR")
    initial_net_income = Column(Float, default=8000.0)
    target_net_income = Column(Float, default=10000.0)
    current_net_income = Column(Float, default=8000.0)
    simulated_net_income = Column(Float, default=8000.0)
    created_at = Column(DateTime, default=get_utc_now)
    
    members = relationship("StoreMember", back_populates="store", cascade="all, delete-orphan")


class StoreMember(Base):
    __tablename__ = "store_members"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    store_id = Column(String(50), ForeignKey("stores.store_id"), index=True, nullable=False)
    role = Column(String(20), default="OWNER")  # OWNER, MANAGER, STAFF, VIEWER
    created_at = Column(DateTime, default=get_utc_now)
    
    user = relationship("User", back_populates="memberships")
    store = relationship("Store", back_populates="members")


class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String(50), index=True, default="STORE_001", nullable=False)
    customer_id = Column(String(50), unique=True, index=True, nullable=False)
    customer_name = Column(String(100), nullable=False)
    area = Column(String(100), nullable=False)
    age_group = Column(String(20), nullable=False)
    total_orders = Column(Integer, default=0)
    total_spending = Column(Float, default=0.0)
    last_purchase_date = Column(String(20), nullable=False)
    preferred_category = Column(String(100), nullable=False)
    average_order_value = Column(Float, default=0.0)
    segment = Column(String(50), default="Active")  # Active, Inactive, Frequent, High Value, At Risk
    
    transactions = relationship("Transaction", back_populates="customer")


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String(50), index=True, default="STORE_001", nullable=False)
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
    status = Column(String(50), default="HEALTHY")
    
    transactions = relationship("Transaction", back_populates="product")


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String(50), index=True, default="STORE_001", nullable=False)
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
    store_id = Column(String(50), index=True, default="STORE_001", nullable=False)
    category = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    month = Column(String(20), default="Current Month")
    notes = Column(String(255), default="")


class ExecutionRecord(Base):
    __tablename__ = "execution_records"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String(50), index=True, default="STORE_001", nullable=False)
    execution_id = Column(String(100), unique=True, index=True, nullable=False)
    thread_id = Column(String(100), index=True, nullable=False)
    status = Column(String(50), default="IDLE")
    initial_income = Column(Float, default=8000.0)
    target_income = Column(Float, default=10000.0)
    current_income = Column(Float, default=8000.0)
    simulated_income = Column(Float, default=8000.0)
    variance = Column(Float, default=0.0)
    current_agent = Column(String(100), default="Supervisor")
    current_task = Column(String(255), default="")
    created_at = Column(DateTime, default=get_utc_now)
    completed_at = Column(DateTime, nullable=True)


class TaskRecord(Base):
    __tablename__ = "task_records"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String(50), index=True, default="STORE_001", nullable=False)
    execution_id = Column(String(100), index=True, nullable=False)
    task_id = Column(String(50), index=True, nullable=False)
    task_name = Column(String(200), nullable=False)
    assigned_agent = Column(String(100), nullable=False)
    priority = Column(String(20), default="MEDIUM")
    expected_impact = Column(Float, default=0.0)
    simulated_impact = Column(Float, default=0.0)
    risk_level = Column(String(20), default="LOW")
    approval_required = Column(Boolean, default=False)
    status = Column(String(50), default="PENDING")
    execution_result = Column(Text, default="")
    failure_reason = Column(Text, default="")
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)


class ApprovalRecord(Base):
    __tablename__ = "approval_records"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String(50), index=True, default="STORE_001", nullable=False)
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
    status = Column(String(50), default="PENDING")
    decided_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String(50), index=True, default="STORE_001", nullable=False)
    execution_id = Column(String(100), index=True, nullable=True)
    event_type = Column(String(100), nullable=False)
    agent_name = Column(String(100), nullable=False)
    details = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=get_utc_now)


class FailureRecord(Base):
    __tablename__ = "failure_records"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String(50), index=True, default="STORE_001", nullable=False)
    execution_id = Column(String(100), index=True, nullable=False)
    task_id = Column(String(50), index=True, nullable=False)
    agent_name = Column(String(100), nullable=False)
    error_description = Column(Text, nullable=False)
    root_cause = Column(Text, nullable=False)
    recovery_status = Column(String(50), default="UNRESOLVED")
    retry_count = Column(Integer, default=0)
    timestamp = Column(DateTime, default=get_utc_now)


class AIProviderSetting(Base):
    __tablename__ = "ai_provider_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String(50), index=True, default="STORE_001", nullable=False)
    provider_name = Column(String(50), nullable=False)  # openai, gemini, groq, ollama, deterministic
    model_name = Column(String(100), nullable=False)
    is_enabled = Column(Boolean, default=True)
    is_primary = Column(Boolean, default=False)
    is_fallback = Column(Boolean, default=False)
    api_key = Column(Text, nullable=True)
    api_key_masked = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=get_utc_now)


class AIUsageLog(Base):
    __tablename__ = "ai_usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String(50), index=True, default="STORE_001", nullable=False)
    execution_id = Column(String(100), index=True, nullable=True)
    agent_name = Column(String(100), nullable=False)
    provider_name = Column(String(50), nullable=False)
    model_name = Column(String(100), nullable=False)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    estimated_cost_usd = Column(Float, default=0.0)
    latency_ms = Column(Float, default=0.0)
    status = Column(String(20), default="SUCCESS")
    error_message = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=get_utc_now)


class IntegrationSetting(Base):
    __tablename__ = "integration_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String(50), index=True, default="STORE_001", nullable=False)
    integration_type = Column(String(50), nullable=False)  # google_sheets, weather, email, whatsapp
    is_enabled = Column(Boolean, default=False)
    status = Column(String(50), default="NOT CONFIGURED")  # NOT CONFIGURED, CONNECTED AND VERIFIED, CONNECTION FAILED
    config_json = Column(Text, default="{}")
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)


class DailyBriefing(Base):
    __tablename__ = "daily_briefings"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String(50), index=True, default="STORE_001", nullable=False)
    briefing_date = Column(String(20), index=True, nullable=False)
    greeting = Column(String(100), default="Namaste Sharma Ji!")
    summary_text = Column(Text, nullable=False)
    audio_script = Column(Text, nullable=False)
    today_sales = Column(Float, default=0.0)
    yesterday_sales = Column(Float, default=0.0)
    sales_growth_pct = Column(Float, default=0.0)
    low_stock_count = Column(Integer, default=0)
    inactive_customer_count = Column(Integer, default=0)
    growth_opportunities_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=get_utc_now)


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String(50), index=True, default="STORE_001", nullable=False)
    session_id = Column(String(100), index=True, default="SESSION_DEFAULT", nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    language = Column(String(20), default="hinglish")
    tools_used = Column(Text, default="[]")
    evidence_json = Column(Text, default="{}")
    suggested_actions = Column(Text, default="[]")
    timestamp = Column(DateTime, default=get_utc_now)
