# -*- coding: utf-8 -*-
"""
Application Settings — pydantic-settings load from .env

Usage:
    from app.core.config import settings
    print(settings.MONGO_URI)
"""
import os
import secrets
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── MongoDB ──────────────────────────────────────────────────
    MONGO_URI: str = "mongodb://admin:admin123@localhost:27017/your_db?authSource=admin"
    MONGO_DB: str = "your_db"

    # ── Redis ────────────────────────────────────────────────────
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""

    # ── Authentication (JWT) ─────────────────────────────────────
    JWT_SECRET_KEY: str = secrets.token_hex(32)  # Override in .env!
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Super Admin (seeded on startup) ──────────────────────────
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
