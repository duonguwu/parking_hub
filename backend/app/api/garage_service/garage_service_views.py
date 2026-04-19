# -*- coding: utf-8 -*-
"""Garage Service Views."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from app.api.garage_service.garage_service_utils import (
    list_services_for_garage, upsert_garage_service, remove_garage_service,
)
from app.api.auth.permissions import require_permission
from app.api.shared.common_utils import api_response
from app.api.shared.schemas import Operation, Resource

garage_service_router = APIRouter(prefix="/garage-services", tags=["Garage Services"])


class ListByGarageInput(BaseModel):
    garage_id: str = Field(..., min_length=1)


class UpsertInput(BaseModel):
    garage_id: str = Field(..., min_length=1)
    service_type_code: str = Field(..., min_length=1)
    price: int = Field(..., ge=0)
    estimated_duration_minutes: Optional[int] = Field(default=None, ge=1, le=600)


class RemoveInput(BaseModel):
    garage_id: str = Field(..., min_length=1)
    service_type_code: str = Field(..., min_length=1)


@garage_service_router.post("/list_by_garage")
async def list_by_garage(input_data: ListByGarageInput) -> Dict[str, Any]:
    """Public — list active services at a garage."""
    data = await list_services_for_garage(input_data.garage_id)
    return api_response(Operation.RETRIEVED, Resource.GARAGE_SERVICES, data)


@garage_service_router.post("/upsert")
async def upsert(
    input_data: UpsertInput,
    current_user: dict = Depends(require_permission(["service:create", "service:edit"])),
) -> Dict[str, Any]:
    data = await upsert_garage_service(
        input_data.garage_id, input_data.service_type_code,
        input_data.price, input_data.estimated_duration_minutes,
        current_user,
    )
    return api_response(Operation.UPDATED, Resource.GARAGE_SERVICE, data)


@garage_service_router.post("/remove")
async def remove(
    input_data: RemoveInput,
    current_user: dict = Depends(require_permission(["service:delete", "service:edit"])),
) -> Dict[str, Any]:
    await remove_garage_service(
        input_data.garage_id, input_data.service_type_code, current_user,
    )
    return api_response(Operation.DELETED, Resource.GARAGE_SERVICE)
