"""Configuration and environment settings."""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings."""
    
    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///./cost_leak_killer.db"
    )
    
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    
    # ML Configuration
    ISOLATION_FOREST_CONTAMINATION = float(os.getenv("ISOLATION_FOREST_CONTAMINATION", 0.1))
    MIN_SAMPLES_FOR_ML = int(os.getenv("MIN_SAMPLES_FOR_ML", 10))
    
    # File Upload
    MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 10 * 1024 * 1024))  # 10MB
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
    
    # Financial Defaults
    DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY", "USD")
    SAVINGS_MULTIPLIER = float(os.getenv("SAVINGS_MULTIPLIER", 0.3))  # 30% default
    
    # LLM Configuration (future integration)
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    
    # Frontend Configuration
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8501")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Email Configuration (for action execution)
    SMTP_SERVER = os.getenv("SMTP_SERVER", "localhost")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM = os.getenv("SMTP_FROM", "alerts@costleakkiller.local")


settings = Settings()
