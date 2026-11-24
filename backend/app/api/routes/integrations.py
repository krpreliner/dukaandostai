from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from pydantic import BaseModel
from app.database.connection import get_db
from app.database.repository import BusinessRepository
from app.integrations.sheets import SheetsIntegration
from app.integrations.weather import WeatherIntegration
from app.integrations.messaging import MessagingIntegration

router = APIRouter(prefix="/integrations", tags=["External Integrations"])

class SheetsPreviewRequest(BaseModel):
    csv_content: str

class SheetsConfirmRequest(BaseModel):
    items: List[Dict[str, Any]]

class ToggleIntegrationRequest(BaseModel):
    is_enabled: bool

class SendLiveMessageRequest(BaseModel):
    recipient_phone: str
    message_body: str
    channel: str = "sms"

@router.get("")
def list_integrations(
    store_id: str = "STORE_001",
    db: Session = Depends(get_db)
):
    repo = BusinessRepository(db)
    settings = repo.get_integration_settings(store_id=store_id)
    return [
        {
            "id": s.id,
            "integration_type": s.integration_type,
            "is_enabled": s.is_enabled,
            "status": s.status,
            "config": s.config_json,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None
        }
        for s in settings
    ]

@router.post("/{integration_type}/toggle")
def toggle_integration(
    integration_type: str,
    req: ToggleIntegrationRequest,
    store_id: str = "STORE_001",
    db: Session = Depends(get_db)
):
    repo = BusinessRepository(db)
    status_str = "CONNECTED AND VERIFIED" if req.is_enabled else "NOT CONFIGURED"
    setting = repo.save_integration_setting(
        integration_type=integration_type,
        is_enabled=req.is_enabled,
        status=status_str,
        config_json="{}",
        store_id=store_id
    )
    return {
        "status": "SUCCESS",
        "integration_type": integration_type,
        "is_enabled": setting.is_enabled,
        "integration_status": setting.status
    }

@router.post("/sheets/preview")
def preview_sheets_import(
    req: SheetsPreviewRequest,
    store_id: str = "STORE_001",
    db: Session = Depends(get_db)
):
    return SheetsIntegration.preview_csv_import(req.csv_content, db, store_id=store_id)

@router.post("/sheets/confirm")
def confirm_sheets_import(
    req: SheetsConfirmRequest,
    store_id: str = "STORE_001",
    db: Session = Depends(get_db)
):
    return SheetsIntegration.confirm_csv_import(req.items, db, store_id=store_id)

@router.get("/weather/signals")
def get_weather_signals(city: str = "Ranchi"):
    return WeatherIntegration.get_weather_signals(city=city)

@router.get("/messaging/preview")
def get_messaging_preview():
    return MessagingIntegration.generate_campaign_draft(
        campaign_name="Breakfast Combo Campaign",
        target_segment="Active Customers",
        offer_description="Bread + Butter Combo",
        discount_pct=5.2
    )

@router.post("/messaging/send-live")
def send_live_message(req: SendLiveMessageRequest):
    return MessagingIntegration.send_live_message(
        recipient_phone=req.recipient_phone,
        message_body=req.message_body,
        channel=req.channel
    )
