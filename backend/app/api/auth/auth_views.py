# -*- coding: utf-8 -*-
"""
Auth Views — API endpoints for authentication.
"""
from fastapi import APIRouter, Depends, Response, Cookie
from typing import Dict, Any, Optional

from app.api.auth.auth_schemas import (
    LoginRequest,
    RegisterCustomerRequest,
    RegisterGarageRequest,
)
from app.api.auth.auth_utils import (
    authenticate_user,
    register_customer,
    register_garage,
    create_tokens_for_user,
    format_user_response,
)
from app.api.auth.jwt_manager import (
    set_auth_cookies,
    clear_auth_cookies,
    decode_token,
    create_access_token,
)
from app.api.auth.dependencies import get_current_user
from app.api.auth.permissions import get_permissions_for_role
from app.api.shared.common_utils import api_response
from app.api.shared.schemas import Operation, Resource

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/login")
async def login(request: LoginRequest, response: Response) -> Dict[str, Any]:
    """Đăng nhập bằng username/email + password."""
    user = await authenticate_user(request.username, request.password)
    access_token, refresh_token = create_tokens_for_user(user)
    set_auth_cookies(response, access_token, refresh_token)

    return api_response(
        operation=Operation.PROCESSED,
        resource=Resource.AUTH,
        data={"user": format_user_response(user)},
        message="Login successful",
    )


@auth_router.post("/register")
async def register_customer_endpoint(
    request: RegisterCustomerRequest,
    response: Response,
) -> Dict[str, Any]:
    """Đăng ký tài khoản customer mới."""
    user = await register_customer(request.model_dump())
    access_token, refresh_token = create_tokens_for_user(user)
    set_auth_cookies(response, access_token, refresh_token)

    return api_response(
        operation=Operation.CREATED,
        resource=Resource.USER,
        data={"user": format_user_response(user)},
        message="Customer registered successfully",
    )


@auth_router.post("/register-garage")
async def register_garage_endpoint(
    request: RegisterGarageRequest,
    response: Response,
) -> Dict[str, Any]:
    """Đăng ký gara mới — tạo tenant + user (garage_owner) + garage."""
    user = await register_garage(request.model_dump())
    access_token, refresh_token = create_tokens_for_user(user)
    set_auth_cookies(response, access_token, refresh_token)

    return api_response(
        operation=Operation.CREATED,
        resource=Resource.GARAGE,
        data={"user": format_user_response(user)},
        message="Garage registered successfully",
    )


@auth_router.post("/refresh")
async def refresh_token(
    response: Response,
    refresh_token: Optional[str] = Cookie(default=None),
) -> Dict[str, Any]:
    """Refresh access token using refresh token cookie."""
    if not refresh_token:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="No refresh token")

    payload = decode_token(refresh_token, expected_type="refresh")
    if not payload:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    # Create new access token with same payload
    new_payload = {
        "sub": payload.get("sub"),
        "username": payload.get("username"),
        "name": payload.get("name"),
        "tenant_id": payload.get("tenant_id"),
        "role": payload.get("role"),
        "permissions": payload.get("permissions", []),
        "allowed_tenant_ids": payload.get("allowed_tenant_ids"),
    }
    new_access_token = create_access_token(new_payload)

    response.set_cookie(
        key="access_token", value=new_access_token,
        httponly=True, samesite="lax", secure=False, path="/",
    )

    return api_response(
        operation=Operation.PROCESSED,
        resource=Resource.TOKEN,
        message="Token refreshed successfully",
    )


@auth_router.post("/logout")
async def logout(response: Response) -> Dict[str, Any]:
    """Đăng xuất — xóa cookies."""
    clear_auth_cookies(response)
    return api_response(
        operation=Operation.PROCESSED,
        resource=Resource.AUTH,
        message="Logged out successfully",
    )


@auth_router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Lấy thông tin user hiện tại."""
    return api_response(
        operation=Operation.RETRIEVED,
        resource=Resource.USER,
        data=current_user,
    )
