from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Product, ExecutionRecord, TaskRecord, ApprovalRecord, FailureRecord, AuditLog
from app.services.business_service import BusinessService

router = APIRouter(prefix="/api/demo", tags=["Demo Controls"])

@router.post("/trigger-failure")
def trigger_failure(db: Session = Depends(get_db)):
    """
    Sets up the mandatory reproducible failure scenario (Section 9):
    Product: Butter.
    Cost Price: ₹60.
    Selling Price: ₹55.
    Marketing Agent proposes discount -> Finance detects negative gross margin -> Promotion blocked!
    """
    # Find Butter
    butter = db.query(Product).filter_by(product_id="PROD003").first()
    if butter:
        butter.cost_price = 60.0
        butter.selling_price = 55.0
        butter.status = "NEGATIVE MARGIN"
        db.commit()

    return {
        "status": "SUCCESS",
        "scenario": "NEGATIVE_GROSS_MARGIN_TRIGGERED",
        "product": "Butter (PROD003)",
        "cost_price": 60.0,
        "selling_price": 55.0,
        "expected_result": "Finance Agent will detect negative gross margin (-₹5.00/unit) and reject any promotion proposal, causing Supervisor to log failure."
    }

@router.post("/reset")
def reset_demo(db: Session = Depends(get_db)):
    """
    Resets all demo synthetic data, database records, and executions to clean baseline.
    """
    # Clear logs and executions
    db.query(FailureRecord).delete()
    db.query(ApprovalRecord).delete()
    db.query(TaskRecord).delete()
    db.query(AuditLog).delete()
    db.query(ExecutionRecord).delete()
    db.commit()

    # Re-seed database
    svc = BusinessService(db)
    svc.reset_synthetic_data()

    return {
        "status": "SUCCESS",
        "message": "Demo data successfully reset to baseline: Net Income ₹8,000.0, 120 customers, 32 products, clean workflow state."
    }
