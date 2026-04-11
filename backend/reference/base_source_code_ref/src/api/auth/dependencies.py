# -*- coding: utf-8 -*-
"""
Auth Dependencies — FastAPI Depends for authentication.

Central auth dependency. Every protected endpoint uses:
    current_user = Depends(get_current_user)

Returns dict:
    {
        "user_id": str,
        "username": str,
        "name": str,
        "tenant_id": str,
        "role_ids": [str],
        "auth_source": str,        # "basic" or "sso"
        "permissions": [str],       # ["camera:view", "user:create", ...]
        "allowed_tenant_ids": [str] or None,  # for center managers
    }

Extensibility:
    - Phase 1: JWT from httpOnly cookie only
    - Phase 3: Add Bearer token support (SSO) -> same output dict
"""
import logging
from typing import Optional, Dict, Any

from fastapi import Cookie, HTTPException, status, Request

from app.api.auth.jwt_manager import decode_token

logger = logging.getLogger(__name__)


async def get_current_user(
    request: Request,
    access_token: Optional[str] = Cookie(default=None),
) -> Dict[str, Any]:
    """
    Extract and verify current user from JWT cookie.

    Flow:
        1. Read access_token from httpOnly cookie
        2. Decode JWT, verify type == "access"
        3. Lookup user in DB, verify is_active
        4. Resolve permissions from roles
        5. Return user dict

    Raises:
        HTTPException(401) if not authenticated
    """
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    # Decode JWT
    payload = decode_token(access_token, expected_type="access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # ─── Verify user still exists and is active ─────────────────
    # TODO: Import tu auth_utils cua du an moi
    # from app.api.auth.auth_utils import get_user_by_id, resolve_user_permissions_and_tenants
    # user = await get_user_by_id(user_id)
    # if not user or not user.get("is_active"):
    #     raise HTTPException(status_code=401, detail="User not found or deactivated")
    # user = await resolve_user_permissions_and_tenants(user)

    # ─── Placeholder: dung payload tu JWT ────────────────────────
    # Trong production, nen lookup DB de verify user con active
    return {
        "user_id": user_id,
        "username": payload.get("username", ""),
        "name": payload.get("name", ""),
        "tenant_id": payload.get("tenant_id", ""),
        "role_ids": payload.get("role_ids", []),
        "auth_source": payload.get("auth_source", "basic"),
        "permissions": payload.get("permissions", []),
        "allowed_tenant_ids": payload.get("allowed_tenant_ids"),
    }
