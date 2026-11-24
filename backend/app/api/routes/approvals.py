from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database.connection import get_db
from app.services.approval_service import ApprovalService
from app.api.schemas.api_models import ApprovalActionRequest

router = APIRouter(prefix="/api/approvals", tags=["Approvals"])

@router.get("/pending")
def get_pending_approvals(execution_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    svc = ApprovalService(db)
    return svc.get_pending_approvals(execution_id=execution_id)

@router.post("/{task_id}/approve")
def approve_task(task_id: str, req: ApprovalActionRequest = None, db: Session = Depends(get_db)):
    svc = ApprovalService(db)
    exec_id = req.execution_id if req else None
    res = svc.handle_decision(task_id=task_id, action="APPROVE", execution_id=exec_id)
    if not res.get("success", False):
        raise HTTPException(status_code=400, detail=res.get("error", "Failed to approve task"))
    return res

@router.post("/{task_id}/reject")
def reject_task(task_id: str, req: ApprovalActionRequest = None, db: Session = Depends(get_db)):
    svc = ApprovalService(db)
    exec_id = req.execution_id if req else None
    res = svc.handle_decision(task_id=task_id, action="REJECT", execution_id=exec_id)
    if not res.get("success", False):
        raise HTTPException(status_code=400, detail=res.get("error", "Failed to reject task"))
    return res
