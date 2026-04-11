# -*- coding: utf-8 -*-
"""
Custom Exceptions — Shared exception hierarchy for API modules.

Usage:
    from app.api.shared.exceptions import NotFoundError, ValidationError

    raise NotFoundError("User", user_id)
    raise ValidationError("Email is required", field="email")
    raise ConflictError("Username already exists")

Tat ca exceptions ke thua HTTPException nen FastAPI tu dong
tra ve JSON response voi status code tuong ung.
"""
from fastapi import HTTPException
from typing import Optional, Dict, Any


class BaseAPIException(HTTPException):
    """Base exception class for API errors."""

    def __init__(
        self,
        status_code: int,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.error_code = error_code
        self.details = details
        super().__init__(status_code=status_code, detail=message)


class ValidationError(BaseAPIException):
    """Validation error — 400 Bad Request."""

    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else None
        super().__init__(
            status_code=400,
            message=message,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class NotFoundError(BaseAPIException):
    """Resource not found — 404 Not Found."""

    def __init__(self, resource: str, resource_id: Optional[str] = None):
        message = f"{resource} not found"
        if resource_id:
            message += f": {resource_id}"
        super().__init__(
            status_code=404,
            message=message,
            error_code="NOT_FOUND",
        )


class ConflictError(BaseAPIException):
    """Resource conflict — 409 Conflict."""

    def __init__(self, message: str):
        super().__init__(
            status_code=409,
            message=message,
            error_code="CONFLICT",
        )


class InternalServerError(BaseAPIException):
    """Internal server error — 500."""

    def __init__(self, message: str = "Internal server error"):
        super().__init__(
            status_code=500,
            message=message,
            error_code="INTERNAL_ERROR",
        )


class ServiceUnavailableError(BaseAPIException):
    """Service unavailable — 503."""

    def __init__(self, service: str):
        super().__init__(
            status_code=503,
            message=f"{service} service unavailable",
            error_code="SERVICE_UNAVAILABLE",
        )
