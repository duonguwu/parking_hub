# -*- coding: utf-8 -*-
"""Tenant Views — API endpoints for tenant management (admin)."""
from fastapi import APIRouter, Depends, Query
from typing import Dict, Any, Optional

from app.api.tenant.tenant_schemas import TenantUpdateRequest
from app.api.tenant.tenant_utils import (
    get_all_tenants,
    get_tenant_by_id,
    update_tenant,
)
from app.api.auth.dependencies import get_current_user
from app.api.auth.permissions import has_permission
from app.api.shared.common_utils import api_response
from app.api.shared.schemas import Operation, Resource

tenant_router = APIRouter(tags=["Tenant Management"])


@tenant_router.get("/tenants")
@has_permission(["tenant:view"])
async def get_tenants(
    status: Optional[str] = Query(default=None),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Lấy danh sách tenants (admin only)."""
    data = await get_all_tenants(current_user, status_filter=status)
    return api_response(Operation.RETRIEVED, Resource.TENANTS, data)


@tenant_router.get("/tenants/{tenant_id}")
@has_permission(["tenant:view"])
async def get_tenant(
    tenant_id: str,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Chi tiết tenant."""
    data = await get_tenant_by_id(tenant_id, current_user)
    return api_response(Operation.RETRIEVED, Resource.TENANT, data)


@tenant_router.put("/tenants/{tenant_id}")
@has_permission(["tenant:edit"])
async def update_tenant_endpoint(
    tenant_id: str,
    request: TenantUpdateRequest,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Cập nhật tenant (admin)."""
    await update_tenant(tenant_id, request.model_dump(exclude_unset=True), current_user)
    return api_response(Operation.UPDATED, Resource.TENANT)
