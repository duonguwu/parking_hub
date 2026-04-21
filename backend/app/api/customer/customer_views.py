# -*- coding: utf-8 -*-
"""
Customer Portal API — RESTful endpoints tailored for the Customer FE.

Provides aggregated & FE-friendly endpoints:
  GET /customer/dashboard-summary   — Home page data (vehicle + recommendations + active booking)
  GET /customer/nearby              — Nearby garages for Map page
  GET /customer/garages/{id}/portal — Aggregated Garage Detail page
  GET /customer/bookings            — Booking list (filterable)
  GET /customer/bookings/{id}/tracking — Booking timeline
  GET /customer/vehicles            — User vehicles list
  POST /customer/vehicles           — Create vehicle
  PUT /customer/vehicles/{id}/default — Set default vehicle
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException

from app.api.auth.dependencies import get_current_user, get_current_user_optional
from app.api.shared.common_utils import api_response
from app.api.shared.schemas import Operation, Resource
from app.api.shared.tool.convert_object_id import convert_mongo_object_id
from app.api.shared.tool.datetime_convert import get_current_time

# Reuse ALL existing business logic — zero duplication
from app.api.vehicle.vehicle_utils import (
    get_user_vehicles, create_vehicle, update_vehicle, format_vehicle,
)
from app.api.vehicle.vehicle_models import VehicleModel
from app.api.vehicle.vehicle_schemas import VehicleCreateRequest
from app.api.garage.garage_utils import search_garages_nearby, format_garage
from app.api.garage.garage_models import GarageModel
from app.api.garage_service.garage_service_utils import list_services_for_garage
from app.api.service_type.service_type_utils import get_service_type_by_code
from app.api.booking.booking_utils import (
    list_bookings_for_user, get_booking, format_booking,
)
from app.api.booking.booking_models import BookingModel
from app.api.capacity.capacity_utils import get_current_and_predicted

logger = logging.getLogger(__name__)

customer_router = APIRouter(prefix="/customer", tags=["Customer Portal"])

# ── Tier label mapping ───────────────────────────────────────────
TIER_LABELS = {1: "BASIC", 2: "STANDARD", 3: "PRO", 4: "ELITE"}


def _tier_label(tier_num: int) -> str:
    return TIER_LABELS.get(tier_num, "STANDARD")


# ─────────────────────────────────────────────────────────────────
# 1. Dashboard Summary  (GET /customer/dashboard-summary)
# ─────────────────────────────────────────────────────────────────

@customer_router.get("/dashboard-summary")
async def dashboard_summary(
    lat: Optional[float] = Query(None, ge=-90, le=90),
    lng: Optional[float] = Query(None, ge=-180, le=180),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Aggregated dashboard data for CustomerHome.tsx.
    Gộp 3 nguồn: vehicle diagnostics + smart recommendations + active booking.
    """
    user_id = current_user["user_id"]

    # ── 1a. Vehicle diagnostics (default vehicle) ──
    vehicle_diagnostics = None
    try:
        default_vehicle = await VehicleModel.collection.find_one({
            "owner_user_id": user_id,
            "is_default": True,
            "is_active": True,
        })
        if not default_vehicle:
            # Fallback: first active vehicle
            default_vehicle = await VehicleModel.collection.find_one({
                "owner_user_id": user_id,
                "is_active": True,
            })

        if default_vehicle:
            # Calculate days since last completed service
            days_since_last = None
            last_booking = await BookingModel.collection.find_one(
                {
                    "customer_id": convert_mongo_object_id(user_id),
                    "vehicle_id": default_vehicle["_id"],
                    "status": "completed",
                },
                sort=[("timestamps.service_completed_at", -1)],
            )
            if last_booking:
                ts = (last_booking.get("timestamps") or {}).get("service_completed_at")
                if ts and isinstance(ts, datetime):
                    days_since_last = (get_current_time() - ts).days

            # finish_degradation: derive from days (mock formula for now)
            # Phase 3 Intelligence will replace with real sensor data
            finish_degradation = 0
            if days_since_last is not None:
                finish_degradation = min(0, -(days_since_last * 0.85))  # ~0.85% per day
                finish_degradation = round(finish_degradation)

            vehicle_diagnostics = {
                "default_vehicle_id": str(default_vehicle["_id"]),
                "license_plate": default_vehicle.get("license_plate", ""),
                "brand": default_vehicle.get("brand", ""),
                "model": default_vehicle.get("model", ""),
                "vehicle_type": default_vehicle.get("vehicle_type", "standard"),
                "finish_degradation": finish_degradation,
                "days_since_last_service": days_since_last,
            }
    except Exception as e:
        logger.warning(f"Error loading vehicle diagnostics: {e}")

    # ── 1b. Smart recommendations (nearby garages) ──
    smart_recommendations = []
    if lat is not None and lng is not None:
        try:
            nearby = await search_garages_nearby(
                latitude=lat, longitude=lng,
                max_distance_km=10, min_tier=1,
            )
            for g in nearby[:5]:  # Top 5
                wait_info = g.get("current_load") or {}
                wait_min = int(wait_info.get("estimated_wait_minutes") or 0)
                is_available = g.get("is_accepting_bookings", True) and wait_min < 60

                smart_recommendations.append({
                    "id": g["id"],
                    "name": g.get("name", ""),
                    "tier": _tier_label(g.get("tier", 1)),
                    "distance": f'{g.get("distance_km", 0)} KM',
                    "wait_time": f"{wait_min} MINS" if wait_min > 0 else "READY",
                    "status": "AVAILABLE" if is_available else "BUSY",
                    "score": g.get("tier_score", 0),
                    "lat": (g.get("location") or {}).get("coordinates", [0, 0])[1] if g.get("location") else 0,
                    "lng": (g.get("location") or {}).get("coordinates", [0, 0])[0] if g.get("location") else 0,
                })
        except Exception as e:
            logger.warning(f"Error loading recommendations: {e}")

    # ── 1c. Active booking ──
    active_booking = None
    try:
        active_statuses = ["pending", "confirmed", "customer_arriving", "customer_arrived", "in_service"]
        cust_oid = convert_mongo_object_id(user_id)
        active_doc = await BookingModel.collection.find_one(
            {"customer_id": cust_oid, "status": {"$in": active_statuses}},
            sort=[("created_at", -1)],
        )
        if active_doc:
            active_booking = format_booking(active_doc)
    except Exception as e:
        logger.warning(f"Error loading active booking: {e}")

    return api_response(
        Operation.RETRIEVED, "dashboard_summary",
        data={
            "vehicle_diagnostics": vehicle_diagnostics,
            "smart_recommendations": smart_recommendations,
            "active_booking": active_booking,
        },
    )


# ─────────────────────────────────────────────────────────────────
# 2. Nearby Garages  (GET /customer/nearby)
# ─────────────────────────────────────────────────────────────────

@customer_router.get("/nearby")
async def nearby_garages(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(default=10, ge=1, le=50),
) -> Dict[str, Any]:
    """
    GET endpoint for CustomerMap.tsx — returns garages near a location.
    Public, no auth required.
    """
    raw = await search_garages_nearby(
        latitude=lat, longitude=lng,
        max_distance_km=radius_km, min_tier=1,
    )
    garages = []
    for g in raw:
        coords = (g.get("location") or {}).get("coordinates", [0, 0])
        garages.append({
            "id": g["id"],
            "name": g.get("name", ""),
            "lat": coords[1] if len(coords) > 1 else 0,
            "lng": coords[0] if len(coords) > 0 else 0,
            "score": g.get("tier_score", 0),
            "distance": f'{g.get("distance_km", 0)}km',
            "tier": _tier_label(g.get("tier", 1)),
            "active": g.get("is_accepting_bookings", True),
        })

    return api_response(
        Operation.RETRIEVED, Resource.GARAGES,
        data={"garages": garages},
    )


# ─────────────────────────────────────────────────────────────────
# 3. Garage Portal  (GET /customer/garages/{garage_id}/portal)
# ─────────────────────────────────────────────────────────────────

@customer_router.get("/garages/{garage_id}/portal")
async def garage_portal(garage_id: str) -> Dict[str, Any]:
    """
    Aggregated Garage Detail for GarageDetail.tsx.
    Gộp: info + amenities + services + capacity_load.
    Public endpoint.
    """
    oid = convert_mongo_object_id(garage_id)
    if not oid:
        raise HTTPException(status_code=400, detail="Invalid garage ID")

    garage = await GarageModel.collection.find_one({"_id": oid})
    if not garage:
        raise HTTPException(status_code=404, detail="Garage not found")

    # ── Info ──
    tier_assessment = garage.get("tier_assessment") or {}
    info = {
        "name": garage.get("name", ""),
        "slug": garage.get("slug", ""),
        "tier": _tier_label(garage.get("tier", 1)),
        "tier_num": garage.get("tier", 1),
        "efficiency_score": round(garage.get("tier_score", 0) / 10, 1),  # 0-100 → 0-10
        "is_verified": garage.get("is_verified", False),
        "is_accepting_bookings": garage.get("is_accepting_bookings", True),
        "address": garage.get("address", {}),
        "description": garage.get("description", ""),
        "photos": garage.get("photos", []),
        "stats": garage.get("stats", {}),
        "metrics": {
            "equipment": round(tier_assessment.get("equipment_score", 0) / 10, 1),
            "process": round(tier_assessment.get("process_score", 0) / 10, 1),
            "staff": round(tier_assessment.get("staff_score", 0) / 10, 1),
            "capacity": round(tier_assessment.get("capacity_score", 0) / 10, 1),
            "reliability": round(tier_assessment.get("reliability_score", 0) / 10, 1),
        },
    }

    # ── Amenities ──
    amenities = garage.get("amenities", [])

    # ── Services (enriched with service_type name) ──
    raw_services = await list_services_for_garage(garage_id)
    services = []
    for svc in raw_services:
        # Enrich with service type name & description
        stype = await get_service_type_by_code(svc["service_type_code"])
        services.append({
            "id": svc["id"],
            "code": svc["service_type_code"],
            "name": stype["name"] if stype else svc["service_type_code"],
            "desc": stype["description"] if stype else "",
            "category": stype["category"] if stype else "wash",
            "time_mins": svc.get("estimated_duration_minutes", 30),
            "price_vnd": svc.get("price", 0),
            "is_popular": svc.get("service_type_code") in ("wash_premium", "detailing"),
        })

    # ── Capacity load (hourly pattern) ──
    # Try real data from capacity_snapshots; fallback to operating hours estimate
    capacity_load = []
    try:
        from app.api.capacity.capacity_models import CapacitySnapshotModel
        from datetime import timedelta
        now = get_current_time()
        dow = now.weekday()
        total_bays = int((garage.get("capacity") or {}).get("total_bays", 3))

        # Get recent snapshots for same day-of-week (last 4 weeks)
        cutoff = now - timedelta(weeks=4)
        snapshots = await CapacitySnapshotModel.collection.find({
            "garage_id": oid,
            "day_of_week": dow,
            "timestamp": {"$gte": cutoff},
        }).to_list(length=500)

        if snapshots and len(snapshots) >= 5:
            # Aggregate by hour
            from collections import defaultdict
            hour_data = defaultdict(list)
            for s in snapshots:
                h = s.get("hour_of_day", 0)
                in_svc = int(s.get("vehicles_in_service", 0))
                waiting = int(s.get("vehicles_waiting", 0))
                hour_data[h].append(in_svc + waiting)

            for hour in sorted(hour_data.keys()):
                vals = hour_data[hour]
                avg_load = sum(vals) / len(vals) if vals else 0
                load_pct = min(100, int((avg_load / max(total_bays, 1)) * 100))
                capacity_load.append({
                    "time": f"{hour:02d}:00",
                    "load_percent": load_pct,
                })
        else:
            # Fallback: generate typical pattern
            capacity_load = _generate_typical_capacity_pattern()

    except Exception as e:
        logger.warning(f"Error loading capacity data: {e}")
        capacity_load = _generate_typical_capacity_pattern()

    return api_response(
        Operation.RETRIEVED, Resource.GARAGE,
        data={
            "info": info,
            "amenities": amenities,
            "services": services,
            "capacity_load": capacity_load,
        },
    )


def _generate_typical_capacity_pattern() -> list:
    """Generate realistic default hourly capacity pattern."""
    pattern = [
        ("07:00", 15), ("08:00", 35), ("09:00", 50), ("10:00", 65),
        ("11:00", 75), ("12:00", 90), ("13:00", 85), ("14:00", 80),
        ("15:00", 70), ("16:00", 60), ("17:00", 55), ("18:00", 45),
        ("19:00", 30), ("20:00", 20),
    ]
    return [{"time": t, "load_percent": p} for t, p in pattern]


# ─────────────────────────────────────────────────────────────────
# 4. Bookings  (GET /customer/bookings, GET /customer/bookings/{id}/tracking)
# ─────────────────────────────────────────────────────────────────

@customer_router.get("/bookings")
async def list_customer_bookings(
    status: Optional[str] = Query(None, description="Filter: ACTIVE,COMPLETED,pending,confirmed,..."),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    List bookings for the current user. Supports status filtering.
    Tương ứng spec: GET /api/bookings?status=COMPLETED,ACTIVE
    """
    # Normalize status values (FE may send uppercase)
    filter_status = status.lower() if status else None
    data = await list_bookings_for_user(current_user, filter_status)
    return api_response(Operation.RETRIEVED, Resource.BOOKINGS, data=data)


@customer_router.get("/bookings/{booking_id}")
async def get_customer_booking(
    booking_id: str,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get booking detail by ID."""
    data = await get_booking(booking_id, current_user)
    return api_response(Operation.RETRIEVED, Resource.BOOKING, data=data)


@customer_router.get("/bookings/{booking_id}/tracking")
async def booking_tracking(
    booking_id: str,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Booking timeline for BookingTracker.tsx.
    Transforms timestamps object → ordered timeline array.
    """
    booking = await get_booking(booking_id, current_user)

    # Build ordered timeline from timestamps
    ts = booking.get("timestamps") or {}

    # Define the canonical status flow order
    STATUS_FLOW = [
        ("created_at", "CREATED", "Yêu cầu đã được hệ thống ghi nhận"),
        ("confirmed_at", "CONFIRMED", "Gara đã chấp nhận lịch hẹn"),
        ("customer_departed_at", "CUSTOMER_DEPARTING", "Khách hàng đang trên đường đến"),
        ("customer_arrived_at", "CUSTOMER_ARRIVED", "Khách hàng đã đến gara"),
        ("service_started_at", "IN_SERVICE", "Đang tiến hành dịch vụ"),
        ("service_completed_at", "COMPLETED", "Dịch vụ đã hoàn thành"),
        ("customer_confirmed_at", "CONFIRMED_HANDOVER", "Khách hàng xác nhận nhận xe"),
        ("cancelled_at", "CANCELLED", "Đã hủy"),
    ]

    timeline = []
    for ts_key, status_label, description in STATUS_FLOW:
        timestamp_val = ts.get(ts_key)
        if timestamp_val:
            timeline.append({
                "status": status_label,
                "timestamp": timestamp_val,
                "description": description,
            })

    return api_response(
        Operation.RETRIEVED, Resource.BOOKING,
        data={
            "booking": booking,
            "timeline": timeline,
        },
    )


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
