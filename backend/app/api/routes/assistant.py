from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.database.connection import get_db
from app.services.assistant_service import AssistantService

router = APIRouter(prefix="/assistant", tags=["Conversational AI Business Assistant"])

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "SESSION_DEFAULT"
    language: Optional[str] = "hi"

@router.post("/chat")
def chat_with_assistant(
    req: ChatRequest,
    x_store_id: str = Header("STORE_001", alias="X-Store-Id"),
    db: Session = Depends(get_db)
):
    svc = AssistantService(db, store_id=x_store_id)
    return svc.process_chat_message(user_text=req.message, session_id=req.session_id, language=req.language)

@router.get("/history")
def get_chat_history(
    session_id: str = "SESSION_DEFAULT",
    limit: int = 30,
    x_store_id: str = Header("STORE_001", alias="X-Store-Id"),
    db: Session = Depends(get_db)
):
    svc = AssistantService(db, store_id=x_store_id)
    return svc.get_chat_history(session_id=session_id, limit=limit)

@router.delete("/history")
def clear_chat_history(
    session_id: str = "SESSION_DEFAULT",
    x_store_id: str = Header("STORE_001", alias="X-Store-Id"),
    db: Session = Depends(get_db)
):
    svc = AssistantService(db, store_id=x_store_id)
    deleted = svc.clear_chat_history(session_id=session_id)
    return {"status": "SUCCESS", "deleted_messages_count": deleted}
