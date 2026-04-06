"""
Application configuration via pydantic-settings.

All settings are loaded from environment variables (or .env file).
Access settings anywhere via: `from backend.config import get_settings`
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.

    Values are loaded in this priority order:
    1. Environment variables (highest priority)
    2. .env file
    3. Default values defined here (lowest priority)
    """

    # --- Application ---
    APP_NAME: str = "AdaptiveTutor"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # --- Database ---
    # SQLite (dev): sqlite+aiosqlite:///./adaptivetutor.db
    # PostgreSQL (prod): postgresql+asyncpg://user:pass@host:5432/dbname
    DATABASE_URL: str = "sqlite+aiosqlite:///./adaptivetutor.db"

    # --- Authentication (JWT) ---
    JWT_SECRET_KEY: str = "CHANGE-ME-IN-PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # --- Anthropic Claude API ---
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"

    # --- CORS ---
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- Computed Properties ---

    @property
    def is_sqlite(self) -> bool:
        """Check if we're using SQLite (local dev)."""
        return self.DATABASE_URL.startswith("sqlite")

    @property
    def is_production(self) -> bool:
        """Check if we're in production mode."""
        return not self.DEBUG and self.JWT_SECRET_KEY != "CHANGE-ME-IN-PRODUCTION"


@lru_cache()
def get_settings() -> Settings:
    """
    Cache and return application settings.
    Uses lru_cache so .env is only read once.
    """
    return Settings()
