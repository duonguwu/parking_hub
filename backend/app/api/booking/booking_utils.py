# -*- coding: utf-8 -*-
"""
Booking business logic — creation, state machine, cancellation.

Concurrency: Redis distributed lock per (garage_id, time-rounded-to-minute).
Capacity: predict_capacity at requested_time → reject if available_bays == 0.
"""
import logging
import random
import string
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from bson import ObjectId
from fastapi import HTTPException

from app.api.booking.booking_models import (
    BookingModel, BOOKING_STATUSES, BOOKING_TRANSITIONS, can_transition, is_terminal,
)
from app.api.capacity.capacity_utils import predict_capacity, apply_event, take_snapshot
from app.api.garage.garage_models import GarageModel
from app.api.garage_service.garage_service_utils import get_price_for_garage_service
from app.api.shared.tool.datetime_convert import get_current_time
from app.api.shared.tool.convert_object_id import convert_mongo_object_id
from app.services.shared.redis_client import redis_client

logger = logging.getLogger(__name__)


# ── Helpers ──────────────────────────────────────────────────────

def _now() -> datetime:
    return get_current_time()


def _generate_booking_code() -> str:
    ts = _now().strftime("%Y%m%d")
    rand = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"WM-{ts}-{rand}"


def _slot_lock_key(garage_id: str, at_time: datetime) -> str:
    # Round to minute
    slot = at_time.replace(second=0, microsecond=0).isoformat()
    return f"slot:{garage_id}:{slot}"


def format_booking(doc) -> dict:
    data = doc if isinstance(doc, dict) else doc.dump()
    ts = data.get("timestamps") or {}
    return {
        "id": str(data.get("_id") or data.get("id") or ""),
        "booking_code": data.get("booking_code", ""),
        "tenant_id": data.get("tenant_id", ""),
        "customer_id": str(data.get("customer_id") or ""),
        "garage_id": str(data.get("garage_id") or ""),
        "vehicle_id": str(data.get("vehicle_id") or "") if data.get("vehicle_id") else None,
        "service_type_code": data.get("service_type_code", ""),
        "price": int(data.get("price") or 0),
        "requested_time": data.get("requested_time").isoformat() if data.get("requested_time") else None,
        "estimated_arrival": data.get("estimated_arrival").isoformat() if data.get("estimated_arrival") else None,
        "status": data.get("status", "pending"),
        "timestamps": {k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in ts.items()},
        "matching_context": data.get("matching_context") or {},
        "feedback": data.get("feedback") or {},
        "cancellation_reason": data.get("cancellation_reason", ""),
        "cancelled_by": data.get("cancelled_by", ""),
    }


# ── Create ──────────────────────────────────────────────────────

async def create_booking(
    customer_id: str, garage_id: str, service_type_code: str,
    requested_time: datetime, vehicle_id: Optional[str] = None,
    matching_context: Optional[dict] = None,
) -> dict:
    """
    Create a booking atomically:
      1. Acquire slot lock (Redis)
      2. Predict capacity at requested_time
      3. Reject if no slot available
      4. Insert booking with status=pending
    """
    customer_oid = convert_mongo_object_id(customer_id)
    garage_oid = convert_mongo_object_id(garage_id)
    vehicle_oid = convert_mongo_object_id(vehicle_id) if vehicle_id else None
    if not customer_oid or not garage_oid:
        raise HTTPException(status_code=400, detail="Invalid id")

    garage = await GarageModel.collection.find_one({"_id": garage_oid})
    if not garage:
        raise HTTPException(status_code=404, detail="Garage not found")
    if not garage.get("is_accepting_bookings", True) or garage.get("status") != "active":
        raise HTTPException(status_code=409, detail="Garage is not accepting bookings")

    # Service availability
    if service_type_code not in (garage.get("services_offered") or []):
        raise HTTPException(status_code=409, detail="Service not offered at this garage")

    # Price lookup
    price = await get_price_for_garage_service(garage_id, service_type_code)
    if price is None:
        raise HTTPException(status_code=409, detail="Service price not configured at this garage")

    lock_key = _slot_lock_key(garage_id, requested_time)

    try:
        async with redis_client.lock_context(lock_key, timeout=10, blocking_timeout=3):
            # Inside lock: predict capacity at requested_time
            predicted = await predict_capacity(garage_id, requested_time)
            if predicted.available_bays <= 0 and predicted.vehicles_waiting > 3:
                raise HTTPException(
                    status_code=409,
                    detail="No slot available at requested time (garage near full)",
                )

            now = _now()
            doc = {
                "tenant_id": garage.get("tenant_id", "platform"),
                "booking_code": _generate_booking_code(),
                "customer_id": customer_oid,
                "garage_id": garage_oid,
                "vehicle_id": vehicle_oid,
                "service_type_code": service_type_code,
                "price": int(price),
                "requested_time": requested_time,
                "estimated_arrival": requested_time,
                "status": "pending",
                "timestamps": {"created_at": now},
                "matching_context": matching_context or {},
                "feedback": {},
                "cancellation_reason": "",
                "cancelled_by": "",
                "created_at": now, "updated_at": now,
                "created_by": str(customer_oid),
                "updated_by": str(customer_oid),
            }
            res = await BookingModel.collection.insert_one(doc)
            created = await BookingModel.collection.find_one({"_id": res.inserted_id})
    except TimeoutError:
        raise HTTPException(status_code=409, detail="Slot contention — please retry")

    return format_booking(created)


# ── State machine transitions ───────────────────────────────────

async def _transition(
    booking_id: str, new_status: str,
    ts_field: Optional[str] = None,
    extra_fields: Optional[dict] = None,
    current_user: Optional[dict] = None,
) -> dict:
    oid = convert_mongo_object_id(booking_id)
    if not oid:
        raise HTTPException(status_code=400, detail="Invalid booking id")
    b = await BookingModel.collection.find_one({"_id": oid})
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found")

    cur_status = b.get("status", "pending")
    if not can_transition(cur_status, new_status):
        raise HTTPException(
            status_code=409,
            detail=f"Cannot transition {cur_status} → {new_status}",
        )

    now = _now()
    set_fields = {"status": new_status, "updated_at": now}
    if current_user:
        set_fields["updated_by"] = current_user.get("username", "")
    if ts_field:
        set_fields[f"timestamps.{ts_field}"] = now
    if extra_fields:
        set_fields.update(extra_fields)

    await BookingModel.collection.update_one({"_id": oid}, {"$set": set_fields})
    updated = await BookingModel.collection.find_one({"_id": oid})
    return format_booking(updated)


async def confirm_booking(booking_id: str, current_user: dict) -> dict:
    """Garage confirms a pending booking."""
    return await _transition(
        booking_id, "confirmed", ts_field="confirmed_at", current_user=current_user,
    )


async def depart_booking(booking_id: str, current_user: dict) -> dict:
    """Customer taps 'departing' — begin ETA tracking."""
    return await _transition(
        booking_id, "customer_arriving", ts_field="customer_departed_at",
        current_user=current_user,
    )


async def checkin_booking(
    booking_id: str, current_user: dict,
    method: str = "gps", lat: Optional[float] = None, lng: Optional[float] = None,
) -> dict:
    """Customer checked in. Verify location if method=gps."""
    b = await BookingModel.collection.find_one({"_id": convert_mongo_object_id(booking_id)})
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Verify method
    if method == "gps":
        if lat is None or lng is None:
            raise HTTPException(status_code=400, detail="GPS coordinates required")
        garage = await GarageModel.collection.find_one({"_id": b["garage_id"]})
        if not garage:
            raise HTTPException(status_code=404, detail="Garage not found")
        from app.services.osm.osm_client import haversine_meters, LatLng
        user_loc = LatLng(lat=lat, lng=lng)
        garage_loc = LatLng(
            lat=garage["location"]["coordinates"][1],
            lng=garage["location"]["coordinates"][0],
        )
        if haversine_meters(user_loc, garage_loc) > 200:   # 200m tolerance
            raise HTTPException(status_code=400, detail="Not within garage proximity")
    # method == "qr" — MVP: trust the call (client scanned QR that matched)

    # Compute actual travel time if departed_at exists
    ts = b.get("timestamps") or {}
    departed = ts.get("customer_departed_at")
    extra = {}
    if departed:
        actual_min = (_now() - departed).total_seconds() / 60.0
        extra["matching_context.actual_travel_minutes"] = round(actual_min, 1)

    result = await _transition(
        booking_id, "customer_arrived", ts_field="customer_arrived_at",
        extra_fields=extra, current_user=current_user,
    )
    await apply_event(b["garage_id"], "arrived")
    await take_snapshot(b["garage_id"])
    return result


async def start_service(booking_id: str, current_user: dict) -> dict:
    b = await BookingModel.collection.find_one({"_id": convert_mongo_object_id(booking_id)})
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found")
    result = await _transition(
        booking_id, "in_service", ts_field="service_started_at", current_user=current_user,
    )
    await apply_event(b["garage_id"], "started")
    await take_snapshot(b["garage_id"])
    return result


async def complete_service(booking_id: str, current_user: dict) -> dict:
    b = await BookingModel.collection.find_one({"_id": convert_mongo_object_id(booking_id)})
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found")
    result = await _transition(
        booking_id, "completed", ts_field="service_completed_at", current_user=current_user,
    )
    await apply_event(b["garage_id"], "completed")
    await take_snapshot(b["garage_id"])
    return result


async def cancel_booking(
    booking_id: str, current_user: dict,
    reason: str = "", cancelled_by: str = "customer",
) -> dict:
    b = await BookingModel.collection.find_one({"_id": convert_mongo_object_id(booking_id)})
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found")

    cur = b.get("status", "pending")
    if cancelled_by == "customer":
        target = "cancelled_by_customer"
    else:
        target = "cancelled_by_garage"

    if not can_transition(cur, target):
        raise HTTPException(
            status_code=409, detail=f"Cannot cancel from state {cur}",
        )

    # Compute cancellation fee hint (MVP: not enforced, just returned)
    fee_pct = 0
    if cur == "confirmed":
        fee_pct = 10
    elif cur == "customer_arriving":
        fee_pct = 20
    # Garage cancels → no customer fee, rely on penalty tracking

    result = await _transition(
        booking_id, target, ts_field="cancelled_at",
        extra_fields={
            "cancellation_reason": reason,
            "cancelled_by": cancelled_by,
        },
        current_user=current_user,
    )

    # If customer already arrived (somehow cancellable), update capacity
    if cur == "customer_arrived":
        await apply_event(b["garage_id"], "cancel_at_garage")
        await take_snapshot(b["garage_id"])

    result["cancellation_fee_percent"] = fee_pct
    return result


# ── Feedback ────────────────────────────────────────────────────

async def submit_feedback(
    booking_id: str, current_user: dict,
    rating: Optional[int] = None, quick_feedback: Optional[str] = None,
    comment: Optional[str] = None,
) -> dict:
    oid = convert_mongo_object_id(booking_id)
    if not oid:
        raise HTTPException(status_code=400, detail="Invalid id")
    b = await BookingModel.collection.find_one({"_id": oid})
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found")
    # Only customer can leave feedback on own booking
    if str(b.get("customer_id")) != str(current_user.get("user_id")):
        raise HTTPException(status_code=403, detail="Not your booking")
    if b.get("status") != "completed":
        raise HTTPException(status_code=409, detail="Can only feedback on completed bookings")

    fb = {}
    if rating is not None:
        if not 1 <= int(rating) <= 5:
            raise HTTPException(status_code=400, detail="Rating must be 1-5")
        fb["rating"] = int(rating)
    if quick_feedback in ("thumbs_up", "thumbs_down"):
        fb["quick_feedback"] = quick_feedback
    if comment:
        fb["comment"] = str(comment)[:1000]

    if not fb:
        raise HTTPException(status_code=400, detail="Empty feedback")

    await BookingModel.collection.update_one(
        {"_id": oid}, {"$set": {"feedback": {**(b.get("feedback") or {}), **fb},
                                 "updated_at": _now()}},
    )
    updated = await BookingModel.collection.find_one({"_id": oid})
    return format_booking(updated)


# ── Queries ─────────────────────────────────────────────────────

async def list_bookings_for_user(current_user: dict, status_filter: Optional[str] = None) -> List[dict]:
    role = current_user.get("role", "")
    query: Dict[str, Any] = {}

    if role == "customer":
        cust_oid = convert_mongo_object_id(current_user.get("user_id"))
        query["customer_id"] = cust_oid
    elif role in ("garage_owner", "garage_manager", "garage_staff"):
        query["tenant_id"] = current_user.get("tenant_id")
    elif current_user.get("tenant_id") == "super_admin":
        pass    # see all
    else:
        return []

    if status_filter:
        query["status"] = status_filter

    docs = await BookingModel.collection.find(query).sort("created_at", -1).to_list(length=100)
    return [format_booking(d) for d in docs]


async def get_booking(booking_id: str, current_user: dict) -> dict:
    oid = convert_mongo_object_id(booking_id)
    if not oid:
        raise HTTPException(status_code=400, detail="Invalid id")
    doc = await BookingModel.collection.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Authorization: customer sees own; garage tenant sees own; super_admin sees all
    role = current_user.get("role", "")
    if role == "customer":
        if str(doc.get("customer_id")) != str(current_user.get("user_id")):
            raise HTTPException(status_code=403, detail="Not your booking")
    elif current_user.get("tenant_id") != "super_admin":
        if doc.get("tenant_id") != current_user.get("tenant_id"):
            raise HTTPException(status_code=403, detail="Not authorized")

    return format_booking(doc)
