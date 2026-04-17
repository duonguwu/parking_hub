# -*- coding: utf-8 -*-
"""User Utils — Business logic for user management (tenant-scoped staff)."""
import logging
from typing import List, Dict, Any

from fastapi import HTTPException
from app.api.user.user_models import UserModel
from app.api.auth.auth_utils import hash_password, get_user_by_username, get_user_by_email
from app.api.shared.tool.datetime_convert import get_current_time
from app.api.shared.tool.convert_object_id import convert_mongo_object_id

logger = logging.getLogger(__name__)


def format_user(doc) -> dict:
    if isinstance(doc, dict):
        data = doc
    else:
        data = doc.dump()
    return {
        "id": str(data.get("_id") or data.get("id") or ""),
        "tenant_id": data.get("tenant_id", ""),
        "username": data.get("username", ""),
        "email": data.get("email", ""),
        "phone": data.get("phone", ""),
        "name": data.get("name", ""),
        "role": data.get("role", ""),
        "is_active": data.get("is_active", True),
        "staff_profile": data.get("staff_profile", {}),
        "last_login": str(data.get("last_login", "")),
        "created_at": str(data.get("created_at", "")),
    }


async def get_users_in_tenant(current_user: dict) -> List[dict]:
    """Get all users within current tenant."""
    try:
        cursor = UserModel.find({}, current_user=current_user)
        docs = await cursor.to_list(length=200)
        return [format_user(doc) for doc in docs]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading users: {e}")
        raise HTTPException(status_code=500, detail="Failed to load users")


async def get_user_by_id_endpoint(user_id: str, current_user: dict) -> dict:
    oid = convert_mongo_object_id(user_id)
    if not oid:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    try:
        doc = await UserModel.find_one({"_id": oid}, current_user=current_user)
        if not doc:
            raise HTTPException(status_code=404, detail="User not found")
        return format_user(doc)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def create_staff_user(data: dict, current_user: dict) -> dict:
    """Create a staff user within the current tenant."""
    # Validate role is staff-level
    allowed_roles = ["garage_manager", "garage_staff"]
    role = data.get("role", "garage_staff")
    if role not in allowed_roles:
        raise HTTPException(status_code=400, detail=f"Role must be one of: {allowed_roles}")

    # Check uniqueness
    if await get_user_by_username(data["username"]):
        raise HTTPException(status_code=409, detail="Username already exists")
    if await get_user_by_email(data["email"]):
        raise HTTPException(status_code=409, detail="Email already exists")

    # Use raw insert to bypass umongo DictField + marshmallow v4 incompatibility
    doc_data = {
        "tenant_id": current_user["tenant_id"],
        "username": data["username"],
        "email": data["email"],
        "phone": data.get("phone", ""),
        "password_hash": hash_password(data["password"]),
        "name": data["name"],
        "role": role,
        "is_active": True,
        "staff_profile": data.get("staff_profile", {}),
        "customer_profile": {},
        "allowed_tenant_ids": [],
        "last_login": None,
        "created_at": get_current_time(),
        "updated_at": get_current_time(),
        "created_by": current_user.get("username", "system"),
        "updated_by": current_user.get("username", "system"),
    }
    insert_result = await UserModel.collection.insert_one(doc_data)

    result = await UserModel.collection.find_one({"_id": insert_result.inserted_id})
    return format_user(result)


async def update_user(user_id: str, update_data: dict, current_user: dict) -> bool:
    """Update user within tenant."""
    # Don't allow changing password through this endpoint
    update_data.pop("password", None)
    update_data.pop("password_hash", None)

    return await UserModel.update_with_tenant_check(
        doc_id=user_id,
        update_data=update_data,
        current_user=current_user,
        name_field="username",
    )


async def deactivate_user(user_id: str, current_user: dict) -> bool:
    """Soft-deactivate a user."""
    oid = convert_mongo_object_id(user_id)
    if not oid:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    # Can't deactivate yourself
    if user_id == current_user.get("user_id"):
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")

    doc = await UserModel.find_one({"_id": oid}, current_user=current_user)
    if not doc:
        raise HTTPException(status_code=404, detail="User not found")

    result = await UserModel.collection.update_one(
        {"_id": oid},
        {"$set": {"is_active": False, "updated_at": get_current_time(),
                  "updated_by": current_user.get("username", "system")}},
    )
    return result.modified_count > 0
