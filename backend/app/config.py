import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "DukaanDost AI"
    TAGLINE: str = "Your AI Business Partner That Doesn't Just Advise. It Takes Action."
    STORE_NAME: str = "Sharma General Store"
    STORE_LOCATION: str = "Ranchi, Jharkhand, India"
    STORE_OWNER: str = "Sharma Ji"
    
    # Financial Goals
    INITIAL_NET_INCOME: float = 8000.0
    TARGET_NET_INCOME: float = 10000.0
    REQUIRED_GROWTH: float = 2000.0
    MAX_PROMOTIONAL_DISCOUNT_PCT: float = 15.0 # Max 15% discount permitted
    
    # Database and Checkpointing
    DATABASE_URL: str = "sqlite:///./dukaandost.db"
    CHECKPOINT_DB_PATH: str = "./checkpoints.db"
    
    # Optional LLM
    OPENAI_API_KEY: str = ""
    USE_LOCAL_DETERMINISTIC_MODE: bool = True
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
