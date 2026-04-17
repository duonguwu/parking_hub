# -*- coding: utf-8 -*-
"""
JWT Manager — Issue and verify JWT tokens, stored in httpOnly cookies.

Token types:
    - access_token:  short-lived (60 min), path="/", dung cho moi request
    - refresh_token: long-lived (7 days), path="/auth", chi gui toi auth endpoints
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from fastapi import Response

from app.core.config import settings

logger = logging.getLogger(__name__)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access", "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    )
    to_encode.update({"exp": expire, "type": "refresh", "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str, expected_type: str = "access") -> Optional[dict]:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != expected_type:
            logger.warning(f"Token type mismatch: expected={expected_type}, got={payload.get('type')}")
            return None
        return payload
    except JWTError as e:
        logger.debug(f"JWT decode failed: {e}")
        return None


def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    response.set_cookie(
        key="access_token", value=access_token,
        httponly=True, samesite="lax", secure=False,
        path="/", max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token", value=refresh_token,
        httponly=True, samesite="lax", secure=False,
        path="/auth", max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )


def clear_auth_cookies(response: Response):
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/auth")
