from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from app.database.connection import get_db
from app.services.briefing_service import BriefingService

router = APIRouter(prefix="/briefing", tags=["AI Daily Business Briefing"])

@router.get("/latest")
def get_latest_briefing(
    x_store_id: str = Header("STORE_001", alias="X-Store-Id"),
    db: Session = Depends(get_db)
):
    svc = BriefingService(db, store_id=x_store_id)
    return svc.get_latest_briefing()

@router.post("/generate")
def generate_fresh_briefing(
    x_store_id: str = Header("STORE_001", alias="X-Store-Id"),
    db: Session = Depends(get_db)
):
    svc = BriefingService(db, store_id=x_store_id)
    return svc.generate_daily_briefing()

@router.get("/history")
def get_briefing_history(
    limit: int = 10,
    x_store_id: str = Header("STORE_001", alias="X-Store-Id"),
    db: Session = Depends(get_db)
):
    svc = BriefingService(db, store_id=x_store_id)
    return svc.get_briefing_history(limit=limit)
