# -*- coding: utf-8 -*-
"""Tenant Views — POST-based API endpoints for tenant management."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from app.api.tenant.tenant_utils import (
    get_all_tenants,
    get_tenant_by_id,
    update_tenant,
)
from app.api.auth.permissions import require_permission
from app.api.shared.common_utils import api_response
from app.api.shared.schemas import Operation, Resource

tenant_router = APIRouter(prefix="/tenant", tags=["Tenant Management"])


class TenantFilterRequest(BaseModel):
    status: Optional[str] = None


class TenantIdInput(BaseModel):
    id: str = Field(..., min_length=1)


class TenantUpdateInput(BaseModel):
    id: str = Field(..., min_length=1)
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[str] = None
    subscription_plan: Optional[str] = None
    contact: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None


@tenant_router.post("/get_all")
async def get_tenants(
    input_data: TenantFilterRequest = TenantFilterRequest(),
    current_user: dict = Depends(require_permission(["tenant:view"])),
) -> Dict[str, Any]:
    data = await get_all_tenants(current_user, status_filter=input_data.status)
    return api_response(Operation.RETRIEVED, Resource.TENANTS, data)


@tenant_router.post("/get_by_id")
async def get_tenant(
    input_data: TenantIdInput,
    current_user: dict = Depends(require_permission(["tenant:view"])),
) -> Dict[str, Any]:
    data = await get_tenant_by_id(input_data.id, current_user)
    return api_response(Operation.RETRIEVED, Resource.TENANT, data)


@tenant_router.post("/update")
async def update_tenant_endpoint(
    input_data: TenantUpdateInput,
    current_user: dict = Depends(require_permission(["tenant:edit"])),
) -> Dict[str, Any]:
    update_data = input_data.model_dump(exclude_unset=True, exclude={"id"})
    await update_tenant(input_data.id, update_data, current_user)
    return api_response(Operation.UPDATED, Resource.TENANT)
