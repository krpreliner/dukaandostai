from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.database.connection import get_db
from app.database.repository import BusinessRepository
from app.ai.provider_manager import ProviderManager
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/ai", tags=["AI Providers & Usage Management"])

class TestConnectionRequest(BaseModel):
    provider_name: str
    api_key: Optional[str] = None
    model: Optional[str] = None

class ProviderSettingUpdateRequest(BaseModel):
    provider_name: str
    model_name: str
    is_enabled: bool = True
    is_primary: bool = False
    is_fallback: bool = False
    api_key: Optional[str] = None

@router.get("/providers")
async def get_providers(
    store_id: str = "STORE_001",
    db: Session = Depends(get_db)
):
    repo = BusinessRepository(db)
    db_settings = {s.provider_name: s for s in repo.get_ai_provider_settings(store_id=store_id)}
    manager = ProviderManager.get_instance()

    provider_list = []
    for name, provider in manager.providers.items():
        db_s = db_settings.get(name)
        is_enabled = db_s.is_enabled if db_s else (name == "deterministic")
        is_primary = db_s.is_primary if db_s else (name == "deterministic")
        is_fallback = db_s.is_fallback if db_s else False
        model = db_s.model_name if db_s else provider.get_supported_models()[0]

        # Test live status
        test_res = await provider.test_connection(model=model)

        provider_list.append({
            "provider_name": name,
            "supported_models": provider.get_supported_models(),
            "selected_model": model,
            "is_enabled": is_enabled,
            "is_primary": is_primary,
            "is_fallback": is_fallback,
            "status": test_res.get("status", "NOT CONFIGURED"),
            "latency_ms": test_res.get("latency_ms", 0.0),
            "message": test_res.get("message", "")
        })

    return provider_list

@router.post("/test-connection")
async def test_provider_connection(req: TestConnectionRequest):
    manager = ProviderManager.get_instance()
    provider = manager.get_provider(req.provider_name)
    result = await provider.test_connection(api_key=req.api_key, model=req.model)
    return result

@router.post("/settings")
def update_provider_settings(
    req: ProviderSettingUpdateRequest,
    store_id: str = "STORE_001",
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    repo = BusinessRepository(db)

    # If this provider is marked as primary, unmark other providers
    if req.is_primary:
        all_s = repo.get_ai_provider_settings(store_id=store_id)
        for s in all_s:
            if s.provider_name != req.provider_name and s.is_primary:
                s.is_primary = False
        db.commit()

    masked_key = (req.api_key[:4] + "..." + req.api_key[-4:]) if req.api_key and len(req.api_key) > 8 else None

    setting_dict = {
        "store_id": store_id,
        "provider_name": req.provider_name,
        "model_name": req.model_name,
        "is_enabled": req.is_enabled,
        "is_primary": req.is_primary,
        "is_fallback": req.is_fallback,
    }
    if req.api_key and req.api_key.strip():
        setting_dict["api_key"] = req.api_key.strip()
        setting_dict["api_key_masked"] = masked_key

    setting = repo.save_ai_provider_setting(setting_dict)

    return {
        "status": "SUCCESS",
        "message": f"Updated settings for AI provider '{req.provider_name}'",
        "provider": {
            "provider_name": setting.provider_name,
            "model_name": setting.model_name,
            "is_enabled": setting.is_enabled,
            "is_primary": setting.is_primary,
            "is_fallback": setting.is_fallback
        }
    }

@router.get("/usage")
def get_ai_usage(
    store_id: str = "STORE_001",
    db: Session = Depends(get_db)
):
    repo = BusinessRepository(db)
    stats = repo.get_ai_usage_stats(store_id=store_id)
    return stats
