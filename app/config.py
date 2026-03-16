from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Supabase
    supabase_url: str
    supabase_key: str
    supabase_storage_url: Optional[str] = None

    # Application
    environment: str = "development"
    max_image_size_mb: int = 5
    low_stock_threshold_default: int = 5
    allowed_origins: str = "*"  # Comma-separated list or "*"

    # Vercel (optional for local dev)
    vercel_url: Optional[str] = "http://localhost:8000"

    # Alexa (optional, Phase 4)
    alexa_skill_id: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
