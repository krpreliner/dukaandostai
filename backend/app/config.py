import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

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
    
    # Real AI Providers (OpenAI, Gemini, Groq, Anthropic, Ollama)
    AI_MODE: str = "deterministic"
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    USE_LOCAL_DETERMINISTIC_MODE: bool = False

    # Real External Integrations (Weather, Twilio Messaging, Google Sheets)
    OPENWEATHER_API_KEY: str = ""
    WEATHERAPI_KEY: str = ""
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    TWILIO_WHATSAPP_NUMBER: str = ""
    GOOGLE_SHEETS_API_KEY: str = ""
    
    # Security & Tokens
    JWT_SECRET_KEY: str = "dukaandost_kirana_super_secret_jwt_key_2026"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

settings = Settings()
