# -*- coding: utf-8 -*-
"""
Auth Dependencies — FastAPI Depends for authentication.

Returns dict:
    {
        "user_id": str,
        "username": str,
        "name": str,
        "tenant_id": str,
        "role": str,
        "permissions": [str],
        "allowed_tenant_ids": [str] or None,
    }
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
    """Extract and verify current user from JWT cookie."""
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

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

    # TODO: Phase 2 — lookup DB to verify user still active
    return {
        "user_id": user_id,
        "username": payload.get("username", ""),
        "name": payload.get("name", ""),
        "tenant_id": payload.get("tenant_id", ""),
        "role": payload.get("role", ""),
        "permissions": payload.get("permissions", []),
        "allowed_tenant_ids": payload.get("allowed_tenant_ids"),
    }


async def get_current_user_optional(
    access_token: Optional[str] = Cookie(default=None),
) -> Optional[Dict[str, Any]]:
    """
    Same as get_current_user but returns None instead of raising 401
    when no/invalid cookie. Use for endpoints where auth is optional
    (public search with personalization if logged in).
    """
    if not access_token:
        return None
    payload = decode_token(access_token, expected_type="access")
    if not payload or not payload.get("sub"):
        return None
    return {
        "user_id": payload.get("sub"),
        "username": payload.get("username", ""),
        "name": payload.get("name", ""),
        "tenant_id": payload.get("tenant_id", ""),
        "role": payload.get("role", ""),
        "permissions": payload.get("permissions", []),
        "allowed_tenant_ids": payload.get("allowed_tenant_ids"),
    }
