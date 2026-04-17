# -*- coding: utf-8 -*-
"""User Views — API endpoints for user management."""
from fastapi import APIRouter, Depends
from typing import Dict, Any

from app.api.user.user_schemas import UserCreateRequest, UserUpdateRequest
from app.api.user.user_utils import (
    get_users_in_tenant,
    get_user_by_id_endpoint,
    create_staff_user,
    update_user,
    deactivate_user,
)
from app.api.auth.dependencies import get_current_user
from app.api.auth.permissions import has_permission
from app.api.shared.common_utils import api_response
from app.api.shared.schemas import Operation, Resource

user_router = APIRouter(tags=["User Management"])


@user_router.get("/users")
@has_permission(["user:view"])
async def get_users(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Lấy danh sách users trong tenant."""
    data = await get_users_in_tenant(current_user)
    return api_response(Operation.RETRIEVED, Resource.USERS, data)


@user_router.get("/users/{user_id}")
@has_permission(["user:view"])
async def get_user(
    user_id: str,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Chi tiết user."""
    data = await get_user_by_id_endpoint(user_id, current_user)
    return api_response(Operation.RETRIEVED, Resource.USER, data)


@user_router.post("/users")
@has_permission(["user:create"])
async def create_user_endpoint(
    request: UserCreateRequest,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Tạo staff user mới trong tenant."""
    data = await create_staff_user(request.model_dump(), current_user)
    return api_response(Operation.CREATED, Resource.USER, data)


@user_router.put("/users/{user_id}")
@has_permission(["user:edit"])
async def update_user_endpoint(
    user_id: str,
    request: UserUpdateRequest,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Cập nhật thông tin user."""
    await update_user(user_id, request.model_dump(exclude_unset=True), current_user)
    return api_response(Operation.UPDATED, Resource.USER)


@user_router.delete("/users/{user_id}")
@has_permission(["user:delete"])
async def delete_user_endpoint(
    user_id: str,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Vô hiệu hóa user (soft delete)."""
    await deactivate_user(user_id, current_user)
    return api_response(Operation.DELETED, Resource.USER)
