# -*- coding: utf-8 -*-
"""
Custom Exceptions — Shared exception hierarchy for API modules.

Usage:
    from app.api.shared.exceptions import NotFoundError, ValidationError
    raise NotFoundError("Garage", garage_id)
"""
from fastapi import HTTPException
from typing import Optional, Dict, Any


class BaseAPIException(HTTPException):
    def __init__(self, status_code: int, message: str,
                 error_code: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        self.error_code = error_code
        self.details = details
        super().__init__(status_code=status_code, detail=message)


class ValidationError(BaseAPIException):
    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else None
        super().__init__(400, message, "VALIDATION_ERROR", details)


class NotFoundError(BaseAPIException):
    def __init__(self, resource: str, resource_id: Optional[str] = None):
        message = f"{resource} not found"
        if resource_id:
            message += f": {resource_id}"
        super().__init__(404, message, "NOT_FOUND")


class ConflictError(BaseAPIException):
    def __init__(self, message: str):
        super().__init__(409, message, "CONFLICT")


class InternalServerError(BaseAPIException):
    def __init__(self, message: str = "Internal server error"):
        super().__init__(500, message, "INTERNAL_ERROR")


class ServiceUnavailableError(BaseAPIException):
    def __init__(self, service: str):
        super().__init__(503, f"{service} service unavailable", "SERVICE_UNAVAILABLE")
