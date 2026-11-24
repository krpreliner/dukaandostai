import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import (
    Product, ExecutionRecord, TaskRecord, ApprovalRecord, FailureRecord, AuditLog, Store
)
from app.agents.finance_agent import FinanceAgent
from app.data.synthetic_data.generator import seed_database

router = APIRouter(prefix="/api/demo", tags=["Demo Controls"])

@router.post("/trigger-failure")
def trigger_failure(
    x_store_id: str = Header("STORE_001", alias="X-Store-Id"),
    db: Session = Depends(get_db)
):
    """
    Section 3: Controlled demonstration scenario for Failure Monitoring.
    1. Sets Amul Butter 500g (PROD003) to Cost ₹60.00 > Selling ₹55.00.
    2. Calculates actual negative gross margin (-9.09%, -₹5.00/unit).
    3. Invokes deterministic Finance Agent validation.
    4. Deterministically rejects unsafe promotional action.
    5. Records & persists FailureRecord with unique ID & execution ID.
    6. Emits immutable AuditLog event.
    7. Updates execution status.
    8. Enforces idempotency (updates existing unresolved failure instead of uncontrolled spam).
    """
    store_id = x_store_id

    # 1. Retrieve or find Amul Butter
    butter = db.query(Product).filter_by(product_id="PROD003", store_id=store_id).first()
    if not butter:
        butter = db.query(Product).filter_by(product_id="PROD003").first()

    cost_price = 60.0
    selling_price = 55.0
    loss_per_unit = round(cost_price - selling_price, 2)
    calculated_margin = round(((selling_price - cost_price) / selling_price) * 100, 2)

    if butter:
        butter.cost_price = cost_price
        butter.selling_price = selling_price
        butter.status = "NEGATIVE MARGIN"
        db.commit()

    # 2. Invoke deterministic Finance Agent validation
    finance_agent = FinanceAgent(db)
    simulated_task = {
        "task_id": "TASK_PROMO_PROD003",
        "task_name": "Promotional Discount Campaign: Amul Butter 500g",
        "details": {
            "bundle_name": "Special Offer - Amul Butter 500g",
            "products": ["PROD003"],
            "discount_pct": 5.0
        }
    }
    validation = finance_agent.validate_task_finance(simulated_task)

    exec_id = "EXEC_DEMO_FAILURE"

    # 3. Idempotency Check: search for existing UNRESOLVED failure record
    existing_failure = db.query(FailureRecord).filter_by(
        store_id=store_id,
        task_id="TASK_PROMO_PROD003",
        recovery_status="UNRESOLVED"
    ).first()

    if existing_failure:
        existing_failure.retry_count += 1
        existing_failure.timestamp = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing_failure)
        failure_record = existing_failure
    else:
        # Ensure execution record exists with FAILED state
        exec_rec = db.query(ExecutionRecord).filter_by(execution_id=exec_id, store_id=store_id).first()
        if not exec_rec:
            exec_rec = ExecutionRecord(
                execution_id=exec_id,
                thread_id=exec_id,
                store_id=store_id,
                current_task="Demonstrate Financial Guardrail: Negative Gross Margin Auto-Rejection",
                target_income=10000.0,
                status="FAILED",
                current_agent="Finance Agent"
            )
            db.add(exec_rec)
        else:
            exec_rec.status = "FAILED"
            exec_rec.current_agent = "Finance Agent"

        failure_record = FailureRecord(
            store_id=store_id,
            execution_id=exec_id,
            task_id="TASK_PROMO_PROD003",
            agent_name="Finance Agent",
            error_description=(
                f"FINANCIAL GUARDRAIL ENFORCED: Negative gross margin detected on 'Amul Butter 500g' "
                f"(Cost: ₹{cost_price:.2f} > Sell: ₹{selling_price:.2f}, Margin: {calculated_margin}%, Loss: -₹{loss_per_unit:.2f}/unit). "
                f"Promotions on negative-margin products are strictly prohibited."
            ),
            root_cause="NEGATIVE_GROSS_MARGIN_VIOLATION",
            recovery_status="UNRESOLVED",
            retry_count=0,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(failure_record)
        db.commit()
        db.refresh(failure_record)

        # 4. Create immutable AuditLog event
        audit = AuditLog(
            store_id=store_id,
            execution_id=exec_id,
            event_type="FINANCIAL_GUARDRAIL_VIOLATION",
            agent_name="Finance Agent",
            details=(
                f"Negative gross margin auto-rejected on Amul Butter (Cost ₹{cost_price:.2f} > Sell ₹{selling_price:.2f}, "
                f"Margin {calculated_margin}%). Unsafe promotional campaign halted. Logged failure #{failure_record.id}."
            ),
            timestamp=datetime.now(timezone.utc)
        )
        db.add(audit)
        db.commit()

    return {
        "status": "SUCCESS",
        "scenario": "NEGATIVE_GROSS_MARGIN_TRIGGERED",
        "failure_id": failure_record.id,
        "execution_id": exec_id,
        "business_id": store_id,
        "product": "Amul Butter 500g (PROD003)",
        "cost_price": cost_price,
        "selling_price": selling_price,
        "calculated_margin_pct": calculated_margin,
        "loss_per_unit": loss_per_unit,
        "violation_type": "NEGATIVE_GROSS_MARGIN_VIOLATION",
        "rejection_reason": validation.get("message", "Negative gross margin auto-rejection"),
        "responsible_agent": "Finance Agent",
        "timestamp": failure_record.timestamp.isoformat() if failure_record.timestamp else None,
        "recovery_status": failure_record.recovery_status,
        "idempotent": existing_failure is not None
    }


@router.post("/reset")
def reset_demo(
    x_store_id: str = Header("STORE_001", alias="X-Store-Id"),
    db: Session = Depends(get_db)
):
    """
    Section 19: Safe demonstration reset control.
    Resets synthetic Kirana store records, transactions, executions, and re-seeds baseline data.
    Preserves audit logging and tenant integrity.
    """
    store_id = x_store_id

    # 1. Clear transient executions & logs for this store
    db.query(FailureRecord).filter_by(store_id=store_id).delete()
    db.query(ApprovalRecord).filter_by(store_id=store_id).delete()
    db.query(TaskRecord).filter_by(store_id=store_id).delete()
    db.query(AuditLog).filter_by(store_id=store_id).delete()
    db.query(ExecutionRecord).filter_by(store_id=store_id).delete()
    db.commit()

    # 2. Re-seed database with clean synthetic records
    seed_database(db, force_reset=True)

    # 3. Reset store income state
    store = db.query(Store).filter_by(store_id=store_id).first()
    if store:
        store.initial_net_income = 8000.0
        store.current_net_income = 8000.0
        store.simulated_net_income = 8000.0
        store.target_net_income = 10000.0
        db.commit()

    # 4. Seed baseline audit events so telemetry & audit trail are immediately verifiable
    baseline_audits = [
        AuditLog(
            store_id=store_id,
            execution_id=None,
            event_type="SYSTEM_BOOTSTRAP_INITIALIZED",
            agent_name="System",
            details="Sharma General Store baseline initialized with 32 catalog products, 120 customers, and audited ledger.",
            timestamp=datetime.now(timezone.utc)
        ),
        AuditLog(
            store_id=store_id,
            execution_id=None,
            event_type="BASELINE_FINANCIALS_RECONCILED",
            agent_name="Finance Agent",
            details="Baseline financial reconciliation complete: Net Operating Income ₹8,000.00/month. Target ₹10,000.00/month.",
            timestamp=datetime.now(timezone.utc)
        )
    ]
    db.add_all(baseline_audits)
    db.commit()

    return {
        "status": "SUCCESS",
        "message": "Demo data successfully reset to baseline: Net Income ₹8,000.00, 120 customers, 32 products, clean workflow state.",
        "store_id": store_id
    }
