# -*- coding: utf-8 -*-
"""User Views — POST-based API endpoints for user management."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any

from app.api.user.user_schemas import UserCreateRequest, UserUpdateRequest
from app.api.user.user_utils import (
    get_users_in_tenant,
    get_user_by_id_endpoint,
    create_staff_user,
    update_user,
    deactivate_user,
)
from app.api.auth.permissions import require_permission
from app.api.shared.common_utils import api_response
from app.api.shared.schemas import Operation, Resource

user_router = APIRouter(prefix="/user", tags=["User Management"])


class UserIdInput(BaseModel):
    id: str = Field(..., min_length=1)


class UserUpdateInput(UserUpdateRequest):
    id: str = Field(..., min_length=1)


@user_router.post("/get_all")
async def get_users(
    current_user: dict = Depends(require_permission(["user:view"])),
) -> Dict[str, Any]:
    data = await get_users_in_tenant(current_user)
    return api_response(Operation.RETRIEVED, Resource.USERS, data)


@user_router.post("/get_by_id")
async def get_user(
    input_data: UserIdInput,
    current_user: dict = Depends(require_permission(["user:view"])),
) -> Dict[str, Any]:
    data = await get_user_by_id_endpoint(input_data.id, current_user)
    return api_response(Operation.RETRIEVED, Resource.USER, data)


@user_router.post("/create")
async def create_user_endpoint(
    input_data: UserCreateRequest,
    current_user: dict = Depends(require_permission(["user:create"])),
) -> Dict[str, Any]:
    data = await create_staff_user(input_data.model_dump(), current_user)
    return api_response(Operation.CREATED, Resource.USER, data)


@user_router.post("/update")
async def update_user_endpoint(
    input_data: UserUpdateInput,
    current_user: dict = Depends(require_permission(["user:edit"])),
) -> Dict[str, Any]:
    update_data = input_data.model_dump(exclude_unset=True, exclude={"id"})
    await update_user(input_data.id, update_data, current_user)
    return api_response(Operation.UPDATED, Resource.USER)


@user_router.post("/delete")
async def delete_user_endpoint(
    input_data: UserIdInput,
    current_user: dict = Depends(require_permission(["user:delete"])),
) -> Dict[str, Any]:
    await deactivate_user(input_data.id, current_user)
    return api_response(Operation.DELETED, Resource.USER)
