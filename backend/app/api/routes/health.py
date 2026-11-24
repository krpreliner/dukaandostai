import time
import os
import psutil
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.connection import get_db
from app.config import settings

router = APIRouter(prefix="/health", tags=["Observability & Health Checks"])
START_TIME = time.time()

@router.get("/live")
def liveness_probe():
    """Kubernetes / Docker liveness probe: returns 200 if process is running."""
    return {
        "status": "ALIVE",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/ready")
def readiness_probe(db: Session = Depends(get_db)):
    """Kubernetes / Docker readiness probe: verifies database connection."""
    try:
        start = time.time()
        db.execute(text("SELECT 1"))
        db_latency = round((time.time() - start) * 1000, 2)
        return {
            "status": "READY",
            "database": "CONNECTED",
            "db_latency_ms": db_latency,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "status": "UNHEALTHY",
            "database": f"DISCONNECTED: {str(e)}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/system")
def system_health(db: Session = Depends(get_db)):
    """Detailed system diagnostic metrics for dashboard health display."""
    # DB ping
    db_ok = True
    db_latency = 0.0
    try:
        t0 = time.time()
        db.execute(text("SELECT 1"))
        db_latency = round((time.time() - t0) * 1000, 2)
    except Exception:
        db_ok = False

    uptime_seconds = int(time.time() - START_TIME)
    
    # Process memory
    try:
        proc = psutil.Process(os.getpid())
        mem_mb = round(proc.memory_info().rss / (1024 * 1024), 2)
        cpu_pct = proc.cpu_percent(interval=0.1)
    except Exception:
        mem_mb = 0.0
        cpu_pct = 0.0

    return {
        "status": "HEALTHY" if db_ok else "DEGRADED",
        "app_env": getattr(settings, "APP_ENV", "development"),
        "uptime_seconds": uptime_seconds,
        "database_connected": db_ok,
        "database_latency_ms": db_latency,
        "process_memory_mb": mem_mb,
        "process_cpu_pct": cpu_pct,
        "ai_mode": getattr(settings, "AI_MODE", "deterministic"),
        "zero_paid_cost_enforced": True,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
