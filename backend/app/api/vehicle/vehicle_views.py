# -*- coding: utf-8 -*-
"""Vehicle Views — API endpoints for vehicle management."""
from fastapi import APIRouter, Depends
from typing import Dict, Any

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

vehicle_router = APIRouter(tags=["Vehicle Management"])


@vehicle_router.get("/vehicles")
async def get_vehicles(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Lấy danh sách xe của user hiện tại."""
    data = await get_user_vehicles(current_user)
    return api_response(Operation.RETRIEVED, Resource.VEHICLES, data)


@vehicle_router.get("/vehicles/{vehicle_id}")
async def get_vehicle(
    vehicle_id: str,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Lấy chi tiết xe."""
    data = await get_vehicle_by_id(vehicle_id, current_user)
    return api_response(Operation.RETRIEVED, Resource.VEHICLE, data)


@vehicle_router.post("/vehicles")
async def create_vehicle_endpoint(
    request: VehicleCreateRequest,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Thêm xe mới."""
    data = await create_vehicle(request.model_dump(), current_user)
    return api_response(Operation.CREATED, Resource.VEHICLE, data)


@vehicle_router.put("/vehicles/{vehicle_id}")
async def update_vehicle_endpoint(
    vehicle_id: str,
    request: VehicleUpdateRequest,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Cập nhật thông tin xe."""
    await update_vehicle(vehicle_id, request.model_dump(exclude_unset=True), current_user)
    return api_response(Operation.UPDATED, Resource.VEHICLE)


@vehicle_router.delete("/vehicles/{vehicle_id}")
async def delete_vehicle_endpoint(
    vehicle_id: str,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Xóa xe (soft delete)."""
    await delete_vehicle(vehicle_id, current_user)
    return api_response(Operation.DELETED, Resource.VEHICLE)
