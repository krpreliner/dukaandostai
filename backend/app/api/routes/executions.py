from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from app.database.connection import get_db
from app.database.models import ExecutionRecord, TaskRecord, FailureRecord, AuditLog
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
