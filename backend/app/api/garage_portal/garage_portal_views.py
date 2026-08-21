# -*- coding: utf-8 -*-
"""
Garage Owner Portal — REST API endpoints.

Base URL: /api/v1/garage
Auth:     garage_owner | garage_manager | garage_staff roles (via cookie JWT)

All data is scoped to the authenticated user's garage (tenant_id → garage).
Super-admins must pass ?garage_id=<id> to specify the target garage.
"""
import logging
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel

from app.api.auth.permissions import require_permission
from app.api.booking.booking_utils import confirm_booking, complete_service, cancel_booking
from app.api.shared.common_utils import api_response
from app.api.shared.schemas import Operation, Resource
from app.api.garage_portal.garage_portal_utils import (
    get_garage_for_user,
    get_dashboard_overview,
    get_capacity_chart,
    get_queue,
    get_analytics,
    get_services_overview,
    get_score_data,
    create_portal_service,
    update_portal_service,
    delete_portal_service,
)

logger = logging.getLogger(__name__)

garage_portal_router = APIRouter(prefix="/garage-portal", tags=["Garage Owner Portal"])


# ─────────────────────────────────────────────────────────────────
# 1. Dashboard
# ─────────────────────────────────────────────────────────────────

@garage_portal_router.get("/dashboard/overview")
async def dashboard_overview(
    garage_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_permission(["garage:view"])),
) -> Dict[str, Any]:
    garage = await get_garage_for_user(current_user, garage_id)
    data = await get_dashboard_overview(garage)
    return api_response(Operation.RETRIEVED, "dashboard_overview", data=data)


@garage_portal_router.get("/dashboard/capacity")
async def dashboard_capacity(
    range: str = Query(default="24H", description="24H or 7D"),
    garage_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_permission(["garage:view"])),
) -> Dict[str, Any]:
    garage = await get_garage_for_user(current_user, garage_id)
    data = await get_capacity_chart(garage, range)
    return api_response(Operation.RETRIEVED, "capacity_chart", data=data)


# ─────────────────────────────────────────────────────────────────
# 2. Booking Queue
# ─────────────────────────────────────────────────────────────────

@garage_portal_router.get("/queue")
async def get_booking_queue(
    filter: str = Query(default="today", description="all | today | pending"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    garage_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_permission(["booking:view"])),
) -> Dict[str, Any]:
    garage = await get_garage_for_user(current_user, garage_id)
    data = await get_queue(garage, filter, page, limit)
    return api_response(Operation.RETRIEVED, "queue", data=data)


class BookingStatusUpdate(BaseModel):
    status: str  # confirmed | completed | cancelled


@garage_portal_router.patch("/queue/bookings/{booking_id}")
async def update_booking_status(
    booking_id: str,
    body: BookingStatusUpdate,
    current_user: dict = Depends(require_permission(["booking:edit"])),
) -> Dict[str, Any]:
    """
    Garage-side status update.
    Maps: confirmed → confirm_booking | completed → complete_service | cancelled → cancel_booking(garage)
    """
    status = body.status.lower()
    if status == "confirmed":
        result = await confirm_booking(booking_id, current_user)
    elif status == "completed":
        result = await complete_service(booking_id, current_user)
    elif status == "cancelled":
        result = await cancel_booking(booking_id, current_user, cancelled_by="garage")
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported status: '{status}'. Use: confirmed, completed, cancelled")

    return api_response(Operation.UPDATED, Resource.BOOKING, data=result)


# ─────────────────────────────────────────────────────────────────
# 3. Analytics
# ─────────────────────────────────────────────────────────────────

@garage_portal_router.get("/analytics")
async def get_analytics_dashboard(
    range: str = Query(default="30D", description="7D | 30D | 90D | 1Y"),
    garage_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_permission(["analytics:view"])),
) -> Dict[str, Any]:
    garage = await get_garage_for_user(current_user, garage_id)
    data = await get_analytics(garage, range)
    return api_response(Operation.RETRIEVED, "analytics", data=data)


# ─────────────────────────────────────────────────────────────────
# 4. Service Management
# ─────────────────────────────────────────────────────────────────

@garage_portal_router.get("/services")
async def list_services(
    garage_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_permission(["service:view"])),
) -> Dict[str, Any]:
    garage = await get_garage_for_user(current_user, garage_id)
    data = await get_services_overview(garage)
    return api_response(Operation.RETRIEVED, Resource.SERVICES, data=data)


class ServiceCreateRequest(BaseModel):
    service_type_code: str
    price: int          # price in local currency (VND)
    duration_minutes: Optional[int] = None


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
    )
    return api_response(Operation.CREATED, Resource.SERVICE, data=data)


class ServiceUpdateRequest(BaseModel):
    price: Optional[int] = None
    duration_minutes: Optional[int] = None


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
    )
    return api_response(Operation.UPDATED, Resource.SERVICE, data=data)


@garage_portal_router.delete("/services/{service_id}")
async def delete_service(
    service_id: str,
    current_user: dict = Depends(require_permission(["service:edit"])),
) -> Dict[str, Any]:
    await delete_portal_service(service_id=service_id, current_user=current_user)
    return api_response(Operation.DELETED, Resource.SERVICE, message="Service removed successfully")


# ─────────────────────────────────────────────────────────────────
# 5. Match Score
# ─────────────────────────────────────────────────────────────────

@garage_portal_router.get("/score")
async def get_score(
    garage_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_permission(["garage:view"])),
) -> Dict[str, Any]:
    garage = await get_garage_for_user(current_user, garage_id)
    data = get_score_data(garage)
    return api_response(Operation.RETRIEVED, "match_score", data=data)
