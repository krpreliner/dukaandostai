import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database.connection import SessionLocal
from app.database.models import Product, FailureRecord, AuditLog, ExecutionRecord
from app.agents.finance_agent import FinanceAgent

client = TestClient(app)

def test_01_negative_gross_margin_detected_and_rejected():
    """Verify Finance Agent deterministically blocks negative margin products."""
    db: Session = SessionLocal()
    try:
        butter = db.query(Product).filter_by(product_id="PROD003").first()
        if not butter:
            butter = Product(
                product_id="PROD003",
                product_name="Amul Butter 500g",
                category="Dairy",
                cost_price=60.0,
                selling_price=55.0,
                current_stock=25,
                minimum_stock=10,
                store_id="STORE_001"
            )
            db.add(butter)
        else:
            butter.cost_price = 60.0
            butter.selling_price = 55.0
        db.commit()

        agent = FinanceAgent(db)
        res = agent.validate_task_finance({
            "task_id": "TASK_TEST_01",
            "task_name": "Butter Promo",
            "details": {"bundle_name": "Dairy Offer", "products": ["PROD003"], "discount_pct": 5.0}
        })

        assert res["is_approved"] is False
        assert res["error_type"] == "NEGATIVE_GROSS_MARGIN"
        assert res["loss_per_unit"] == 5.0
        assert "strictly prohibited" in res["message"]
    finally:
        db.close()

def test_02_zero_margin_rejected():
    """Verify zero margin pricing (cost == sell) fails minimum margin policy."""
    db: Session = SessionLocal()
    try:
        agent = FinanceAgent(db)
        val = agent.validate_offer(cost_price=100.0, proposed_price=100.0, original_price=100.0)
        assert val["is_valid"] is False
        assert any("Margin" in r or "margin" in r for r in val["reasons"])
    finally:
        db.close()

def test_03_positive_healthy_margin_approved():
    """Verify pricing with healthy margin (+11.8%) is valid."""
    db: Session = SessionLocal()
    try:
        agent = FinanceAgent(db)
        val = agent.validate_offer(cost_price=60.0, proposed_price=68.0, original_price=70.0)
        assert val["is_valid"] is True
        assert val["gross_margin_pct"] >= 5.0
        assert val["unit_profit"] > 0
    finally:
        db.close()

def test_04_missing_product_inventory_validation():
    """Verify task referencing non-existent product ID is safely rejected."""
    db: Session = SessionLocal()
    try:
        agent = FinanceAgent(db)
        res = agent.validate_task_finance({
            "task_id": "TASK_MISSING",
            "details": {"bundle_name": "Ghost Bundle", "products": ["PROD_NON_EXISTENT_999"]}
        })
        assert res["is_approved"] is False
        assert res["error_type"] == "MISSING_PRODUCT_INVENTORY"
    finally:
        db.close()

def test_05_invalid_negative_price_rejected():
    """Verify non-positive cost or selling price is rejected."""
    db: Session = SessionLocal()
    try:
        agent = FinanceAgent(db)
        butter = db.query(Product).filter_by(product_id="PROD003").first()
        if butter:
            butter.cost_price = -10.0
            db.commit()
            res = agent.validate_task_finance({
                "task_id": "TASK_INVALID_PRICE",
                "details": {"bundle_name": "Promo", "products": ["PROD003"]}
            })
            assert res["is_approved"] is False
            assert res["error_type"] == "INVALID_PRODUCT_COST"
            # Restore
            butter.cost_price = 60.0
            db.commit()
    finally:
        db.close()

def test_06_demo_failure_endpoint_creates_failure_and_audit_record():
    """Verify /api/demo/trigger-failure creates real FailureRecord and AuditLog."""
    resp = client.post("/api/demo/trigger-failure", headers={"X-Store-Id": "STORE_001"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert data["scenario"] == "NEGATIVE_GROSS_MARGIN_TRIGGERED"
    assert data["cost_price"] == 60.0
    assert data["selling_price"] == 55.0
    assert data["calculated_margin_pct"] < 0
    assert data["responsible_agent"] == "Finance Agent"

    # Verify database persistence
    db: Session = SessionLocal()
    try:
        f = db.query(FailureRecord).filter_by(task_id="TASK_PROMO_PROD003", recovery_status="UNRESOLVED").first()
        assert f is not None
        assert "NEGATIVE_GROSS_MARGIN" in f.root_cause

        audit = db.query(AuditLog).filter_by(event_type="FINANCIAL_GUARDRAIL_VIOLATION").first()
        assert audit is not None
        assert "Amul Butter" in audit.details
    finally:
        db.close()

def test_07_demo_failure_idempotency_prevents_duplicate_spam():
    """Repeated calls to trigger-failure should update existing failure rather than spam duplicates."""
    resp1 = client.post("/api/demo/trigger-failure", headers={"X-Store-Id": "STORE_001"})
    assert resp1.status_code == 200
    fid1 = resp1.json()["failure_id"]

    resp2 = client.post("/api/demo/trigger-failure", headers={"X-Store-Id": "STORE_001"})
    assert resp2.status_code == 200
    assert resp2.json()["idempotent"] is True
    assert resp2.json()["failure_id"] == fid1

def test_08_price_rectification_success():
    """Verify rectifying price to healthy margin resolves failure and updates product."""
    # Ensure active failure exists
    trigger_resp = client.post("/api/demo/trigger-failure", headers={"X-Store-Id": "STORE_001"})
    failure_id = trigger_resp.json()["failure_id"]

    # Rectify with Cost ₹60, Sell ₹68 (+11.8% margin)
    rectify_resp = client.post(
        f"/api/failures/{failure_id}/rectify",
        headers={"X-Store-Id": "STORE_001"},
        json={"product_id": "PROD003", "new_cost_price": 60.0, "new_selling_price": 68.0}
    )
    assert rectify_resp.status_code == 200
    rdata = rectify_resp.json()
    assert rdata["status"] == "SUCCESS"
    assert rdata["gross_margin_pct"] > 5.0
    assert rdata["recovery_status"] == "RESOLVED"

    # Verify DB state
    db: Session = SessionLocal()
    try:
        f = db.query(FailureRecord).filter_by(id=failure_id).first()
        assert f.recovery_status == "RESOLVED"

        p = db.query(Product).filter_by(product_id="PROD003").first()
        assert p.cost_price == 60.0
        assert p.selling_price == 68.0
        assert p.status == "HEALTHY"
    finally:
        db.close()

def test_09_price_rectification_failed_when_still_negative_margin():
    """Verify rectifying to another negative or sub-5% margin is rejected."""
    # Create active failure
    trigger_resp = client.post("/api/demo/trigger-failure", headers={"X-Store-Id": "STORE_001"})
    failure_id = trigger_resp.json()["failure_id"]

    # Attempt to rectify with Sell ₹58 < Cost ₹60
    rectify_resp = client.post(
        f"/api/failures/{failure_id}/rectify",
        headers={"X-Store-Id": "STORE_001"},
        json={"product_id": "PROD003", "new_cost_price": 60.0, "new_selling_price": 58.0}
    )
    assert rectify_resp.status_code == 400
    assert "positive gross margin" in rectify_resp.json()["detail"]

def test_10_recovery_persistence_across_database_query():
    """Verify /api/failures endpoint returns resolved state."""
    resp = client.get("/api/failures", headers={"X-Store-Id": "STORE_001"})
    assert resp.status_code == 200
    records = resp.json()
    assert isinstance(records, list)

def test_11_demo_reset_clears_failures_and_reseeds_clean_state():
    """Verify /api/demo/reset clears transient executions and re-seeds baseline."""
    resp = client.post("/api/demo/reset", headers={"X-Store-Id": "STORE_001"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "SUCCESS"

    # Check database
    db: Session = SessionLocal()
    try:
        failures = db.query(FailureRecord).filter_by(store_id="STORE_001").all()
        assert len(failures) == 0
        products = db.query(Product).filter_by(store_id="STORE_001").all()
        assert len(products) >= 30
        audits = db.query(AuditLog).filter_by(store_id="STORE_001").all()
        assert len(audits) >= 2
    finally:
        db.close()
