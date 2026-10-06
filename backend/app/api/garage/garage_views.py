# -*- coding: utf-8 -*-
"""Garage Views — API hồ sơ bãi đỗ."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any

from app.api.garage.garage_utils import (
    get_all_garages, get_garage_by_id, search_garages, update_garage,
)
from app.api.garage.garage_schemas import GarageProfileUpdate, GarageSearchRequest
from app.api.garage.garage_classification_utils import (
    LOT_TYPES, INTEGRATION_LEVELS, GRADE_CHECKLIST, GRADE_GROUPS,
)
from app.api.auth.permissions import require_permission
from app.api.shared.common_utils import api_response
from app.api.shared.schemas import Operation, Resource

garage_router = APIRouter(prefix="/garage", tags=["Garage Management"])


class GarageFilterInput(BaseModel):
    status: str = "active"


class GarageIdInput(BaseModel):
    id: str = Field(..., min_length=1)


class GarageUpdateInput(GarageProfileUpdate):
    id: str = Field(..., min_length=1)


@garage_router.get("/taxonomy")
async def taxonomy() -> Dict[str, Any]:
    """Public — danh mục loại hình, cấp tích hợp, checklist kiểm định (dùng cho FE)."""
    data = {
        "lot_types": [{"code": k, "label": v} for k, v in LOT_TYPES.items()],
        "integration_levels": [{"level": k, **v} for k, v in INTEGRATION_LEVELS.items()],
        "grade_checklist": GRADE_CHECKLIST,
        "grade_groups": GRADE_GROUPS,
    }
    return api_response(Operation.RETRIEVED, Resource.GARAGES, data)


@garage_router.post("/get_all")
async def get_garages(
    input_data: GarageFilterInput = GarageFilterInput(),
    current_user: dict = Depends(require_permission(["garage:view"])),
) -> Dict[str, Any]:
    data = await get_all_garages(current_user=current_user, status_filter=input_data.status)
    return api_response(Operation.RETRIEVED, Resource.GARAGES, data)


@garage_router.post("/search_nearby")
async def search_nearby(input_data: GarageSearchRequest) -> Dict[str, Any]:
    """Tìm bãi gần vị trí kèm bộ lọc — PUBLIC."""
    data = await search_garages(
        lat=input_data.latitude, lng=input_data.longitude, radius_km=input_data.max_distance_km,
        lot_types=input_data.lot_types, covered=input_data.covered, ev=input_data.ev,
        min_height_m=input_data.min_height_m, guard_24h=input_data.guard_24h,
        no_flood=input_data.no_flood, min_grade=input_data.min_grade,
        max_hourly_price=input_data.max_hourly_price, service_type=input_data.service_type,
        only_available=input_data.only_available,
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
    data = await update_garage(input_data.id, update_data, current_user)
    return api_response(Operation.UPDATED, Resource.GARAGE, data)
