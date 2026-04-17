# -*- coding: utf-8 -*-
"""Auth API Schemas — Request/Response models for authentication."""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List


class LoginRequest(BaseModel):
    username: str = Field(..., description="Username hoặc email", min_length=1)
    password: str = Field(..., description="Mật khẩu", min_length=6)


class RegisterCustomerRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., description="Email")
    phone: str = Field(..., min_length=10, max_length=15)
    password: str = Field(..., min_length=6, max_length=128)
    name: str = Field(..., min_length=1, max_length=100)


class RegisterGarageRequest(BaseModel):
    """Đăng ký gara mới — tạo tenant + garage_owner user + garage."""
    # Owner info
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., description="Email")
    phone: str = Field(..., min_length=10, max_length=15)
    password: str = Field(..., min_length=6, max_length=128)
    owner_name: str = Field(..., min_length=1, max_length=100)

    # Garage info
    garage_name: str = Field(..., min_length=1, max_length=200)
    address_street: str = Field(..., min_length=1)
    address_district: str = Field(..., min_length=1)
    address_city: str = Field(..., min_length=1)
    address_province: str = Field(default="")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    total_bays: int = Field(default=2, ge=1, le=50)


class UserResponse(BaseModel):
    user_id: str
    username: str
    name: str
    email: str
    phone: str
    role: str
    tenant_id: str
    is_active: bool


class AuthResponse(BaseModel):
    user: UserResponse
    message: str = "Login successful"
