"""
Application configuration via pydantic-settings.
All settings are loaded from environment variables.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # --- Application ---
    APP_NAME: str = "AdaptiveTutor"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # --- Database ---
    DATABASE_URL: str = "sqlite+aiosqlite:///./adaptivetutor.db"

    # --- Authentication ---
    JWT_SECRET_KEY: str = "CHANGE-ME-IN-PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # --- Anthropic Claude API ---
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"

    # --- CORS ---
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache()
def get_settings() -> Settings:
    """Cache and return application settings."""
    return Settings()
