# -*- coding: utf-8 -*-
"""
Admin — REST API quản trị mạng lưới.

Auth: super_admin | platform_ops. Đọc cần `system:view`, ghi cần `system:config`.
"""
import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.api.admin.admin_utils import (
    get_overview, list_garages, network_map, get_garage_admin, update_garage_admin, save_assessment,
    list_users, set_user_active, list_service_types_admin, create_service_type, update_service_type,
)
from app.api.auth.permissions import require_permission
from app.api.garage.garage_classification_utils import GRADE_CHECKLIST, GRADE_GROUPS, INTEGRATION_LEVELS, LOT_TYPES
from app.api.shared.common_utils import api_response
from app.api.shared.schemas import Operation, Resource

logger = logging.getLogger(__name__)

admin_router = APIRouter(prefix="/admin", tags=["Admin"])

VIEW = Depends(require_permission(["system:view"]))
CONFIG = Depends(require_permission(["system:config"]))


# ── Tổng quan & danh mục tham chiếu ──────────────────────────────

@admin_router.get("/overview")
async def overview(current_user: dict = VIEW) -> Dict[str, Any]:
    return api_response(Operation.RETRIEVED, "network_overview", data=await get_overview())


@admin_router.get("/meta")
async def meta(current_user: dict = VIEW) -> Dict[str, Any]:
    """Danh mục dùng cho form: loại bãi, cấp tích hợp, checklist kiểm định."""
    return api_response(Operation.RETRIEVED, "admin_meta", data={
        "lot_types": [{"code": k, "label": v} for k, v in LOT_TYPES.items()],
        "integration_levels": [{"level": k, **v} for k, v in INTEGRATION_LEVELS.items()],
        "grade_groups": [{"key": k, "label": v} for k, v in GRADE_GROUPS.items()],
        "grade_checklist": GRADE_CHECKLIST,
    })


# ── Bãi đỗ ───────────────────────────────────────────────────────

@admin_router.get("/garages")
async def garages(
    status: Optional[str] = Query(None),
    level: Optional[int] = Query(None, ge=1, le=4),
    lot_type: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = VIEW,
) -> Dict[str, Any]:
    data = await list_garages(status, level, lot_type, district, q, page, limit)
    return api_response(Operation.RETRIEVED, Resource.GARAGES, data=data)


@admin_router.get("/map")
async def garages_map(
    status: Optional[str] = Query(None),
    level: Optional[int] = Query(None, ge=1, le=4),
    current_user: dict = VIEW,
) -> Dict[str, Any]:
    return api_response(Operation.RETRIEVED, Resource.GARAGES, data=await network_map(status, level))


@admin_router.get("/garages/{garage_id}")
async def garage_detail(garage_id: str, current_user: dict = VIEW) -> Dict[str, Any]:
    return api_response(Operation.RETRIEVED, Resource.GARAGE, data=await get_garage_admin(garage_id))


class GarageAdminUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(pending_review|active|suspended)$")
    integration_level: Optional[int] = Field(None, ge=1, le=4)
    is_verified: Optional[bool] = None
    is_accepting_bookings: Optional[bool] = None


@admin_router.patch("/garages/{garage_id}")
async def garage_update(garage_id: str, body: GarageAdminUpdate, current_user: dict = CONFIG) -> Dict[str, Any]:
    data = await update_garage_admin(garage_id, body.model_dump(exclude_none=True), current_user)
    return api_response(Operation.UPDATED, Resource.GARAGE, data=data)


class AssessmentBody(BaseModel):
    items: Dict[str, Any] = Field(default_factory=dict)
    note: str = Field(default="", max_length=1000)


@admin_router.put("/garages/{garage_id}/assessment")
async def garage_assessment(garage_id: str, body: AssessmentBody, current_user: dict = CONFIG) -> Dict[str, Any]:
    data = await save_assessment(garage_id, body.items, body.note, current_user)
    return api_response(Operation.UPDATED, Resource.GARAGE, data=data)


# ── Người dùng ───────────────────────────────────────────────────

@admin_router.get("/users")
async def users(
    role: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = VIEW,
) -> Dict[str, Any]:
    return api_response(Operation.RETRIEVED, Resource.USERS, data=await list_users(role, q, page, limit))


class UserActiveBody(BaseModel):
    is_active: bool


@admin_router.patch("/users/{user_id}")
async def user_update(user_id: str, body: UserActiveBody, current_user: dict = CONFIG) -> Dict[str, Any]:
    return api_response(Operation.UPDATED, Resource.USER, data=await set_user_active(user_id, body.is_active, current_user))


# ── Danh mục dịch vụ ─────────────────────────────────────────────

@admin_router.get("/service-types")
async def service_types(current_user: dict = VIEW) -> Dict[str, Any]:
    return api_response(Operation.RETRIEVED, Resource.SERVICE_TYPES, data=await list_service_types_admin())


class ServiceTypeBody(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    icon: Optional[str] = None
    base_price_min: Optional[int] = Field(None, ge=0)
    base_price_max: Optional[int] = Field(None, ge=0)
    estimated_duration_minutes: Optional[int] = Field(None, ge=0)
    default_pricing: Optional[Dict[str, Any]] = None
    is_popular: Optional[bool] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


@admin_router.post("/service-types")
async def service_type_create(body: ServiceTypeBody, current_user: dict = CONFIG) -> Dict[str, Any]:
    data = await create_service_type(body.model_dump(exclude_none=True), current_user)
    return api_response(Operation.CREATED, Resource.SERVICE_TYPE, data=data)


@admin_router.patch("/service-types/{code}")
async def service_type_update(code: str, body: ServiceTypeBody, current_user: dict = CONFIG) -> Dict[str, Any]:
    payload = body.model_dump(exclude_none=True)
    payload.pop("code", None)
    data = await update_service_type(code, payload, current_user)
    return api_response(Operation.UPDATED, Resource.SERVICE_TYPE, data=data)
