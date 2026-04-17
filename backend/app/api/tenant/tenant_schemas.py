# -*- coding: utf-8 -*-
"""Tenant API Schemas."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class TenantUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[str] = None  # "active" | "suspended"
    subscription_plan: Optional[str] = None
    contact: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None
