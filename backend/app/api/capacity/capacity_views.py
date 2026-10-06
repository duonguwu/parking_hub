# -*- coding: utf-8 -*-
"""Capacity Views."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, List

from app.api.capacity.capacity_utils import set_occupied, get_current_and_predicted
from app.api.auth.permissions import require_permission
from app.api.shared.common_utils import api_response
from app.api.shared.schemas import Operation, Resource

capacity_router = APIRouter(prefix="/capacity", tags=["Capacity"])


class CapacityByGarageInput(BaseModel):
    garage_id: str = Field(..., min_length=1)
    horizons_min: List[int] = [30, 60, 120]


class OccupancyUpdateInput(BaseModel):
    garage_id: str = Field(..., min_length=1)
    occupied: int = Field(..., ge=0)


@capacity_router.post("/current_and_predicted")
async def current_and_predicted(input_data: CapacityByGarageInput) -> Dict[str, Any]:
    """Public — chỗ trống hiện tại + dự đoán ở các mốc."""
    data = await get_current_and_predicted(input_data.garage_id, input_data.horizons_min)
    return api_response(Operation.RETRIEVED, Resource.GARAGE_CAPACITY, data)


@capacity_router.post("/update_occupancy")
async def update_occupancy(
    input_data: OccupancyUpdateInput,
    current_user: dict = Depends(require_permission(["capacity:edit"])),
) -> Dict[str, Any]:
    data = await set_occupied(input_data.garage_id, input_data.occupied, current_user)
    return api_response(Operation.UPDATED, Resource.GARAGE_CAPACITY, data)
