# -*- coding: utf-8 -*-
"""Garage Views — API endpoints for garage management."""
from fastapi import APIRouter, Depends, Query
from typing import Dict, Any, Optional

from app.api.garage.garage_schemas import (
    GarageUpdateRequest,
    GarageCapacityUpdateRequest,
)
from app.api.garage.garage_utils import (
    get_all_garages,
    get_garage_by_id,
    search_garages_nearby,
    update_garage,
    update_garage_capacity,
)
from app.api.auth.dependencies import get_current_user
from app.api.auth.permissions import has_permission
from app.api.shared.common_utils import api_response
from app.api.shared.schemas import Operation, Resource

garage_router = APIRouter(tags=["Garage Management"])


@garage_router.get("/garages")
@has_permission(["garage:view"])
async def get_garages(
    status: str = Query(default="active"),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Lấy danh sách garages (theo tenant hoặc toàn bộ nếu customer/admin)."""
    data = await get_all_garages(current_user=current_user, status_filter=status)
    return api_response(Operation.RETRIEVED, Resource.GARAGES, data)


@garage_router.get("/garages/nearby")
async def search_nearby(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(default=10, ge=1, le=50),
    min_tier: int = Query(default=1, ge=1, le=4),
    service: Optional[str] = Query(default=None),
) -> Dict[str, Any]:
    """Tìm garages gần vị trí — PUBLIC, dùng cho matching."""
    data = await search_garages_nearby(
        latitude=lat, longitude=lng,
        max_distance_km=radius_km, min_tier=min_tier,
        service_type=service,
    )
    return api_response(Operation.RETRIEVED, Resource.GARAGES, data)


@garage_router.get("/garages/{garage_id}")
@has_permission(["garage:view"])
async def get_garage(
    garage_id: str,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Lấy chi tiết garage."""
    data = await get_garage_by_id(garage_id, current_user)
    return api_response(Operation.RETRIEVED, Resource.GARAGE, data)


@garage_router.put("/garages/{garage_id}")
@has_permission(["garage:edit"])
async def update_garage_endpoint(
    garage_id: str,
    request: GarageUpdateRequest,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Cập nhật thông tin garage."""
    await update_garage(garage_id, request.model_dump(exclude_unset=True), current_user)
    return api_response(Operation.UPDATED, Resource.GARAGE)


@garage_router.put("/garages/{garage_id}/capacity")
@has_permission(["capacity:edit"])
async def update_capacity_endpoint(
    garage_id: str,
    request: GarageCapacityUpdateRequest,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Cập nhật real-time capacity (dùng bởi staff)."""
    await update_garage_capacity(garage_id, request.model_dump(), current_user)
    return api_response(Operation.UPDATED, Resource.GARAGE_CAPACITY)
