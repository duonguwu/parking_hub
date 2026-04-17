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

    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            ".env",
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
