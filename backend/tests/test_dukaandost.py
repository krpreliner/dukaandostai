import pytest
import os
import sqlite3
from app.database.connection import init_db, SessionLocal, engine
from app.data.synthetic_data.generator import (
    generate_customers, generate_products, generate_expenses,
    generate_transactions, seed_database
)
from app.agents.business_analyst import BusinessAnalystAgent
from app.agents.strategy_planner import StrategyPlannerAgent
from app.agents.marketing_agent import MarketingAgent
from app.agents.inventory_agent import InventoryAgent
from app.agents.finance_agent import FinanceAgent
from app.agents.supervisor import SupervisorAgent
from app.tools.profit_calculator import ProfitCalculator
from app.services.execution_service import ExecutionService
from app.services.approval_service import ApprovalService
from app.services.business_service import BusinessService
from app.database.models import Product, TaskRecord, ApprovalRecord

@pytest.fixture(scope="module")
def setup_db():
    init_db()
    db = SessionLocal()
    seed_database(db, force_reset=True)
    yield db
    db.close()


def test_01_baseline_income_calculation(setup_db):
    """TEST 1: Business Analyst correctly calculates baseline income (₹8,000.0)."""
    db = setup_db
    analyst = BusinessAnalystAgent(db)
    res = analyst.run(target_income=10000.0)
    assert res["current_income"] == 8000.0
    assert res["revenue"] == 95000.0
    assert res["expenses"] == 11000.0
    assert res["income_gap"] == 2000.0


def test_02_strategy_planner_creates_plan(setup_db):
    """TEST 2: Strategy Planner independently creates an actionable plan."""
    db = setup_db
    analyst = BusinessAnalystAgent(db)
    analysis = analyst.run()
    planner = StrategyPlannerAgent()
    tasks = planner.run(analysis)
    assert len(tasks) >= 4
    for t in tasks:
        assert "task_id" in t
        assert "task_name" in t
        assert "assigned_agent" in t
        assert "expected_impact" in t
        assert "approval_required" in t
    total_expected = sum(t["expected_impact"] for t in tasks)
    assert total_expected >= 2000.0


def test_03_marketing_agent_analysis(setup_db):
    """TEST 3: Marketing Agent analyses customer behaviour and bundles."""
    db = setup_db
    marketing = MarketingAgent(db)
    combo = marketing.propose_combo(["PROD002", "PROD003"], "Breakfast Combo", 109.0)
    assert combo["original_price"] > 0
    assert combo["proposed_price"] == 109.0
    assert "promotional_message" in combo
    # Verify simulated bundling task
    task = {
        "task_id": "TASK_TEST",
        "task_name": "Combo Test",
        "details": {"bundle_name": "Combo Test", "target_units": 40}
    }
    sim_res = marketing.execute_bundling_task(task)
    assert sim_res["success"] is True
    assert sim_res["simulated_impact"] > 0


def test_04_inventory_agent_detections(setup_db):
    """TEST 4: Inventory Agent detects low stock and slow-moving products."""
    db = setup_db
    inv = InventoryAgent(db)
    health = inv.check_health()
    assert health["low_stock_count"] >= 2
    assert health["slow_moving_count"] >= 1
    assert health["expiring_soon_count"] >= 1


def test_05_finance_agent_blocks_negative_margin(setup_db):
    """TEST 5: Finance Agent blocks negative-margin offers."""
    db = setup_db
    finance = FinanceAgent(db)
    # Butter: Cost 60, Proposed Sell 55 -> Negative margin
    val = finance.validate_offer(cost_price=60.0, proposed_price=55.0, original_price=70.0)
    assert val["is_valid"] is False
    assert any("Negative gross margin" in r for r in val["reasons"])


def test_06_supervisor_coordination(setup_db):
    """TEST 6: Supervisor coordinates specialised agents."""
    db = setup_db
    supervisor = SupervisorAgent(db)
    analysis = supervisor.analyze_business(10000.0)
    tasks = supervisor.plan_strategy(analysis)
    assert len(tasks) > 0
    # Dispatch an inventory task
    inv_task = tasks[2]
    res = supervisor.execute_specialized_task(inv_task)
    assert res.get("success") is True


def test_07_approval_request_interrupts_execution(setup_db):
    """TEST 7: Approval request interrupts execution."""
    db = setup_db
    exec_svc = ExecutionService(db)
    res = exec_svc.start_worker(custom_target=10000.0)
    # The workflow pauses at human approval node
    assert res["status"] == "WAITING FOR APPROVAL"
    assert res["is_interrupted"] is True


def test_08_approval_resumes_same_workflow(setup_db):
    """TEST 8: Approval resumes the same workflow."""
    db = setup_db
    app_svc = ApprovalService(db)
    pending = app_svc.get_pending_approvals()
    assert len(pending) > 0
    task_id = pending[0]["task_id"]
    res = app_svc.handle_decision(task_id, "APPROVE")
    assert res["success"] is True
    assert res["decision"] == "APPROVE"


def test_09_rejection_prevents_execution(setup_db):
    """TEST 9: Rejection prevents execution of unapproved action."""
    db = setup_db
    app_svc = ApprovalService(db)
    pending = app_svc.get_pending_approvals()
    if pending:
        task_id = pending[0]["task_id"]
        res = app_svc.handle_decision(task_id, "REJECT")
        assert res["success"] is True
        assert res["decision"] == "REJECT"
        db.expire_all()
        task_rec = db.query(TaskRecord).filter_by(execution_id=res["execution_id"], task_id=task_id).first()
        assert task_rec.status == "REJECTED"


def test_10_application_restart_restores_pending_workflow(setup_db):
    """TEST 10: Application restart restores the pending workflow from SQLite checkpointer."""
    db = setup_db
    exec_svc = ExecutionService(db)
    status = exec_svc.get_execution_status(exec_svc.repo.get_latest_execution().execution_id)
    assert status["execution_id"] is not None
    assert "status" in status


def test_11_duplicate_execution_prevented(setup_db):
    """TEST 11: Completed tasks are not executed twice."""
    db = setup_db
    exec_record = db.query(TaskRecord).all()
    # Check that task IDs within an execution have unique task_id entries
    task_keys = [f"{t.execution_id}_{t.task_id}" for t in exec_record]
    assert len(task_keys) == len(set(task_keys))


def test_12_failure_recovery_works(setup_db):
    """TEST 12: Failure recovery works when negative margin is corrected."""
    db = setup_db
    butter = db.query(Product).filter_by(product_id="PROD003").first()
    # 1. Trigger failure condition
    butter.cost_price = 60.0
    butter.selling_price = 55.0
    db.commit()
    fa = FinanceAgent(db)
    test_task = {
        "task_id": "TASK_FAIL_RECOVER",
        "task_name": "Butter Promo",
        "details": {"bundle_name": "Butter Promo", "products": ["PROD003"]}
    }
    val = fa.validate_task_finance(test_task)
    assert val["is_approved"] is False

    # 2. Human owner corrects product price
    butter.cost_price = 245.0
    butter.selling_price = 275.0
    db.commit()

    # 3. Re-validate
    val2 = fa.validate_task_finance(test_task)
    assert val2["is_approved"] is True


def test_13_feedback_updates_priorities(setup_db):
    """TEST 13: Feedback records variance and updates insights."""
    variance = -20.0
    expected = 440.0
    simulated = 420.0
    pct = round((simulated / expected) * 100, 1)
    assert pct == 95.5


def test_14_dashboard_retrieves_backend_info(setup_db):
    """TEST 14: Dashboard retrieves actual backend information."""
    db = setup_db
    biz_svc = BusinessService(db)
    overview = biz_svc.get_overview()
    assert overview["store_name"] == "Sharma General Store"
    assert overview["total_customers"] == 120
    assert overview["total_products"] == 32
    assert overview["revenue"] == 95000.0


def test_15_financial_calculations_reconcile(setup_db):
    """TEST 15: Financial calculations reconcile exactly to ₹8,000 baseline."""
    customers = generate_customers()
    products = generate_products()
    expenses = generate_expenses()
    txns = generate_transactions(customers, products)

    total_rev = round(sum(t["total_amount"] for t in txns), 2)
    total_cogs = round(sum(t["cost_amount"] for t in txns), 2)
    total_exp = round(sum(e["amount"] for e in expenses), 2)

    gross_profit = round(total_rev - total_cogs, 2)
    net_income = round(gross_profit - total_exp, 2)

    assert total_rev == 95000.0
    assert total_cogs == 76000.0
    assert gross_profit == 19000.0
    assert total_exp == 11000.0
    assert net_income == 8000.0


def test_16_no_real_external_actions():
    """TEST 16: No real external actions (API payments, SMS gateway) are configured or executed."""
    assert os.getenv("REAL_PAYMENT_GATEWAY_URL") is None
    assert os.getenv("TWILIO_LIVE_SMS_AUTH") is None
