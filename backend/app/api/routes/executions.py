from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel
from app.database.connection import get_db
from app.database.models import ExecutionRecord, TaskRecord, FailureRecord, AuditLog, Product
from app.services.execution_service import ExecutionService
from app.database.repository import BusinessRepository

router = APIRouter(prefix="/api", tags=["Executions"])

@router.get("/executions")
def list_executions(
    x_store_id: str = Header("STORE_001", alias="X-Store-Id"),
    db: Session = Depends(get_db)
):
    records = db.query(ExecutionRecord).filter_by(store_id=x_store_id).order_by(desc(ExecutionRecord.id)).all()
    return [
        {
            "execution_id": r.execution_id,
            "thread_id": r.thread_id,
            "status": r.status,
            "initial_income": r.initial_income,
            "target_income": r.target_income,
            "current_income": r.current_income,
            "simulated_income": r.simulated_income,
            "variance": r.variance,
            "current_agent": r.current_agent,
            "current_task": r.current_task,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "completed_at": r.completed_at.isoformat() if r.completed_at else None
        }
        for r in records
    ]

@router.get("/executions/{execution_id}")
def get_execution_detail(execution_id: str, db: Session = Depends(get_db)):
    svc = ExecutionService(db)
    res = svc.get_execution_status(execution_id)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res

@router.get("/failures")
def list_failures(
    execution_id: Optional[str] = Query(None),
    x_store_id: str = Header("STORE_001", alias="X-Store-Id"),
    db: Session = Depends(get_db)
):
    q = db.query(FailureRecord).filter_by(store_id=x_store_id)
    if execution_id:
        q = q.filter_by(execution_id=execution_id)
    records = q.order_by(desc(FailureRecord.id)).all()
    return [
        {
            "id": r.id,
            "execution_id": r.execution_id,
            "task_id": r.task_id,
            "agent_name": r.agent_name,
            "error_description": r.error_description,
            "root_cause": r.root_cause,
            "recovery_status": r.recovery_status,
            "retry_count": r.retry_count,
            "timestamp": r.timestamp.isoformat() if r.timestamp else None
        }
        for r in records
    ]

class RectifyFailurePriceRequest(BaseModel):
    product_id: Optional[str] = "PROD003"
    new_cost_price: float = 60.0
    new_selling_price: float = 68.0

@router.post("/failures/{failure_id}/rectify")
def rectify_failure_price(
    failure_id: int,
    req: RectifyFailurePriceRequest,
    x_store_id: str = Header("STORE_001", alias="X-Store-Id"),
    db: Session = Depends(get_db)
):
    """
    Section 3-C: Genuine price correction and deterministic revalidation.
    1. Retrieves target product.
    2. Validates positive pricing and positive gross margin.
    3. Calculates deterministic gross margin.
    4. Applies financial guardrails.
    5. Updates product price and marks status HEALTHY.
    6. Updates failure record to RESOLVED.
    7. Emits immutable AuditLog event.
    """
    store_id = x_store_id
    prod_id = req.product_id or "PROD003"
    prod = db.query(Product).filter_by(product_id=prod_id, store_id=store_id).first()
    if not prod:
        prod = db.query(Product).filter_by(product_id=prod_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail=f"Product '{prod_id}' not found in catalog.")

    if req.new_cost_price <= 0 or req.new_selling_price <= 0:
        raise HTTPException(status_code=400, detail="Cost price and selling price must be strictly positive (> ₹0.00).")

    if req.new_selling_price <= req.new_cost_price:
        loss = round(req.new_cost_price - req.new_selling_price, 2)
        raise HTTPException(
            status_code=400,
            detail=f"Price rectification rejected: Proposed selling price ₹{req.new_selling_price:.2f} does not yield a positive gross margin over cost price ₹{req.new_cost_price:.2f} (Loss: -₹{loss:.2f}/unit)."
        )

    # Deterministic gross margin calculation
    unit_profit = round(req.new_selling_price - req.new_cost_price, 2)
    margin_pct = round((unit_profit / req.new_selling_price) * 100, 2)

    # Minimum margin policy check (minimum 5%)
    if margin_pct < 5.0:
        raise HTTPException(
            status_code=400,
            detail=f"Financial policy violation: Gross margin +{margin_pct:.2f}% is below the mandatory 5.0% minimum threshold."
        )

    rec = db.query(FailureRecord).filter_by(id=failure_id, store_id=store_id).first()
    if not rec:
        rec = db.query(FailureRecord).filter_by(id=failure_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail=f"Failure record #{failure_id} not found.")

    old_cost = prod.cost_price
    old_sell = prod.selling_price
    prod.cost_price = req.new_cost_price
    prod.selling_price = req.new_selling_price
    prod.status = "HEALTHY"

    rec.recovery_status = "RESOLVED"
    rec.retry_count += 1
    rec.error_description = (
        f"{rec.error_description} [RECTIFIED: Cost ₹{req.new_cost_price:.2f}, Sell ₹{req.new_selling_price:.2f}, Margin +{margin_pct:.1f}%]"
    )

    audit = AuditLog(
        store_id=store_id,
        execution_id=rec.execution_id,
        event_type="PRICE_RECTIFICATION_VALIDATED",
        agent_name="Finance Agent",
        details=(
            f"Product '{prod.product_name}' price rectified: Old Cost ₹{old_cost:.2f} / Sell ₹{old_sell:.2f} -> "
            f"New Cost ₹{req.new_cost_price:.2f} / Sell ₹{req.new_selling_price:.2f}. "
            f"Deterministic Gross Margin: +{margin_pct:.2f}% (Unit profit: ₹{unit_profit:.2f}). "
            f"Financial Guardrail verified. Failure #{failure_id} resolved."
        ),
        timestamp=datetime.now(timezone.utc)
    )
    db.add(audit)
    db.commit()
    db.refresh(prod)
    db.refresh(rec)

    return {
        "status": "SUCCESS",
        "message": f"Product '{prod.product_name}' rectified and revalidated with positive gross margin +{margin_pct:.2f}%.",
        "failure_id": failure_id,
        "product_id": prod.product_id,
        "product_name": prod.product_name,
        "old_cost_price": old_cost,
        "old_selling_price": old_sell,
        "new_cost_price": req.new_cost_price,
        "new_selling_price": req.new_selling_price,
        "unit_profit": unit_profit,
        "gross_margin_pct": margin_pct,
        "recovery_status": rec.recovery_status
    }

@router.post("/failures/{failure_id}/resolve")
def resolve_single_failure(failure_id: int, db: Session = Depends(get_db)):
    repo = BusinessRepository(db)
    rec = repo.resolve_failure(failure_id)
    if not rec:
        raise HTTPException(status_code=404, detail=f"Failure record #{failure_id} not found")
    return {
        "status": "SUCCESS",
        "message": f"Failure #{failure_id} resolved.",
        "failure_id": failure_id,
        "recovery_status": rec.recovery_status
    }

@router.post("/failures/resolve-all")
def resolve_all_active_failures(
    x_store_id: str = Header("STORE_001", alias="X-Store-Id"),
    db: Session = Depends(get_db)
):
    repo = BusinessRepository(db)
    count = repo.resolve_all_failures(store_id=x_store_id)
    return {
        "status": "SUCCESS",
        "message": f"Resolved {count} failure records.",
        "resolved_count": count
    }

@router.get("/audit-logs")
def list_audit_logs(
    execution_id: Optional[str] = Query(None),
    limit: int = 50,
    x_store_id: str = Header("STORE_001", alias="X-Store-Id"),
    db: Session = Depends(get_db)
):
    q = db.query(AuditLog).filter_by(store_id=x_store_id)
    if execution_id:
        q = q.filter_by(execution_id=execution_id)
    logs = q.order_by(desc(AuditLog.id)).limit(limit).all()
    return [
        {
            "id": l.id,
            "execution_id": l.execution_id,
            "event_type": l.event_type,
            "agent_name": l.agent_name,
            "details": l.details,
            "timestamp": l.timestamp.isoformat() if l.timestamp else None
        }
        for l in logs
    ]
