"""Application configuration.

All settings are read from environment variables (optionally from a .env file).
Secrets are never logged: warnings mention *that* a development default is in
use, never its value.
"""

from __future__ import annotations

import logging
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# --- Development-only fallbacks -------------------------------------------------
# These defaults exist so `uvicorn backend.main:app` works out of the box for
# local development. They are NOT suitable for production.
_DEV_DATABASE_URL = "sqlite:///./familyshield_dev.db"  # clearly labelled fallback
_DEV_SECRET_KEY = "familyshield-insecure-development-secret-change-me"
_DEV_FRONTEND_BASE_URL = "http://localhost:3000"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ---------------------------------------------------------------- database
    DATABASE_URL: str = _DEV_DATABASE_URL

    # ------------------------------------------------------------------ security
    SECRET_KEY: str = _DEV_SECRET_KEY
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    # ------------------------------------------------------------ external APIs
    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GOOGLE_SAFE_BROWSING_API_KEY: str | None = None

    # Network probes are opt-in and disabled by default. When enabled, only a
    # TLS handshake is attempted; page contents are NEVER fetched or executed.
    SAFE_URL_PROBE: bool = False
    TLS_PROBE_TIMEOUT_SECONDS: float = 1.5

    # ------------------------------------------------------------------- server
    CORS_ORIGINS: str = (
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:5173,http://127.0.0.1:5173"
    )
    RATE_LIMIT_PER_MINUTE: int = 20
    FRONTEND_BASE_URL: str = _DEV_FRONTEND_BASE_URL

    # Creates tables on startup for local SQLite development. Set to false in
    # production and use `alembic upgrade head` instead.
    DEV_AUTO_CREATE_TABLES: bool = True

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def using_dev_database(self) -> bool:
        return self.DATABASE_URL == _DEV_DATABASE_URL

    @property
    def using_dev_secret(self) -> bool:
        return self.SECRET_KEY == _DEV_SECRET_KEY

    def log_safety_warnings(self) -> None:
        """Log configuration warnings without ever printing a secret value."""
        if self.using_dev_secret:
            logger.warning(
                "SECURITY: SECRET_KEY is the development default. Set a strong "
                "SECRET_KEY environment variable before deploying."
            )
        if self.using_dev_database:
            logger.warning(
                "CONFIG: DATABASE_URL is the local SQLite development fallback "
                "(%s). Set DATABASE_URL for a real deployment.",
                _DEV_DATABASE_URL,
            )
        if not self.GROQ_API_KEY:
            logger.info("CONFIG: GROQ_API_KEY not set; deterministic explanation engine will be used.")
        if not self.GOOGLE_SAFE_BROWSING_API_KEY:
            logger.info("CONFIG: Google Safe Browsing check disabled (no API key).")
        if not self.SAFE_URL_PROBE:
            logger.info("CONFIG: Active URL probes disabled (SAFE_URL_PROBE=false).")


@lru_cache
def get_settings() -> Settings:
    # Environment variables (or a .env file) override every default above.
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
