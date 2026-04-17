# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends

from src.api_service.core.constansts.permission import (
    PermissionAction,
    PermissionModule,
)
from src.api_service.core.decorator.has_permission import has_permission
from src.api_service.core.response_api.response_success import (
    ApiResponse,
)

from ..schemas.user_info_schema import UpdateUserInfo
from ..utils.sso_util import (
    sso_fpt_get_user_in_jwt,
)
from ..utils.user_utils import get_all_user_by_admin, update_user_info_by_admin

user_router = APIRouter(prefix="/user", tags=["User Info"])


@user_router.post("/get_user_info", response_model=ApiResponse)
async def get_user_info(
    current_user: dict = Depends(sso_fpt_get_user_in_jwt)
):

    return {"success": True, "data": [current_user]}


@user_router.post("/get_user_by_admin", response_model=ApiResponse)
@has_permission(permission=[PermissionModule.ADMIN_USER.value + ":" + PermissionAction.VIEW.value])
async def get_user_by_admin(
    current_user: dict = Depends(sso_fpt_get_user_in_jwt)
):
    total, list_user = await get_all_user_by_admin(current_user)

    return {
        "success": True,
        "data": list_user,
        "length": total
    }


@user_router.post("/update_user_info_by_admin", response_model=ApiResponse)
@has_permission(permission=[PermissionModule.ADMIN_USER.value + ":" + PermissionAction.EDIT.value])
async def update_user_info_endpoint(
    input_data: UpdateUserInfo,
    current_user: dict = Depends(sso_fpt_get_user_in_jwt)
):
    result = await update_user_info_by_admin(input_data, current_user)

    return {"success": result}
