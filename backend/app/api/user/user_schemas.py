# -*- coding: utf-8 -*-
"""User API Schemas."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class UserCreateRequest(BaseModel):
    """Tạo user mới trong tenant (staff cho gara)."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(...)
    phone: str = Field(default="", max_length=15)
    password: str = Field(..., min_length=6, max_length=128)
    name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(default="garage_staff")
    # "garage_manager" | "garage_staff"
    staff_profile: Optional[Dict[str, Any]] = None
    # { position: "washer" | "cashier" | "manager", shift: "morning" | "afternoon" | "full" }


class UserUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=15)
    role: Optional[str] = None
    is_active: Optional[bool] = None
    staff_profile: Optional[Dict[str, Any]] = None
