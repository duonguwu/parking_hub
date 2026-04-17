# -*- coding: utf-8 -*-
"""
RBAC Permissions — Role-Based Access Control for WashMind.

Permission format: "{module}:{action}"
    e.g. "garage:view", "booking:create", "user:edit"

Usage:
    @router.get("/items")
    @has_permission(["item:view"])
    async def get_items(current_user: dict = Depends(get_current_user)):
        ...

    @router.post("/items")
    @has_permission(["item:create", "item:edit"])  # cần có ÍT NHẤT 1
    async def create_item(current_user: dict = Depends(get_current_user)):
        ...

Super admin bypass:
    - tenant_id == "super_admin" -> skip mọi check
    - permission "__all__" -> skip mọi check
"""
import inspect
from enum import Enum
from functools import wraps
from typing import Callable, List
from fastapi import Depends, HTTPException


class PermissionAction(str, Enum):
    VIEW = "view"
    CREATE = "create"
    EDIT = "edit"
    DELETE = "delete"
    CONFIG = "config"


class PermissionModule(str, Enum):
    ALL = "__all__"
    USER = "user"
    ROLE = "role"
    TENANT = "tenant"
    GARAGE = "garage"
    VEHICLE = "vehicle"
    BOOKING = "booking"
    SERVICE = "service"
    CAPACITY = "capacity"
    MATCHING = "matching"
    ANALYTICS = "analytics"
    SUBSCRIPTION = "subscription"
    FLEET = "fleet"
    SYSTEM = "system"


# Module → permissions mapping
MODULE_PERMISSIONS = {
    "user":         ["user:view", "user:create", "user:edit", "user:delete"],
    "role":         ["role:view", "role:create", "role:edit", "role:delete"],
    "tenant":       ["tenant:view", "tenant:create", "tenant:edit", "tenant:delete"],
    "garage":       ["garage:view", "garage:create", "garage:edit", "garage:delete"],
    "vehicle":      ["vehicle:view", "vehicle:create", "vehicle:edit", "vehicle:delete"],
    "booking":      ["booking:view", "booking:create", "booking:edit", "booking:delete"],
    "service":      ["service:view", "service:create", "service:edit", "service:delete"],
    "capacity":     ["capacity:view", "capacity:edit"],
    "matching":     ["matching:view"],
    "analytics":    ["analytics:view"],
    "subscription": ["subscription:view", "subscription:create", "subscription:edit"],
    "fleet":        ["fleet:view", "fleet:create", "fleet:edit"],
    "system":       ["system:view", "system:config"],
}

ALL_PERMISSIONS = [p for perms in MODULE_PERMISSIONS.values() for p in perms]

# ── Default role permission sets ─────────────────────────────────
ROLE_PERMISSIONS = {
    "super_admin": ["__all__"],
    "platform_ops": [
        "tenant:view", "tenant:create", "tenant:edit",
        "user:view", "user:create",
        "garage:view", "garage:edit",
        "booking:view",
        "analytics:view",
        "system:view", "system:config",
    ],
    "garage_owner": [
        "garage:view", "garage:edit",
        "user:view", "user:create", "user:edit", "user:delete",
        "role:view",
        "booking:view", "booking:create", "booking:edit",
        "service:view", "service:create", "service:edit",
        "capacity:view", "capacity:edit",
        "analytics:view",
    ],
    "garage_manager": [
        "garage:view",
        "user:view",
        "booking:view", "booking:create", "booking:edit",
        "service:view",
        "capacity:view", "capacity:edit",
        "analytics:view",
    ],
    "garage_staff": [
        "booking:view", "booking:edit",
        "capacity:view", "capacity:edit",
    ],
    "customer": [
        "garage:view",
        "vehicle:view", "vehicle:create", "vehicle:edit", "vehicle:delete",
        "booking:view", "booking:create",
        "matching:view",
    ],
    "fleet_manager": [
        "garage:view",
        "vehicle:view", "vehicle:create", "vehicle:edit",
        "booking:view", "booking:create",
        "matching:view",
        "fleet:view", "fleet:create", "fleet:edit",
    ],
}


def get_permissions_for_role(role: str) -> list:
    """Get permission list for a given role name."""
    return ROLE_PERMISSIONS.get(role, [])


async def get_permission(current_user: dict, required_permissions: List[str]) -> bool:
    """
    Check xem user có quyền thực hiện action không.
    Logic: super_admin → True | __all__ → True | cần ÍT NHẤT 1 permission trong list
    """
    if current_user.get("tenant_id") == "super_admin":
        return True

    user_perms = current_user.get("permissions", [])

    if "__all__" in user_perms:
        return True

    if not required_permissions:
        return True

    for perm in user_perms:
        if perm in required_permissions:
            return True

    return False


def require_permission(permissions: List[str] = None):
    """
    FastAPI Depends factory for RBAC — preferred over @has_permission decorator.

    Usage (trong views):
        async def endpoint(
            input_data: BodyModel,
            current_user: dict = Depends(require_permission(["garage:view"])),
        ):
            ...

    Dùng Depends thay @has_permission vì FastAPI không reliable resolve
    Pydantic body params qua @wraps + *args/**kwargs wrapper.
    """
    if permissions is None:
        permissions = []

    # Local import tránh circular: permissions.py ← dependencies.py ← jwt_manager.py
    from app.api.auth.dependencies import get_current_user

    async def _check(current_user: dict = Depends(get_current_user)) -> dict:
        if not await get_permission(current_user, permissions):
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to perform this action.",
            )
        return current_user

    return _check


def has_permission(permission: List[str] = None):
    """
    Decorator để bắt các yêu cầu RBAC trên endpoint.

    Giữ nguyên function signature (parameters, annotations, defaults)
    để FastAPI có thể resolve path params và dependency injection đúng cách.

    Usage:
        @router.get("/items/{item_id}")
        @has_permission(["item:view"])
        async def get_items(item_id: str, current_user: dict = Depends(get_current_user)):
            ...
    """
    if permission is None:
        permission = []

    def decorator(actual_func: Callable):
        @wraps(actual_func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")

            if current_user is None:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication credentials were not provided",
                )

            is_allowed = await get_permission(current_user, permission)

            if not is_allowed:
                raise HTTPException(
                    status_code=403,
                    detail="You do not have permission to perform this action.",
                )

            if inspect.iscoroutinefunction(actual_func):
                return await actual_func(*args, **kwargs)
            else:
                return actual_func(*args, **kwargs)

        # ── Preserve original function signature for FastAPI ──
        # FastAPI inspects function signature to resolve path params,
        # query params, and Depends. @wraps preserves __wrapped__ but
        # FastAPI needs the actual signature on the wrapper function.
        wrapper.__signature__ = inspect.signature(actual_func)

        return wrapper
    return decorator
