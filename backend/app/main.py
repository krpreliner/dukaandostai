import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.connection import init_db, SessionLocal
from app.data.synthetic_data.generator import seed_database
from app.api.routes import business, worker, approvals, executions, demo

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables
    init_db()
    # Seed synthetic business data if not already present
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    description="Autonomous AI Growth Manager for Kirana and Small Retail Businesses",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow dev origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(business.router)
app.include_router(worker.router)
app.include_router(approvals.router)
app.include_router(executions.router)
app.include_router(demo.router)

@app.get("/api/health")
def health_check():
    return {
        "status": "HEALTHY",
        "app": settings.APP_NAME,
        "tagline": settings.TAGLINE,
        "store": settings.STORE_NAME,
        "location": settings.STORE_LOCATION,
        "deterministic_mode": settings.USE_LOCAL_DETERMINISTIC_MODE
    }
