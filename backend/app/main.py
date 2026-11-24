import os
import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.connection import SessionLocal
from app.database.migrations import run_schema_migrations
from app.data.synthetic_data.generator import seed_database
from app.api.routes import (
    business, worker, approvals, executions, demo,
    auth, ai_providers, integrations, health, assistant, briefing
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Apply additive schema migrations (preserves existing data)
    run_schema_migrations()
    # Seed default synthetic multi-tenant records
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    description="Autonomous AI Growth Manager for Kirana and Small Retail Businesses",
    version="2.0.0",
    lifespan=lifespan
)

# Correlation ID and Request Timing Middleware
@app.middleware("http")
async def correlation_and_timing_middleware(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id
    start_time = time.time()

    response = await call_next(request)

    latency = round((time.time() - start_time) * 1000, 2)
    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Process-Time-Ms"] = str(latency)
    return response

# Configure CORS restricted to configured local origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Register All Subsystem Routers
app.include_router(auth.router, prefix="/api")
app.include_router(ai_providers.router, prefix="/api")
app.include_router(integrations.router, prefix="/api")
app.include_router(health.router, prefix="/api")
app.include_router(assistant.router, prefix="/api")
app.include_router(briefing.router, prefix="/api")
app.include_router(business.router)
app.include_router(worker.router)
app.include_router(approvals.router)
app.include_router(executions.router)
app.include_router(demo.router)

@app.get("/")
def root():
    return {
        "status": "ONLINE",
        "app": settings.APP_NAME,
        "tagline": settings.TAGLINE,
        "version": "2.0.0",
        "documentation": "/docs",
        "health_check": "/api/health/live"
    }

@app.get("/api/health")
def legacy_health_check():
    return {
        "status": "HEALTHY",
        "app": settings.APP_NAME,
        "tagline": settings.TAGLINE,
        "store": settings.STORE_NAME,
        "location": settings.STORE_LOCATION,
        "deterministic_mode": settings.USE_LOCAL_DETERMINISTIC_MODE
    }

@app.get("/api/report/download")
@app.get("/api/report/technical")
def download_technical_report():
    base = Path(__file__).resolve().parent.parent.parent
    pdf_path = base / "DUKAANDOST_AI_FINAL_TECHNICAL_REPORT.pdf"
    if not pdf_path.exists():
        pdf_path = base / "docs" / "DUKAANDOST_AI_FINAL_TECHNICAL_REPORT.pdf"
    return FileResponse(
        path=str(pdf_path),
        filename="DUKAANDOST_AI_FINAL_TECHNICAL_REPORT.pdf",
        media_type="application/pdf"
    )

@app.get("/api/report/final")
@app.get("/api/report/engineering")
def download_final_report():
    base = Path(__file__).resolve().parent.parent.parent
    pdf_path = base / "DUKAANDOST_AI_COMPLETE_ENGINEERING_REPORT.pdf"
    if not pdf_path.exists():
        pdf_path = base / "docs" / "DUKAANDOST_AI_COMPLETE_ENGINEERING_REPORT.pdf"
    return FileResponse(
        path=str(pdf_path),
        filename="DUKAANDOST_AI_FINAL_REPORT.pdf",
        media_type="application/pdf"
    )

@app.get("/api/report/diagram")
def get_architecture_diagram():
    base = Path(__file__).resolve().parent.parent.parent
    img_path = base / "architecture" / "dukaandost_system_architecture.png"
    return FileResponse(
        path=str(img_path),
        filename="dukaandost_system_architecture.png",
        media_type="image/png"
    )
