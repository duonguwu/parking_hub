# -*- coding: utf-8 -*-
"""Garage Views — POST-based API endpoints for garage management."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

from app.api.garage.garage_utils import (
    get_all_garages,
    get_garage_by_id,
    search_garages_nearby,
    update_garage,
    update_garage_capacity,
)
from app.api.auth.permissions import require_permission
from app.api.shared.common_utils import api_response
from app.api.shared.schemas import Operation, Resource

garage_router = APIRouter(prefix="/garage", tags=["Garage Management"])


class GarageFilterInput(BaseModel):
    status: str = "active"


class GarageIdInput(BaseModel):
    id: str = Field(..., min_length=1)


class GarageUpdateInput(BaseModel):
    id: str = Field(..., min_length=1)
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    services_offered: Optional[List[str]] = None
    vehicle_types_accepted: Optional[List[str]] = None
    amenities: Optional[List[str]] = None
    is_accepting_bookings: Optional[bool] = None
    operating_hours: Optional[Dict[str, Any]] = None


class GarageCapacityInput(BaseModel):
    id: str = Field(..., min_length=1)
    vehicles_in_service: int = Field(..., ge=0)
    vehicles_waiting: int = Field(..., ge=0)
    estimated_wait_minutes: int = Field(default=0, ge=0)


class GarageSearchInput(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    max_distance_km: float = Field(default=10, ge=1, le=50)
    min_tier: int = Field(default=1, ge=1, le=4)
    service_type: Optional[str] = None


@garage_router.post("/get_all")
async def get_garages(
    input_data: GarageFilterInput = GarageFilterInput(),
    current_user: dict = Depends(require_permission(["garage:view"])),
) -> Dict[str, Any]:
    data = await get_all_garages(current_user=current_user, status_filter=input_data.status)
    return api_response(Operation.RETRIEVED, Resource.GARAGES, data)


@garage_router.post("/search_nearby")
async def search_nearby(
    input_data: GarageSearchInput,
) -> Dict[str, Any]:
    """Tìm garages gần vị trí — PUBLIC."""
    data = await search_garages_nearby(
        latitude=input_data.latitude, longitude=input_data.longitude,
        max_distance_km=input_data.max_distance_km, min_tier=input_data.min_tier,
        service_type=input_data.service_type,
    )
    return api_response(Operation.RETRIEVED, Resource.GARAGES, data)


@garage_router.post("/get_by_id")
async def get_garage(
    input_data: GarageIdInput,
    current_user: dict = Depends(require_permission(["garage:view"])),
) -> Dict[str, Any]:
    data = await get_garage_by_id(input_data.id, current_user)
    return api_response(Operation.RETRIEVED, Resource.GARAGE, data)


@garage_router.post("/update")
async def update_garage_endpoint(
    input_data: GarageUpdateInput,
    current_user: dict = Depends(require_permission(["garage:edit"])),
) -> Dict[str, Any]:
    update_data = input_data.model_dump(exclude_unset=True, exclude={"id"})
    await update_garage(input_data.id, update_data, current_user)
    return api_response(Operation.UPDATED, Resource.GARAGE)


@garage_router.post("/update_capacity")
async def update_capacity_endpoint(
    input_data: GarageCapacityInput,
    current_user: dict = Depends(require_permission(["capacity:edit"])),
) -> Dict[str, Any]:
    capacity_data = input_data.model_dump(exclude={"id"})
    await update_garage_capacity(input_data.id, capacity_data, current_user)
    return api_response(Operation.UPDATED, Resource.GARAGE_CAPACITY)
