# -*- coding: utf-8 -*-
"""Customer Portal utils — gom dữ liệu cho app tài xế."""
import logging
from datetime import timedelta
from typing import Optional, List

from fastapi import HTTPException

from app.api.booking.booking_models import BookingModel, ACTIVE_STATUSES
from app.api.booking.booking_utils import enrich_bookings, sweep_overdue, get_booking
from app.api.capacity.capacity_utils import hourly_rates, predict_availability
from app.api.garage.garage_utils import get_garage_detail, search_garages
from app.api.garage.garage_models import GarageModel
from app.api.garage_service.garage_service_utils import list_services_for_garage
from app.api.garage_service.pricing_utils import to_local
from app.api.service_type.service_type_utils import get_service_type_map
from app.api.user.user_models import UserModel
from app.api.vehicle.vehicle_models import VehicleModel
from app.api.shared.tool.convert_object_id import convert_mongo_object_id
from app.api.shared.tool.datetime_convert import get_current_time

logger = logging.getLogger(__name__)

STATUS_ORDER = {"available": 0, "limited": 1, "unknown": 2, "full": 3}


async def get_dashboard_summary(current_user: dict, lat: Optional[float], lng: Optional[float]) -> dict:
    user_id = current_user["user_id"]
    cust_oid = convert_mongo_object_id(user_id)
    await sweep_overdue(customer_oid=cust_oid)

    vehicle = await VehicleModel.collection.find_one(
        {"owner_user_id": user_id, "is_active": True}, sort=[("is_default", -1)],
    )
    active_docs = await BookingModel.collection.find(
        {"customer_id": cust_oid, "status": {"$in": ACTIVE_STATUSES}},
    ).sort("start_time", 1).to_list(length=10)

    done = await BookingModel.collection.find(
        {"customer_id": cust_oid, "status": "checked_out"}, {"final_price": 1, "garage_id": 1},
    ).to_list(length=5000)

    nearby: List[dict] = []
    if lat is not None and lng is not None:
        cards = await search_garages(lat=lat, lng=lng, radius_km=3, limit=60)
        cards.sort(key=lambda c: (STATUS_ORDER.get(c["availability"]["status"], 9), c.get("distance_km") or 0))
        nearby = cards[:6]

    return {
        "default_vehicle": {
            "id": str(vehicle["_id"]),
            "license_plate": vehicle.get("license_plate", ""),
            "brand": vehicle.get("brand", ""), "model": vehicle.get("model", ""),
        } if vehicle else None,
        "active_bookings": await enrich_bookings(active_docs),
        "nearby": nearby,
        "stats": {
            "total_sessions": len(done),
            "total_spent": sum(int(b.get("final_price") or 0) for b in done),
            "lots_visited": len({b["garage_id"] for b in done}),
        },
    }


async def get_garage_portal(garage_id: str) -> dict:
    """Trang chi tiết bãi cho tài xế."""
    garage = await get_garage_detail(garage_id)
    if garage["status"] != "active":
        raise HTTPException(status_code=404, detail="Bãi không hoạt động")
    oid = convert_mongo_object_id(garage_id)
    raw = await GarageModel.collection.find_one({"_id": oid})

    stype_map = await get_service_type_map()
    services = []
    for svc in await list_services_for_garage(garage_id):
        st = stype_map.get(svc["service_type_code"]) or {}
        services.append({
            "id": svc["id"], "code": svc["service_type_code"],
            "name": st.get("name", svc["service_type_code"]), "desc": st.get("description", ""),
            "category": st.get("category", "parking"), "unit": st.get("unit", "hour"),
            "icon": st.get("icon", "clock"), "sort_order": st.get("sort_order", 999),
            "time_mins": svc.get("estimated_duration_minutes", 60),
            "price_vnd": svc.get("price", 0), "pricing": svc.get("pricing", {}),
            "note": svc.get("note", ""), "is_popular": bool(st.get("is_popular")),
        })
    services.sort(key=lambda s: s["sort_order"])

    now = get_current_time()
    dow = to_local(now).weekday()
    hourly = await hourly_rates(raw, day_of_week=dow)
    forecast = []
    if garage["integration_level"] >= 2:
        for h in (1, 2, 3):
            forecast.append({"hours_ahead": h, **(await predict_availability(raw, now + timedelta(hours=h)))})

    reviews_docs = await BookingModel.collection.find(
        {"garage_id": oid, "status": "checked_out", "feedback.rating": {"$exists": True}},
        {"feedback": 1, "customer_id": 1, "timestamps": 1},
    ).sort("timestamps.checked_out_at", -1).to_list(length=5)
    users = {u["_id"]: u async for u in UserModel.collection.find(
        {"_id": {"$in": [r["customer_id"] for r in reviews_docs if r.get("customer_id")]}}, {"name": 1})}
    reviews = [{
        "rating": r["feedback"].get("rating"),
        "comment": r["feedback"].get("comment", ""),
        "name": (users.get(r.get("customer_id")) or {}).get("name", "Khách"),
        "at": ((r.get("timestamps") or {}).get("checked_out_at") or now).isoformat(),
    } for r in reviews_docs]

    return {
        "garage": garage,
        "services": services,
        "hourly_today": hourly,
        "forecast": forecast,
        "reviews": reviews,
    }


TIMELINE = [
    ("created_at", "CREATED", "Đã gửi yêu cầu đặt chỗ"),
    ("reserved_at", "RESERVED", "Bãi đã giữ chỗ cho bạn"),
    ("checked_in_at", "CHECKED_IN", "Xe đã vào bãi"),
    ("checked_out_at", "CHECKED_OUT", "Xe đã ra bãi"),
    ("paid_at", "PAID", "Đã thanh toán"),
    ("cancelled_at", "CANCELLED", "Đã huỷ"),
    ("rejected_at", "REJECTED", "Bãi từ chối yêu cầu"),
    ("no_show_at", "NO_SHOW", "Quá thời gian giữ chỗ, xe không đến"),
    ("expired_at", "EXPIRED", "Bãi chưa xác nhận trước giờ hẹn"),
]


async def get_booking_tracking(booking_id: str, current_user: dict) -> dict:
    booking = await get_booking(booking_id, current_user)
    ts = booking.get("timestamps") or {}
    timeline = [{"status": label, "timestamp": ts[key], "description": desc}
                for key, label, desc in TIMELINE if ts.get(key)]
    timeline.sort(key=lambda x: x["timestamp"])
    return {"booking": booking, "timeline": timeline}
