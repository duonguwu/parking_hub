# -*- coding: utf-8 -*-
"""
Auth Utils — Business logic for authentication, user creation, password hashing.
"""
import logging
from typing import Optional, Dict, Any

from fastapi import HTTPException
from passlib.context import CryptContext

from app.api.auth.jwt_manager import create_access_token, create_refresh_token
from app.api.auth.permissions import get_permissions_for_role
from app.api.shared.tool.datetime_convert import get_current_time
from app.api.shared.tool.convert_object_id import convert_mongo_object_id

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _build_token_payload(user_doc: dict) -> dict:
    """Build JWT payload from user document."""
    user_id = str(user_doc.get("_id", user_doc.get("user_id", "")))
    role = user_doc.get("role", "customer")
    permissions = get_permissions_for_role(role)

    return {
        "sub": user_id,
        "username": user_doc.get("username", ""),
        "name": user_doc.get("name", ""),
        "tenant_id": user_doc.get("tenant_id", ""),
        "role": role,
        "permissions": permissions,
        "allowed_tenant_ids": user_doc.get("allowed_tenant_ids"),
    }


def create_tokens_for_user(user_doc: dict) -> tuple:
    """Create access + refresh tokens for a user."""
    payload = _build_token_payload(user_doc)
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)
    return access_token, refresh_token


def format_user_response(user_doc: dict) -> dict:
    """Format user document for API response."""
    return {
        "user_id": str(user_doc.get("_id", "")),
        "username": user_doc.get("username", ""),
        "name": user_doc.get("name", ""),
        "email": user_doc.get("email", ""),
        "phone": user_doc.get("phone", ""),
        "role": user_doc.get("role", ""),
        "tenant_id": user_doc.get("tenant_id", ""),
        "is_active": user_doc.get("is_active", True),
    }


# ─── Database Operations ────────────────────────────────────────

async def get_user_by_username(username: str) -> Optional[dict]:
    """Find user by username (direct collection query, no tenant filter)."""
    from app.api.user.user_models import UserModel
    doc = await UserModel.collection.find_one({"username": username})
    return doc


async def get_user_by_email(email: str) -> Optional[dict]:
    """Find user by email."""
    from app.api.user.user_models import UserModel
    doc = await UserModel.collection.find_one({"email": email})
    return doc


async def get_user_by_id(user_id: str) -> Optional[dict]:
    """Find user by ID."""
    from app.api.user.user_models import UserModel
    oid = convert_mongo_object_id(user_id)
    if not oid:
        return None
    doc = await UserModel.collection.find_one({"_id": oid})
    return doc


async def authenticate_user(username: str, password: str) -> dict:
    """Authenticate user with username/email + password."""
    # Try username first, then email
    user = await get_user_by_username(username)
    if not user:
        user = await get_user_by_email(username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.get("is_active", True):
        raise HTTPException(status_code=401, detail="Account is deactivated")

    if not verify_password(password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Update last_login
    from app.api.user.user_models import UserModel
    await UserModel.collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": get_current_time()}}
    )

    return user


async def register_customer(data: dict) -> dict:
    """Register a new customer user."""
    from app.api.user.user_models import UserModel

    # Check uniqueness
    if await get_user_by_username(data["username"]):
        raise HTTPException(status_code=409, detail="Username already exists")
    if await get_user_by_email(data["email"]):
        raise HTTPException(status_code=409, detail="Email already exists")

    user_doc = UserModel(
        tenant_id="platform",
        username=data["username"],
        email=data["email"],
        phone=data["phone"],
        password_hash=hash_password(data["password"]),
        name=data["name"],
        role="customer",
        is_active=True,
        created_at=get_current_time(),
        updated_at=get_current_time(),
        created_by="self_register",
        updated_by="self_register",
    )
    await user_doc.commit()

    result = await UserModel.collection.find_one({"_id": user_doc.pk})
    return result


async def register_garage(data: dict) -> dict:
    """
    Register a new garage — creates:
    1. Tenant document
    2. User (garage_owner) document
    3. Garage document
    Returns the created user document.
    """
    from app.api.user.user_models import UserModel
    from app.api.tenant.tenant_models import TenantModel
    from app.api.garage.garage_models import GarageModel
    import re

    # Check uniqueness
    if await get_user_by_username(data["username"]):
        raise HTTPException(status_code=409, detail="Username already exists")
    if await get_user_by_email(data["email"]):
        raise HTTPException(status_code=409, detail="Email already exists")

    # Generate slug from garage name
    slug = re.sub(r'[^a-z0-9]+', '-', data["garage_name"].lower()).strip('-')

    # Check slug uniqueness
    existing_tenant = await TenantModel.collection.find_one({"slug": slug})
    if existing_tenant:
        slug = f"{slug}-{str(get_current_time().timestamp())[-4:]}"

    # 1. Create Tenant
    tenant_doc = TenantModel(
        name=data["garage_name"],
        slug=slug,
        type="garage",
        status="active",
        contact={
            "phone": data["phone"],
            "email": data["email"],
            "address": f"{data['address_street']}, {data['address_district']}, {data['address_city']}"
        },
        subscription_plan="free",
        settings={
            "timezone": "Asia/Ho_Chi_Minh",
            "currency": "VND",
            "language": "vi",
        },
        tenant_id=slug,  # Self-referencing for TenantAwareDocument
        created_at=get_current_time(),
        updated_at=get_current_time(),
        created_by="self_register",
        updated_by="self_register",
    )
    await tenant_doc.commit()

    # 2. Create User (garage_owner)
    user_doc = UserModel(
        tenant_id=slug,
        username=data["username"],
        email=data["email"],
        phone=data["phone"],
        password_hash=hash_password(data["password"]),
        name=data["owner_name"],
        role="garage_owner",
        is_active=True,
        created_at=get_current_time(),
        updated_at=get_current_time(),
        created_by="self_register",
        updated_by="self_register",
    )
    await user_doc.commit()

    # Update tenant with owner_user_id
    await TenantModel.collection.update_one(
        {"_id": tenant_doc.pk},
        {"$set": {"owner_user_id": str(user_doc.pk)}}
    )

    # 3. Create Garage
    garage_doc = GarageModel(
        tenant_id=slug,
        name=data["garage_name"],
        slug=slug,
        location={
            "type": "Point",
            "coordinates": [data["longitude"], data["latitude"]],
        },
        address={
            "street": data["address_street"],
            "district": data["address_district"],
            "city": data["address_city"],
            "province": data.get("address_province", ""),
        },
        tier=1,  # Default: Basic
        tier_score=0.0,
        capacity={
            "total_bays": data.get("total_bays", 2),
            "max_vehicles_per_hour": data.get("total_bays", 2) * 2,
            "avg_processing_time_minutes": 30,
        },
        status="active",
        is_verified=False,
        is_accepting_bookings=True,
        current_load={
            "vehicles_in_service": 0,
            "vehicles_waiting": 0,
            "estimated_wait_minutes": 0,
        },
        created_at=get_current_time(),
        updated_at=get_current_time(),
        created_by=data["username"],
        updated_by=data["username"],
    )
    await garage_doc.commit()

    result = await UserModel.collection.find_one({"_id": user_doc.pk})
    return result


async def seed_super_admin():
    """Seed super admin account on startup (idempotent)."""
    from app.core.config import settings

    if not settings.SUPER_ADMIN_PASSWORD:
        logger.warning("SUPER_ADMIN_PASSWORD not set, skipping seed")
        return

    existing = await get_user_by_username(settings.SUPER_ADMIN_USERNAME)
    if existing:
        logger.info("Super admin already exists, skipping seed")
        return

    from app.api.user.user_models import UserModel

    admin_doc = UserModel(
        tenant_id="super_admin",
        username=settings.SUPER_ADMIN_USERNAME,
        email="admin@washmind.vn",
        phone="0000000000",
        password_hash=hash_password(settings.SUPER_ADMIN_PASSWORD),
        name="Super Admin",
        role="super_admin",
        is_active=True,
        created_at=get_current_time(),
        updated_at=get_current_time(),
        created_by="system",
        updated_by="system",
    )
    await admin_doc.commit()
    logger.info(f"Super admin seeded: {settings.SUPER_ADMIN_USERNAME}")
