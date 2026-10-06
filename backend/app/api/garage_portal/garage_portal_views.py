# -*- coding: utf-8 -*-
"""
Garage Owner Portal — REST API cho chủ bãi.

Auth:  garage_owner | garage_manager | garage_staff (cookie JWT)
Dữ liệu giới hạn trong bãi của tenant. super_admin truyền ?garage_id=<id>.
"""
import logging
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.api.auth.permissions import require_permission
from app.api.booking.booking_utils import (
    confirm_booking, reject_booking, checkin_booking, checkout_booking,
    mark_no_show, mark_paid, cancel_booking, create_walk_in,
)
from app.api.capacity.capacity_utils import set_occupied
from app.api.garage.garage_schemas import GarageProfileUpdate
from app.api.garage.garage_utils import get_garage_detail, update_garage_profile
from app.api.shared.common_utils import api_response
from app.api.shared.schemas import Operation, Resource
from app.api.garage_portal.garage_portal_utils import (
    get_garage_for_user,
    list_accessible_garages,
    get_dashboard_overview,
    get_capacity_chart,
    get_portal_bookings,
    get_analytics,
    get_services_overview,
    get_score_data,
    create_portal_service,
    update_portal_service,
    delete_portal_service,
)

logger = logging.getLogger(__name__)

garage_portal_router = APIRouter(prefix="/garage-portal", tags=["Garage Owner Portal"])


# ── 1. Hồ sơ bãi ─────────────────────────────────────────────────

@garage_portal_router.get("/garages")
async def my_garages(
    q: Optional[str] = Query(None),
    current_user: dict = Depends(require_permission(["garage:view"])),
) -> Dict[str, Any]:
    """Các bãi user được thao tác (chủ có thể có nhiều bãi; super_admin thấy toàn mạng lưới)."""
    return api_response(Operation.RETRIEVED, Resource.GARAGE, data=await list_accessible_garages(current_user, q))


@garage_portal_router.get("/garage")
async def my_garage(
    garage_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_permission(["garage:view"])),
) -> Dict[str, Any]:
    garage = await get_garage_for_user(current_user, garage_id)
    return api_response(Operation.RETRIEVED, Resource.GARAGE, data=await get_garage_detail(str(garage["_id"])))


@garage_portal_router.put("/garage")
async def update_my_garage(
    body: GarageProfileUpdate,
    garage_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_permission(["garage:edit"])),
) -> Dict[str, Any]:
    garage = await get_garage_for_user(current_user, garage_id)
    data = await update_garage_profile(garage, body.model_dump(exclude_unset=True), current_user)
    return api_response(Operation.UPDATED, Resource.GARAGE, data=data)


# ── 2. Tổng quan & chỗ trống ─────────────────────────────────────

@garage_portal_router.get("/dashboard/overview")
async def dashboard_overview(
    garage_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_permission(["garage:view"])),
) -> Dict[str, Any]:
    garage = await get_garage_for_user(current_user, garage_id)
    return api_response(Operation.RETRIEVED, "dashboard_overview", data=await get_dashboard_overview(garage))


@garage_portal_router.get("/dashboard/capacity")
async def dashboard_capacity(
    range: str = Query(default="24H", description="24H or 7D"),
    garage_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_permission(["garage:view"])),
) -> Dict[str, Any]:
    garage = await get_garage_for_user(current_user, garage_id)
    return api_response(Operation.RETRIEVED, "capacity_chart", data=await get_capacity_chart(garage, range))


class OccupancyBody(BaseModel):
    occupied: int = Field(..., ge=0)


@garage_portal_router.put("/occupancy")
async def update_occupancy(
    body: OccupancyBody,
    garage_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_permission(["capacity:edit"])),
) -> Dict[str, Any]:
    garage = await get_garage_for_user(current_user, garage_id)
    data = await set_occupied(garage["_id"], body.occupied, current_user)
    return api_response(Operation.UPDATED, Resource.GARAGE_CAPACITY, data=data)


# ── 3. Lượt đặt & vào/ra ─────────────────────────────────────────

@garage_portal_router.get("/bookings")
async def list_bookings(
    tab: str = Query(default="upcoming", description="upcoming | pending | inside | history"),
    q: Optional[str] = Query(None, description="Biển số hoặc mã lượt"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    garage_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_permission(["booking:view"])),
) -> Dict[str, Any]:
    garage = await get_garage_for_user(current_user, garage_id)
    return api_response(Operation.RETRIEVED, Resource.BOOKINGS, data=await get_portal_bookings(garage, tab, q, page, limit))


class BookingActionBody(BaseModel):
    action: str = Field(..., pattern="^(confirm|reject|checkin|checkout|no_show|cancel|paid)$")
    reason: str = Field(default="", max_length=300)
    license_plate: Optional[str] = Field(None, max_length=20)
    payment_method: Optional[str] = Field(None, pattern="^(cash|transfer)$")


@garage_portal_router.post("/bookings/{booking_id}/actions")
async def booking_action(
    booking_id: str,
    body: BookingActionBody,
    current_user: dict = Depends(require_permission(["booking:edit"])),
) -> Dict[str, Any]:
    a = body.action
    if a == "confirm":
        result = await confirm_booking(booking_id, current_user)
    elif a == "reject":
        result = await reject_booking(booking_id, current_user, body.reason)
    elif a == "checkin":
        result = await checkin_booking(booking_id, current_user, body.license_plate)
    elif a == "checkout":
        result = await checkout_booking(booking_id, current_user, body.payment_method)
    elif a == "no_show":
        result = await mark_no_show(booking_id, current_user)
    elif a == "paid":
        result = await mark_paid(booking_id, current_user, body.payment_method or "cash")
    else:
        result = await cancel_booking(booking_id, current_user, body.reason)
    return api_response(Operation.UPDATED, Resource.BOOKING, data=result)


class WalkInBody(BaseModel):
    license_plate: str = Field(..., min_length=4, max_length=20)
    service_type_code: str = Field(default="park_hourly")


@garage_portal_router.post("/walk-ins")
async def walk_in(
    body: WalkInBody,
    garage_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_permission(["booking:edit"])),
) -> Dict[str, Any]:
    garage = await get_garage_for_user(current_user, garage_id)
    data = await create_walk_in(garage, body.license_plate, body.service_type_code, current_user)
    return api_response(Operation.CREATED, Resource.BOOKING, data=data)


# ── 4. Phân tích ─────────────────────────────────────────────────

@garage_portal_router.get("/analytics")
async def get_analytics_dashboard(
    range: str = Query(default="30D", description="7D | 30D | 90D"),
    garage_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_permission(["analytics:view"])),
) -> Dict[str, Any]:
    garage = await get_garage_for_user(current_user, garage_id)
    return api_response(Operation.RETRIEVED, "analytics", data=await get_analytics(garage, range))


# ── 5. Dịch vụ & bảng giá ────────────────────────────────────────

@garage_portal_router.get("/services")
async def list_services(
    garage_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_permission(["service:view"])),
) -> Dict[str, Any]:
    garage = await get_garage_for_user(current_user, garage_id)
    return api_response(Operation.RETRIEVED, Resource.GARAGE_SERVICES, data=await get_services_overview(garage))


class ServiceCreateRequest(BaseModel):
    service_type_code: str
    price: Optional[int] = None          # VND — giá chính; bỏ trống thì dùng bảng giá mẫu
    duration_minutes: Optional[int] = None
    pricing: Optional[Dict[str, Any]] = None
    note: Optional[str] = None


@garage_portal_router.post("/services")
async def create_service(
    body: ServiceCreateRequest,
    garage_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_permission(["service:create"])),
) -> Dict[str, Any]:
    garage = await get_garage_for_user(current_user, garage_id)
    data = await create_portal_service(
        garage=garage,
        service_type_code=body.service_type_code,
        price=body.price,
        duration_minutes=body.duration_minutes,
        current_user=current_user,
        pricing=body.pricing,
        note=body.note,
    )
    return api_response(Operation.CREATED, Resource.GARAGE_SERVICE, data=data)


class ServiceUpdateRequest(BaseModel):
    price: Optional[int] = None
    duration_minutes: Optional[int] = None
    pricing: Optional[Dict[str, Any]] = None
    note: Optional[str] = None


@garage_portal_router.put("/services/{service_id}")
async def update_service(
    service_id: str,
    body: ServiceUpdateRequest,
    current_user: dict = Depends(require_permission(["service:edit"])),
) -> Dict[str, Any]:
    data = await update_portal_service(
        service_id=service_id,
        price=body.price,
        duration_minutes=body.duration_minutes,
        current_user=current_user,
        pricing=body.pricing,
        note=body.note,
    )
    return api_response(Operation.UPDATED, Resource.GARAGE_SERVICE, data=data)


@garage_portal_router.delete("/services/{service_id}")
async def delete_service(
    service_id: str,
    current_user: dict = Depends(require_permission(["service:edit"])),
) -> Dict[str, Any]:
    await delete_portal_service(service_id=service_id, current_user=current_user)
    return api_response(Operation.DELETED, Resource.GARAGE_SERVICE, message="Service removed successfully")


# ── 6. Chất lượng ────────────────────────────────────────────────

@garage_portal_router.get("/score")
async def get_score(
    garage_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_permission(["garage:view"])),
) -> Dict[str, Any]:
    garage = await get_garage_for_user(current_user, garage_id)
    return api_response(Operation.RETRIEVED, "quality_score", data=get_score_data(garage))
