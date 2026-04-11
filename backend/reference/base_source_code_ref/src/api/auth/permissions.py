# -*- coding: utf-8 -*-
"""
RBAC Permissions — Role-Based Access Control.

Permission format: "{module}:{action}"
    Ví du: "camera:view", "user:create", "role:edit"

Usage trong views:
    @has_permission(["item:view"])
    async def get_items(current_user: dict = Depends(get_current_user)):
        ...

    @has_permission(["item:create", "item:edit"])  # can co IT NHAT 1
    async def create_item(current_user: dict = Depends(get_current_user)):
        ...

Super admin bypass:
    - tenant_id == "super_admin" -> skip moi check
    - permission "__all__" -> skip moi check
"""
from enum import Enum
from functools import wraps
from typing import Callable, List, Optional
from fastapi import HTTPException


class PermissionAction(str, Enum):
    """Cac action co the thuc hien tren resource."""
    VIEW = "view"
    EDIT = "edit"
    DELETE = "delete"
    CREATE = "create"
    CONFIG = "config"


class PermissionModule(str, Enum):
    """
    Cac module trong he thong.
    Them module moi khi tao feature moi.
    """
    ALL = "__all__"
    USER = "user"
    ROLE = "role"
    STORE = "store"
    TENANT = "tenant"
    SYSTEM = "system"
    # === Them module domain cua ban o day ===
    # PRODUCT = "product"
    # ORDER = "order"
    # REPORT = "report"


# Module -> list of permissions. Dung khi tao Role tu dong.
MODULE_PERMISSIONS = {
    "user":   ["user:view", "user:create", "user:edit", "user:delete"],
    "role":   ["role:view", "role:create", "role:edit", "role:delete"],
    "store":  ["store:view", "store:edit"],
    "tenant": ["tenant:view", "tenant:create", "tenant:edit", "tenant:delete"],
    "system": ["system:view", "system:config"],
    # === Them permission domain cua ban o day ===
    # "product": ["product:view", "product:create", "product:edit", "product:delete"],
    # "order":   ["order:view", "order:create", "order:edit"],
}

# Tat ca permissions co the gan cho role
ALL_PERMISSIONS = [p for perms in MODULE_PERMISSIONS.values() for p in perms]


async def get_permission(current_user: dict, required_permissions: List[str]) -> bool:
    """
    Check xem user co quyen thuc hien action khong.

    Logic:
        1. super_admin -> always True
        2. __all__ permission -> always True
        3. Khong yeu cau permission cu the -> chi can dang nhap
        4. User can co IT NHAT 1 permission trong required list
    """
    # Super admin bypass
    if (current_user.get("tenant_id") == "super_admin"
            or "super_admin" in current_user.get("role_ids", [])):
        return True

    user_perms = current_user.get("permissions", [])

    # __all__ = full access
    if "__all__" in user_perms:
        return True

    # Khong yeu cau quyen cu the -> chi can dang nhap
    if not required_permissions:
        return True

    # User can co 1 trong cac quyen duoc require
    for perm in user_perms:
        if perm in required_permissions:
            return True

    return False


def has_permission(permission: List[str] = None):
    """
    Decorator de bat cac yeu cau RBAC tren endpoint.

    Usage:
        @router.get("/items")
        @has_permission(["item:view"])
        async def get_items(current_user: dict = Depends(get_current_user)):
            ...

    Luu y: current_user PHAI co trong kwargs cua endpoint.
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

            import inspect
            if inspect.iscoroutinefunction(actual_func):
                return await actual_func(*args, **kwargs)
            else:
                return actual_func(*args, **kwargs)

        return wrapper
    return decorator
