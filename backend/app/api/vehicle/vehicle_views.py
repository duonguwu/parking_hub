# -*- coding: utf-8 -*-
"""Vehicle Views — POST-based API endpoints for vehicle management."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from app.api.vehicle.vehicle_schemas import VehicleCreateRequest, VehicleUpdateRequest
from app.api.vehicle.vehicle_utils import (
    get_user_vehicles,
    get_vehicle_by_id,
    create_vehicle,
    update_vehicle,
    delete_vehicle,
)
from app.api.auth.dependencies import get_current_user
from app.api.shared.common_utils import api_response
from app.api.shared.schemas import Operation, Resource

vehicle_router = APIRouter(prefix="/vehicle", tags=["Vehicle Management"])


class VehicleIdInput(BaseModel):
    id: str = Field(..., min_length=1)


class VehicleUpdateInput(VehicleUpdateRequest):
    id: str = Field(..., min_length=1)


@vehicle_router.post("/get_all")
async def get_vehicles(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    data = await get_user_vehicles(current_user)
    return api_response(Operation.RETRIEVED, Resource.VEHICLES, data)


@vehicle_router.post("/get_by_id")
async def get_vehicle(
    input_data: VehicleIdInput,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    data = await get_vehicle_by_id(input_data.id, current_user)
    return api_response(Operation.RETRIEVED, Resource.VEHICLE, data)


@vehicle_router.post("/create")
async def create_vehicle_endpoint(
    input_data: VehicleCreateRequest,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    data = await create_vehicle(input_data.model_dump(), current_user)
    return api_response(Operation.CREATED, Resource.VEHICLE, data)


@vehicle_router.post("/update")
async def update_vehicle_endpoint(
    input_data: VehicleUpdateInput,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    update_data = input_data.model_dump(exclude_unset=True, exclude={"id"})
    await update_vehicle(input_data.id, update_data, current_user)
    return api_response(Operation.UPDATED, Resource.VEHICLE)


@vehicle_router.post("/delete")
async def delete_vehicle_endpoint(
    input_data: VehicleIdInput,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    await delete_vehicle(input_data.id, current_user)
    return api_response(Operation.DELETED, Resource.VEHICLE)
