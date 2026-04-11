# -*- coding: utf-8 -*-
"""
FastAPI Application Entry Point

Bao gom:
    - Lifespan (startup/shutdown): init MongoDB, Redis, seed admin, start services
    - CORS middleware
    - Auth middleware (protect all endpoints, whitelist public paths)
    - Health check endpoints
    - Main router registration

Usage:
    uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""
import logging
import os

from dotenv import load_dotenv
load_dotenv()  # Load .env truoc khi import bat ky module nao

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse as StarletteJSONResponse

from app.core.logging_config import setup_logging
from app.core.config import settings
from app.api.auth.jwt_manager import decode_token
from app.api.main_router import main_router
from app.db.mongo import init_mongo, close_mongo
from app.services.shared.redis_client import redis_client

# ── Setup logging ────────────────────────────────────────────────
setup_logging(service="main", console_level=logging.INFO, file_level=logging.DEBUG)
logger = logging.getLogger(__name__)


# ── Lifespan (startup + shutdown) ────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────
    try:
        # 1. Initialize MongoDB
        init_mongo()

        # 2. Seed super admin account (skip if already exists)
        # from app.api.auth.auth_utils import seed_super_admin
        # await seed_super_admin()

        # 3. Connect Redis (neu dung)
        # await redis_client.connect()

        # 4. Start background services (neu co)
        # await some_service.start()

        logger.info("All services started successfully")

    except Exception as e:
        logger.critical(f"Startup failed: {e}", exc_info=True)
        raise

    yield  # Application running

    # ── Shutdown ─────────────────────────────────────────────────
    try:
        logger.info("Shutting down services...")

        # Stop background services
        # await some_service.stop()

        # Disconnect Redis
        # await redis_client.disconnect()

        # Close MongoDB
        close_mongo()

        logger.info("Shutdown completed successfully")
    except Exception as e:
        logger.error(f"Shutdown failed: {e}", exc_info=True)


# ── FastAPI App ──────────────────────────────────────────────────

app = FastAPI(title="YourProject", lifespan=lifespan)


# ── CORS Middleware ──────────────────────────────────────────────
# IMPORTANT: Must use explicit origins when credentials (cookies) are involved.
# Set CORS_ORIGINS env var: "http://localhost:5173,http://localhost:3000"

_cors_env = os.environ.get("CORS_ORIGINS", "")
CORS_ORIGINS: list[str] = (
    [o.strip() for o in _cors_env.split(",") if o.strip()]
    if _cors_env
    else ["http://localhost:5173", "http://localhost:3000"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,      # Required for httpOnly cookies
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Auth Middleware ──────────────────────────────────────────────
# Protects ALL endpoints via cookie. Public paths are whitelisted.

PUBLIC_PATH_PREFIXES = (
    "/auth/",        # login, refresh, etc.
    "/health",       # health checks
    "/docs",         # Swagger UI
    "/openapi.json",
    "/redoc",
)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Global auth middleware — check JWT cookie tren moi request.

    Skip:
        - OPTIONS (CORS preflight)
        - Public paths (auth, health, docs)
        - WebSocket (xu ly rieng trong views)
    """
    async def dispatch(self, request, call_next):
        path = request.url.path

        # Allow CORS preflight
        if request.method == "OPTIONS":
            return await call_next(request)

        # Allow public paths
        if path == "/" or any(path.startswith(p) for p in PUBLIC_PATH_PREFIXES):
            return await call_next(request)

        # Skip WebSocket (handled separately in views)
        if request.scope.get("type") == "websocket":
            return await call_next(request)

        # Check JWT cookie
        access_token = request.cookies.get("access_token")
        if not access_token:
            return StarletteJSONResponse(
                status_code=401,
                content={"detail": "Not authenticated"},
            )

        payload = decode_token(access_token, expected_type="access")
        if not payload:
            return StarletteJSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired token"},
            )

        # Attach user info to request state
        request.state.user = payload
        return await call_next(request)


app.add_middleware(AuthMiddleware)


# ── Register routers ────────────────────────────────────────────

app.include_router(main_router)


# ── Health check ─────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/health")
async def health_check():
    """System health check."""
    health = {"api": "ok", "mongodb": "unknown", "redis": "unknown"}

    # Check MongoDB
    try:
        from app.db.mongo import get_motor_client
        client = get_motor_client()
        await client.admin.command("ping")
        health["mongodb"] = "ok"
    except Exception:
        health["mongodb"] = "error"

    # Check Redis (neu dung)
    # try:
    #     is_healthy = await redis_client.health_check()
    #     health["redis"] = "ok" if is_healthy else "error"
    # except Exception:
    #     health["redis"] = "error"

    return health
