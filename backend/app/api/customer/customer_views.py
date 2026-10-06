# -*- coding: utf-8 -*-
"""
Customer Portal API — REST endpoints cho app tài xế.

  GET /customer/dashboard-summary      — Trang chủ (lượt đang hoạt động, bãi gần, thống kê)
  GET /customer/nearby                 — Bãi trên bản đồ + bộ lọc
  GET /customer/garages/{id}/portal    — Chi tiết bãi
  GET /customer/bookings               — Lượt đặt của tôi
  GET /customer/bookings/{id}/tracking — Dòng thời gian lượt đặt
  GET/POST/PUT /customer/vehicles      — Quản lý xe
"""
import logging
from typing import Dict, Any, Optional, List

from fastapi import APIRouter, Depends, Query

from app.api.auth.dependencies import get_current_user
from app.api.shared.common_utils import api_response
from app.api.shared.schemas import Operation, Resource

from app.api.vehicle.vehicle_utils import get_user_vehicles, create_vehicle, update_vehicle
from app.api.vehicle.vehicle_schemas import VehicleCreateRequest
from app.api.garage.garage_utils import search_garages
from app.api.booking.booking_utils import list_bookings_for_user, get_booking
from app.api.customer.customer_utils import (
    get_dashboard_summary, get_garage_portal, get_booking_tracking,
)

logger = logging.getLogger(__name__)

customer_router = APIRouter(prefix="/customer", tags=["Customer Portal"])


@customer_router.get("/dashboard-summary")
async def dashboard_summary(
    lat: Optional[float] = Query(None, ge=-90, le=90),
    lng: Optional[float] = Query(None, ge=-180, le=180),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    data = await get_dashboard_summary(current_user, lat, lng)
    return api_response(Operation.RETRIEVED, "dashboard_summary", data=data)


@customer_router.get("/nearby")
async def nearby_garages(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(default=5, ge=0.2, le=50),
    lot_types: Optional[str] = Query(None, description="Danh sách lot_type, phân tách bởi dấu phẩy"),
    covered: bool = False,
    ev: bool = False,
    min_height_m: Optional[float] = Query(None, ge=1.5, le=5),
    guard_24h: bool = False,
    no_flood: bool = False,
    min_grade: int = Query(default=1, ge=1, le=5),
    max_hourly_price: Optional[int] = Query(None, ge=0),
    service_type: Optional[str] = None,
    only_available: bool = False,
    is_24h: bool = False,
    q: Optional[str] = Query(None, max_length=50),
) -> Dict[str, Any]:
    """Public — bãi quanh một điểm, kèm chỗ trống realtime và giá giờ."""
    garages = await search_garages(
        lat=lat, lng=lng, radius_km=radius_km,
        lot_types=[x for x in (lot_types or "").split(",") if x] or None,
        covered=covered, ev=ev, min_height_m=min_height_m, guard_24h=guard_24h,
        no_flood=no_flood, min_grade=min_grade, max_hourly_price=max_hourly_price,
        service_type=service_type, only_available=only_available, is_24h=is_24h, q=q,
    )
    return api_response(Operation.RETRIEVED, Resource.GARAGES, data={"garages": garages})


@customer_router.get("/garages/{garage_id}/portal")
async def garage_portal(garage_id: str) -> Dict[str, Any]:
    """Public — chi tiết bãi."""
    return api_response(Operation.RETRIEVED, Resource.GARAGE, data=await get_garage_portal(garage_id))


@customer_router.get("/bookings")
async def list_customer_bookings(
    status: Optional[str] = Query(None, description="Lọc trạng thái, nhiều giá trị phân tách bởi dấu phẩy"),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    data = await list_bookings_for_user(current_user, status.lower() if status else None)
    return api_response(Operation.RETRIEVED, Resource.BOOKINGS, data=data)


@customer_router.get("/bookings/{booking_id}")
async def get_customer_booking(
    booking_id: str,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    return api_response(Operation.RETRIEVED, Resource.BOOKING, data=await get_booking(booking_id, current_user))


@customer_router.get("/bookings/{booking_id}/tracking")
async def booking_tracking(
    booking_id: str,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    return api_response(Operation.RETRIEVED, Resource.BOOKING, data=await get_booking_tracking(booking_id, current_user))


# ─────────────────────────────────────────────────────────────────
# 5. Vehicle Management  (GET, POST, PUT /customer/vehicles/...)
# ─────────────────────────────────────────────────────────────────

@customer_router.get("/vehicles")
async def list_vehicles(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """List all vehicles for current user."""
    data = await get_user_vehicles(current_user)
    return api_response(Operation.RETRIEVED, Resource.VEHICLES, data=data)


@customer_router.post("/vehicles")
async def create_vehicle_endpoint(
    input_data: VehicleCreateRequest,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Create a new vehicle for the current user."""
    data = await create_vehicle(input_data.model_dump(), current_user)
    return api_response(Operation.CREATED, Resource.VEHICLE, data=data)


@customer_router.put("/vehicles/{vehicle_id}/default")
async def set_default_vehicle(
    vehicle_id: str,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Set a vehicle as the user's default vehicle."""
    await update_vehicle(vehicle_id, {"is_default": True}, current_user)
    return api_response(
        Operation.UPDATED, Resource.VEHICLE,
        message="Vehicle set as default successfully",
    )
