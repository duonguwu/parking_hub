# -*- coding: utf-8 -*-
"""Capacity Views."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, List

from app.api.capacity.capacity_utils import (
    manual_update_load, get_current_and_predicted,
)
from app.api.auth.permissions import require_permission
from app.api.shared.common_utils import api_response
from app.api.shared.schemas import Operation, Resource

capacity_router = APIRouter(prefix="/capacity", tags=["Capacity"])


class CapacityByGarageInput(BaseModel):
    garage_id: str = Field(..., min_length=1)
    horizons_min: List[int] = [15, 30, 60]


class CapacityUpdateInput(BaseModel):
    garage_id: str = Field(..., min_length=1)
    vehicles_in_service: int = Field(..., ge=0)
    vehicles_waiting: int = Field(..., ge=0)


@capacity_router.post("/current_and_predicted")
async def current_and_predicted(input_data: CapacityByGarageInput) -> Dict[str, Any]:
    """Public — current load + predictions for upcoming horizons."""
    data = await get_current_and_predicted(input_data.garage_id, input_data.horizons_min)
    return api_response(Operation.RETRIEVED, Resource.GARAGE_CAPACITY, data)


@capacity_router.post("/update_load")
async def update_load(
    input_data: CapacityUpdateInput,
    current_user: dict = Depends(require_permission(["capacity:edit"])),
) -> Dict[str, Any]:
    await manual_update_load(
        input_data.garage_id,
        input_data.vehicles_in_service,
        input_data.vehicles_waiting,
        current_user,
    )
    return api_response(Operation.UPDATED, Resource.GARAGE_CAPACITY)
