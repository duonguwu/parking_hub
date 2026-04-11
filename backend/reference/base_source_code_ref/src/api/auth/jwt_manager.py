# -*- coding: utf-8 -*-
"""
JWT Manager — Issue and verify JWT tokens, stored in httpOnly cookies.

Token types:
    - access_token:  short-lived (30 min), path="/", dung cho moi request
    - refresh_token: long-lived (7 days), path="/auth", chi gui toi auth endpoints

Usage:
    from app.api.auth.jwt_manager import (
        create_access_token,
        create_refresh_token,
        decode_token,
        set_auth_cookies,
        clear_auth_cookies,
    )
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from fastapi import Response

from app.core.config import settings

logger = logging.getLogger(__name__)


# ─── Token creation ─────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a short-lived access token (default 30 min).

    Args:
        data: Payload dict, typically {"sub": user_id, "username": ..., "tenant_id": ..., "role_ids": [...]}
        expires_delta: Custom expiration (optional)
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access", "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a long-lived refresh token (default 7 days).

    Args:
        data: Payload dict (same as access token)
        expires_delta: Custom expiration (optional)
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    )
    to_encode.update({"exp": expire, "type": "refresh", "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


# ─── Token verification ─────────────────────────────────────────

def decode_token(token: str, expected_type: str = "access") -> Optional[dict]:
    """
    Decode and verify a JWT token.

    Args:
        token: JWT string
        expected_type: "access" or "refresh"

    Returns:
        Payload dict if valid, None if invalid/expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != expected_type:
            logger.warning(f"Token type mismatch: expected={expected_type}, got={payload.get('type')}")
            return None
        return payload
    except JWTError as e:
        logger.debug(f"JWT decode failed: {e}")
        return None


# ─── Cookie helpers ──────────────────────────────────────────────

def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    """
    Set httpOnly cookies for both access and refresh tokens.

    Security notes:
        - httponly=True: JS cannot read cookies (XSS protection)
        - samesite="lax": CSRF protection
        - secure=True: only send over HTTPS (enable in production!)
        - refresh_token path="/auth": only sent to auth endpoints
    """
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=False,       # TODO: set True when HTTPS in production
        path="/",
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=False,       # TODO: set True when HTTPS in production
        path="/auth",       # Only sent to /auth/* endpoints
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )


def clear_auth_cookies(response: Response):
    """Clear authentication cookies (logout)."""
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/auth")
