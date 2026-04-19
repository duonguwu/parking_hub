# -*- coding: utf-8 -*-
"""
WashMind — Application Settings (pydantic-settings, load from .env)

Usage:
    from app.core.config import settings
    print(settings.MONGO_URI)
"""
import os
import secrets
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────────────
    APP_NAME: str = "WashMind"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # ── MongoDB ──────────────────────────────────────────────────
    MONGO_URI: str = "mongodb://admin:admin123@localhost:27017/washmind?authSource=admin"
    MONGO_DB: str = "washmind"

    # ── Authentication (JWT) ─────────────────────────────────────
    JWT_SECRET_KEY: str = secrets.token_hex(32)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Super Admin (seeded on startup) ──────────────────────────
    SUPER_ADMIN_USERNAME: str = "superadmin"
    SUPER_ADMIN_PASSWORD: str = ""

    # ── CORS ─────────────────────────────────────────────────────
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # ── Redis (Phase 2: locks, caching) ──────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL_SECONDS: int = 3600          # 1h default
    REDIS_LOCK_TIMEOUT_SECONDS: int = 10

    # ── OSM Routing (Phase 2) ────────────────────────────────────
    # Public demo OSRM — rate-limited, use self-hosted for prod.
    OSRM_BASE_URL: str = "https://router.project-osrm.org"
    OSM_ROUTE_CACHE_TTL_SECONDS: int = 3600
    OSM_HTTP_TIMEOUT_SECONDS: float = 5.0

    # ── Weather (Phase 2) ────────────────────────────────────────
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1/forecast"
    WEATHER_CACHE_TTL_SECONDS: int = 900          # 15 min
    WEATHER_HTTP_TIMEOUT_SECONDS: float = 5.0

    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            ".env",
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
