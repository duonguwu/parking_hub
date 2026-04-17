# -*- coding: utf-8 -*-
"""
WashMind Backend — FastAPI Application Entry Point

Usage:
    uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""
import logging
import os

from dotenv import load_dotenv
load_dotenv()

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

# ── Setup logging ────────────────────────────────────────────────
setup_logging(service="main", console_level=logging.INFO, file_level=logging.DEBUG)
logger = logging.getLogger(__name__)


# ── Lifespan (startup + shutdown) ────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──
    try:
        # 1. Initialize MongoDB
        init_mongo()

        # 2. Ensure indexes
        await ensure_indexes()

        # 3. Seed super admin
        from app.api.auth.auth_utils import seed_super_admin
        await seed_super_admin()

        logger.info("🚀 WashMind Backend started successfully")

    except Exception as e:
        logger.critical(f"Startup failed: {e}", exc_info=True)
        raise

    yield

    # ── Shutdown ──
    try:
        logger.info("Shutting down services...")
        close_mongo()
        logger.info("Shutdown completed")
    except Exception as e:
        logger.error(f"Shutdown error: {e}", exc_info=True)


async def ensure_indexes():
    """Create MongoDB indexes for all collections."""
    from app.api.user.user_models import UserModel
    from app.api.tenant.tenant_models import TenantModel
    from app.api.garage.garage_models import GarageModel
    from app.api.vehicle.vehicle_models import VehicleModel

    try:
        # Users
        await UserModel.collection.create_index("username", unique=True)
        await UserModel.collection.create_index("email", unique=True)
        await UserModel.collection.create_index("phone")
        await UserModel.collection.create_index([("tenant_id", 1), ("role", 1)])

        # Tenants
        await TenantModel.collection.create_index("slug", unique=True)
        await TenantModel.collection.create_index("status")

        # Garages
        await GarageModel.collection.create_index([("location", "2dsphere")])
        await GarageModel.collection.create_index("tenant_id")
        await GarageModel.collection.create_index([("tier", 1), ("status", 1)])
        await GarageModel.collection.create_index([("status", 1), ("is_accepting_bookings", 1)])
        await GarageModel.collection.create_index("slug")

        # Vehicles
        await VehicleModel.collection.create_index("owner_user_id")
        await VehicleModel.collection.create_index("license_plate", unique=True)

        logger.info("✅ MongoDB indexes ensured")
    except Exception as e:
        logger.warning(f"Index creation warning: {e}")


# ── FastAPI App ──────────────────────────────────────────────────

app = FastAPI(
    title="WashMind API",
    description="Intelligent dispatch system for car wash network",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


# ── CORS Middleware ──────────────────────────────────────────────

_cors_env = os.environ.get("CORS_ORIGINS", "")
CORS_ORIGINS: list[str] = (
    [o.strip() for o in _cors_env.split(",") if o.strip()]
    if _cors_env
    else ["http://localhost:5173", "http://localhost:3000"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Auth Middleware ──────────────────────────────────────────────

PUBLIC_PATH_PREFIXES = (
    "/auth/",
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/garages/nearby",  # Public search
)


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        path = request.url.path

        if request.method == "OPTIONS":
            return await call_next(request)

        if path == "/" or any(path.startswith(p) for p in PUBLIC_PATH_PREFIXES):
            return await call_next(request)

        if request.scope.get("type") == "websocket":
            return await call_next(request)

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

        request.state.user = payload
        return await call_next(request)


app.add_middleware(AuthMiddleware)


# ── Register routers ────────────────────────────────────────────

app.include_router(main_router)


# ── Health check ─────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "ok", "app": "WashMind", "version": settings.APP_VERSION}


@app.get("/health")
async def health_check():
    health = {"api": "ok", "mongodb": "unknown"}

    try:
        from app.db.mongo import get_motor_client
        client = get_motor_client()
        await client.admin.command("ping")
        health["mongodb"] = "ok"
    except Exception:
        health["mongodb"] = "error"

    return health
