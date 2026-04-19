# -*- coding: utf-8 -*-
"""Service Type Views — PUBLIC catalog (no auth)."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any

from app.api.service_type.service_type_utils import (
    get_all_service_types, get_service_type_by_code,
)
from app.api.shared.common_utils import api_response
from app.api.shared.schemas import Operation, Resource

service_type_router = APIRouter(prefix="/service-types", tags=["Service Types"])


class ServiceTypeFilter(BaseModel):
    active_only: bool = True


class ServiceTypeCodeInput(BaseModel):
    code: str


@service_type_router.post("/get_all")
async def list_service_types(
    input_data: ServiceTypeFilter = ServiceTypeFilter(),
) -> Dict[str, Any]:
    data = await get_all_service_types(active_only=input_data.active_only)
    return api_response(Operation.RETRIEVED, Resource.SERVICE_TYPE, data)


@service_type_router.post("/get_by_code")
async def get_service_type(input_data: ServiceTypeCodeInput) -> Dict[str, Any]:
    data = await get_service_type_by_code(input_data.code)
    if not data:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Service type not found")
    return api_response(Operation.RETRIEVED, Resource.SERVICE_TYPE, data)
