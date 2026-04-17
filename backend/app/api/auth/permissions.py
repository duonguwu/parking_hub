# -*- coding: utf-8 -*-
"""
RBAC Permissions — Role-Based Access Control for WashMind.

Permission format: "{module}:{action}"
    e.g. "garage:view", "booking:create", "user:edit"

Usage:
    @has_permission(["garage:view"])
    async def get_garages(current_user: dict = Depends(get_current_user)):
        ...

Super admin bypass: tenant_id == "super_admin" → skip all checks
"""
from enum import Enum
from functools import wraps
from typing import Callable, List
from fastapi import HTTPException


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
    # Super admin bypass
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


def has_permission(permission: List[str] = None):
    """Decorator to enforce RBAC on endpoint."""
    if permission is None:
        permission = []

    def decorator(actual_func: Callable):
        @wraps(actual_func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if current_user is None:
                raise HTTPException(status_code=401, detail="Authentication credentials were not provided")

            is_allowed = await get_permission(current_user, permission)
            if not is_allowed:
                raise HTTPException(status_code=403, detail="You do not have permission to perform this action.")

            import inspect
            if inspect.iscoroutinefunction(actual_func):
                return await actual_func(*args, **kwargs)
            else:
                return actual_func(*args, **kwargs)

        return wrapper
    return decorator
