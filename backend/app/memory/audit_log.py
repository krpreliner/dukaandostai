from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.database.models import AuditLog

class AuditLogger:
    @staticmethod
    def log(
        db: Session,
        event_type: str,
        agent_name: str,
        details: str,
        execution_id: Optional[str] = None
    ) -> AuditLog:
        record = AuditLog(
            execution_id=execution_id,
            event_type=event_type,
            agent_name=agent_name,
            details=details,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(record)
        db.commit()
        return record
