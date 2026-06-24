"""Application configuration loaded from environment variables."""

from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache

# Project root is 3 levels up from this file: config.py -> app -> backend -> OPD
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Gemini Configuration
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    gemini_api_base: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    gemini_temperature: float = 0.3
    gemini_max_tokens: int = 1024

    # Database Configuration
    database_url: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/healthcare"

    # App Configuration
    backend_port: int = 8000
    frontend_port: int = 5173

    # Memory Configuration
    max_messages_before_summary: int = 20

    model_config = {"env_file": str(PROJECT_ROOT / ".env"), "extra": "ignore"}


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
