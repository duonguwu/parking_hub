# -*- coding: utf-8 -*-
"""
Booking business logic — giữ chỗ theo khung giờ, vào/ra bãi, tính tiền.

Concurrency: Redis lock theo bãi khi tạo lượt (đếm suất giữ chỗ trong khung giờ).
Sức chứa: số lượt chiếm suất chồng lấn khung giờ ≤ floor(total_spots × reservable_ratio).
Cam kết theo cấp tích hợp: cấp 1 không nhận đặt · cấp 2 chờ bãi xác nhận · cấp 3–4 tự giữ chỗ.
"""
import logging
import math
import random
import string
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from bson import ObjectId
from fastapi import HTTPException

from app.api.booking.booking_models import (
    BookingModel, HOLDING_STATUSES, can_transition,
)
from app.api.capacity.capacity_utils import adjust_occupied, get_availability, HOLD_BEFORE_MINUTES
from app.api.garage.garage_models import GarageModel
from app.api.garage.garage_stats_utils import recompute_garage_stats
from app.api.garage_service.garage_service_utils import get_garage_service_doc, resolve_pricing
from app.api.garage_service.pricing_utils import quote_price
from app.api.user.user_models import UserModel
from app.api.vehicle.vehicle_models import VehicleModel
from app.api.service_type.service_type_models import ServiceTypeModel
from app.api.shared.tool.datetime_convert import get_current_time
from app.api.shared.tool.convert_object_id import convert_mongo_object_id
from app.services.shared.redis_client import redis_client

logger = logging.getLogger(__name__)

MAX_BOOKING_DAYS = 31
STAFF_ROLES = ("garage_owner", "garage_manager", "garage_staff")


# ── Helpers ──────────────────────────────────────────────────────

def _now() -> datetime:
    return get_current_time()


def _iso(v):
    return v.isoformat() if isinstance(v, datetime) else v


def _generate_booking_code() -> str:
    ts = _now().strftime("%Y%m%d")
    rand = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"PH-{ts}-{rand}"


def normalize_plate(plate: Optional[str]) -> str:
    return "".join(ch for ch in (plate or "").upper() if ch.isalnum() or ch in "-.")


def format_booking(doc, extra: Optional[dict] = None) -> dict:
    data = doc if isinstance(doc, dict) else doc.dump()
    ts = data.get("timestamps") or {}
    out = {
        "id": str(data.get("_id") or data.get("id") or ""),
        "booking_code": data.get("booking_code", ""),
        "tenant_id": data.get("tenant_id", ""),
        "customer_id": str(data["customer_id"]) if data.get("customer_id") else None,
        "garage_id": str(data.get("garage_id") or ""),
        "vehicle_id": str(data["vehicle_id"]) if data.get("vehicle_id") else None,
        "license_plate": data.get("license_plate", ""),
        "service_type_code": data.get("service_type_code", ""),
        "quoted_price": int(data.get("quoted_price") or 0),
        "final_price": int(data["final_price"]) if data.get("final_price") is not None else None,
        "payment_status": data.get("payment_status", "unpaid"),
        "payment_method": data.get("payment_method", ""),
        "start_time": _iso(data.get("start_time")),
        "end_time": _iso(data.get("end_time")),
        "grace_until": _iso(data.get("grace_until")),
        "status": data.get("status", "pending"),
        "source": data.get("source", "app"),
        "timestamps": {k: _iso(v) for k, v in ts.items()},
        "matching_context": data.get("matching_context") or {},
        "feedback": data.get("feedback") or {},
        "cancellation_reason": data.get("cancellation_reason", ""),
        "cancelled_by": data.get("cancelled_by", ""),
    }
    if extra:
        out.update(extra)
    return out


async def enrich_bookings(docs: List[dict]) -> List[dict]:
    """Gắn tên bãi, tên dịch vụ, tên khách cho danh sách lượt (batch query)."""
    garage_ids = list({d["garage_id"] for d in docs if d.get("garage_id")})
    customer_ids = list({d["customer_id"] for d in docs if d.get("customer_id")})
    codes = list({d.get("service_type_code") for d in docs})
    garages = {g["_id"]: g async for g in GarageModel.collection.find(
        {"_id": {"$in": garage_ids}}, {"name": 1, "address": 1, "location": 1})}
    users = {u["_id"]: u async for u in UserModel.collection.find(
        {"_id": {"$in": customer_ids}}, {"name": 1, "phone": 1})}
    stypes = {s["code"]: s async for s in ServiceTypeModel.collection.find(
        {"code": {"$in": codes}}, {"code": 1, "name": 1, "unit": 1})}
    out = []
    for d in docs:
        g = garages.get(d.get("garage_id")) or {}
        u = users.get(d.get("customer_id")) or {}
        coords = (g.get("location") or {}).get("coordinates") or [0, 0]
        out.append(format_booking(d, {
            "garage_name": g.get("name", ""),
            "garage_address": ", ".join(x for x in [(g.get("address") or {}).get("street"),
                                                    (g.get("address") or {}).get("district")] if x),
            "garage_location": {"lat": coords[1], "lng": coords[0]},
            "customer_name": u.get("name", "") or ("Khách vãng lai" if not d.get("customer_id") else ""),
            "customer_phone": u.get("phone", ""),
            "service_name": (stypes.get(d.get("service_type_code")) or {}).get("name", d.get("service_type_code")),
        }))
    return out


def _assert_staff_of(booking: dict, current_user: dict) -> None:
    if current_user.get("tenant_id") == "super_admin":
        return
    if current_user.get("role") not in STAFF_ROLES or booking.get("tenant_id") != current_user.get("tenant_id"):
        raise HTTPException(status_code=403, detail="Không có quyền với lượt đặt này")


def _assert_customer_of(booking: dict, current_user: dict) -> None:
    if str(booking.get("customer_id")) != str(current_user.get("user_id")):
        raise HTTPException(status_code=403, detail="Không phải lượt đặt của bạn")


async def _load(booking_id: str) -> dict:
    oid = convert_mongo_object_id(booking_id)
    if not oid:
        raise HTTPException(status_code=400, detail="Invalid booking id")
    b = await BookingModel.collection.find_one({"_id": oid})
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found")
    return b


async def count_overlapping(garage_oid: ObjectId, start: datetime, end: datetime,
                            exclude_id: Optional[ObjectId] = None) -> int:
    q: Dict[str, Any] = {
        "garage_id": garage_oid,
        "status": {"$in": HOLDING_STATUSES},
        "source": {"$ne": "walk_in"},
        "start_time": {"$lt": end},
        "end_time": {"$gt": start},
    }
    if exclude_id:
        q["_id"] = {"$ne": exclude_id}
    return await BookingModel.collection.count_documents(q)


def reservable_quota(garage: dict) -> int:
    cap = garage.get("capacity") or {}
    total = int(cap.get("total_spots") or 1)
    ratio = float(cap.get("reservable_ratio") or 0.5)
    return max(1, math.floor(total * ratio))


# ── Create ──────────────────────────────────────────────────────

async def create_booking(
    customer_id: str, garage_id: str, service_type_code: str,
    start_time: datetime, end_time: Optional[datetime] = None,
    vehicle_id: Optional[str] = None, license_plate: Optional[str] = None,
    matching_context: Optional[dict] = None, source: str = "app",
) -> dict:
    customer_oid = convert_mongo_object_id(customer_id)
    garage_oid = convert_mongo_object_id(garage_id)
    vehicle_oid = convert_mongo_object_id(vehicle_id) if vehicle_id else None
    if not customer_oid or not garage_oid:
        raise HTTPException(status_code=400, detail="Invalid id")

    garage = await GarageModel.collection.find_one({"_id": garage_oid})
    if not garage:
        raise HTTPException(status_code=404, detail="Garage not found")
    if not garage.get("is_accepting_bookings", True) or garage.get("status") != "active":
        raise HTTPException(status_code=409, detail="Bãi đang tạm ngưng nhận đặt chỗ")
    level = int(garage.get("integration_level") or 1)
    if level < 2:
        raise HTTPException(status_code=409, detail="Bãi này chỉ hiển thị thông tin, chưa nhận đặt chỗ")

    gsvc = await get_garage_service_doc(garage_id, service_type_code)
    if not gsvc or service_type_code not in (garage.get("services_offered") or []):
        raise HTTPException(status_code=409, detail="Bãi không cung cấp dịch vụ này")

    now = _now()
    if start_time.tzinfo is None:
        raise HTTPException(status_code=422, detail="start_time phải có múi giờ")
    if start_time < now - timedelta(minutes=10):
        raise HTTPException(status_code=422, detail="Giờ bắt đầu đã qua")
    if start_time > now + timedelta(days=60):
        raise HTTPException(status_code=422, detail="Chỉ đặt trước tối đa 60 ngày")
    if end_time is None:
        end_time = start_time + timedelta(minutes=int(gsvc.get("estimated_duration_minutes") or 120))
    if end_time <= start_time:
        raise HTTPException(status_code=422, detail="Giờ kết thúc phải sau giờ bắt đầu")
    if end_time - start_time > timedelta(days=MAX_BOOKING_DAYS):
        raise HTTPException(status_code=422, detail=f"Tối đa {MAX_BOOKING_DAYS} ngày mỗi lượt")

    plate = normalize_plate(license_plate)
    if vehicle_oid:
        v = await VehicleModel.collection.find_one({"_id": vehicle_oid})
        if not v or str(v.get("owner_user_id")) != str(customer_oid):
            raise HTTPException(status_code=404, detail="Không tìm thấy xe")
        plate = plate or normalize_plate(v.get("license_plate"))

    quote = quote_price(resolve_pricing(gsvc), start_time, end_time)
    grace = int((garage.get("capacity") or {}).get("grace_minutes") or 15)

    try:
        async with redis_client.lock_context(f"booking:{garage_id}", timeout=10, blocking_timeout=3):
            dup = await BookingModel.collection.find_one({
                "garage_id": garage_oid, "customer_id": customer_oid,
                "status": {"$in": HOLDING_STATUSES},
                "start_time": {"$lt": end_time}, "end_time": {"$gt": start_time},
            })
            if dup:
                raise HTTPException(status_code=409, detail="Bạn đã có lượt đặt trùng khung giờ tại bãi này")

            if await count_overlapping(garage_oid, start_time, end_time) >= reservable_quota(garage):
                raise HTTPException(status_code=409, detail="Bãi đã hết suất giữ chỗ trong khung giờ này")

            if start_time <= now + timedelta(minutes=HOLD_BEFORE_MINUTES):
                avail = await get_availability(garage)
                if avail["has_data"] and (avail["available"] or 0) <= 0:
                    raise HTTPException(status_code=409, detail="Bãi hiện đã hết chỗ")

            status = "reserved" if level >= 3 else "pending"
            stamps = {"created_at": now}
            if status == "reserved":
                stamps["reserved_at"] = now
            doc = {
                "tenant_id": garage.get("tenant_id", "platform"),
                "booking_code": _generate_booking_code(),
                "customer_id": customer_oid,
                "garage_id": garage_oid,
                "vehicle_id": vehicle_oid,
                "license_plate": plate,
                "service_type_code": service_type_code,
                "quoted_price": int(quote["amount"]),
                "final_price": None,
                "payment_status": "unpaid",
                "payment_method": "",
                "start_time": start_time,
                "end_time": end_time,
                "grace_until": start_time + timedelta(minutes=grace),
                "status": status,
                "source": source,
                "timestamps": stamps,
                "matching_context": matching_context or {},
                "feedback": {},
                "cancellation_reason": "",
                "cancelled_by": "",
                "created_at": now, "updated_at": now,
                "created_by": str(customer_oid), "updated_by": str(customer_oid),
            }
            res = await BookingModel.collection.insert_one(doc)
            created = await BookingModel.collection.find_one({"_id": res.inserted_id})
    except TimeoutError:
        raise HTTPException(status_code=409, detail="Hệ thống đang bận, vui lòng thử lại")

    return format_booking(created, {"quote": quote})


async def create_walk_in(garage: dict, license_plate: str, service_type_code: str, current_user: dict) -> dict:
    """Chủ bãi ghi nhận xe vãng lai vào bãi (không qua đặt trước)."""
    if current_user.get("tenant_id") not in ("super_admin", garage.get("tenant_id")):
        raise HTTPException(status_code=403, detail="Không phải bãi của bạn")
    plate = normalize_plate(license_plate)
    if not plate:
        raise HTTPException(status_code=422, detail="Cần nhập biển số")
    gsvc = await get_garage_service_doc(str(garage["_id"]), service_type_code)
    if not gsvc:
        raise HTTPException(status_code=409, detail="Bãi chưa cấu hình dịch vụ này")
    inside = await BookingModel.collection.find_one({"garage_id": garage["_id"], "license_plate": plate, "status": "checked_in"})
    if inside:
        raise HTTPException(status_code=409, detail=f"Xe {plate} đang ở trong bãi")
    now = _now()
    end = now + timedelta(minutes=int(gsvc.get("estimated_duration_minutes") or 120))
    doc = {
        "tenant_id": garage.get("tenant_id"),
        "booking_code": _generate_booking_code(),
        "customer_id": None, "garage_id": garage["_id"], "vehicle_id": None,
        "license_plate": plate, "service_type_code": service_type_code,
        "quoted_price": int(quote_price(resolve_pricing(gsvc), now, end)["amount"]),
        "final_price": None, "payment_status": "unpaid", "payment_method": "",
        "start_time": now, "end_time": end, "grace_until": now,
        "status": "checked_in", "source": "walk_in",
        "timestamps": {"created_at": now, "checked_in_at": now},
        "matching_context": {}, "feedback": {}, "cancellation_reason": "", "cancelled_by": "",
        "created_at": now, "updated_at": now,
        "created_by": current_user.get("username", ""), "updated_by": current_user.get("username", ""),
    }
    res = await BookingModel.collection.insert_one(doc)
    await adjust_occupied(garage["_id"], +1)
    return format_booking(await BookingModel.collection.find_one({"_id": res.inserted_id}))


# ── State machine transitions ───────────────────────────────────

async def _transition(
    b: dict, new_status: str, current_user: Optional[dict] = None,
    ts_field: Optional[str] = None, extra_fields: Optional[dict] = None,
) -> dict:
    cur_status = b.get("status", "pending")
    if not can_transition(cur_status, new_status):
        raise HTTPException(status_code=409, detail=f"Không thể chuyển {cur_status} → {new_status}")
    now = _now()
    set_fields = {"status": new_status, "updated_at": now}
    if current_user:
        set_fields["updated_by"] = current_user.get("username", "")
    if ts_field:
        set_fields[f"timestamps.{ts_field}"] = now
    if extra_fields:
        set_fields.update(extra_fields)
    res = await BookingModel.collection.update_one(
        {"_id": b["_id"], "status": cur_status}, {"$set": set_fields},
    )
    if res.modified_count == 0:
        raise HTTPException(status_code=409, detail="Lượt đặt vừa được cập nhật bởi người khác")
    return await BookingModel.collection.find_one({"_id": b["_id"]})


async def confirm_booking(booking_id: str, current_user: dict) -> dict:
    """Bãi cấp 2 xác nhận lượt pending → reserved."""
    b = await _load(booking_id)
    _assert_staff_of(b, current_user)
    return format_booking(await _transition(b, "reserved", current_user, "reserved_at"))


async def reject_booking(booking_id: str, current_user: dict, reason: str = "") -> dict:
    b = await _load(booking_id)
    _assert_staff_of(b, current_user)
    return format_booking(await _transition(
        b, "rejected", current_user, "rejected_at",
        {"cancellation_reason": reason, "cancelled_by": "garage"},
    ))


async def checkin_booking(booking_id: str, current_user: dict, license_plate: Optional[str] = None) -> dict:
    """Xe vào bãi. Nhân viên bãi check-in (đối chiếu biển số nếu có)."""
    b = await _load(booking_id)
    _assert_staff_of(b, current_user)
    extra = {}
    plate = normalize_plate(license_plate)
    if plate:
        if b.get("license_plate") and plate != b["license_plate"]:
            raise HTTPException(status_code=409, detail=f"Biển số không khớp lượt đặt ({b['license_plate']})")
        extra["license_plate"] = plate
    if _now() < b["start_time"] - timedelta(hours=2):
        raise HTTPException(status_code=409, detail="Còn quá sớm so với giờ hẹn (tối đa 2 giờ)")
    updated = await _transition(b, "checked_in", current_user, "checked_in_at", extra)
    await adjust_occupied(b["garage_id"], +1)
    return format_booking(updated)


async def compute_final_price(b: dict, until: Optional[datetime] = None) -> dict:
    """Tính tiền theo thời gian thực tế: từ lúc vào (hoặc giờ hẹn nếu vào sớm) tới lúc ra."""
    until = until or _now()
    checked_in = (b.get("timestamps") or {}).get("checked_in_at") or b["start_time"]
    start = max(checked_in, b["start_time"]) if b.get("source") != "walk_in" else checked_in
    gsvc = await get_garage_service_doc(str(b["garage_id"]), b["service_type_code"])
    if not gsvc or until <= start:
        return {"amount": int(b.get("quoted_price") or 0), "minutes": 0, "breakdown": []}
    q = quote_price(resolve_pricing(gsvc), start, until)
    # Không thấp hơn báo giá lúc đặt cho gói trọn (đêm/ngày/tháng)
    if (resolve_pricing(gsvc).get("mode") == "flat"):
        q["amount"] = max(q["amount"], int(b.get("quoted_price") or 0))
    return q


async def checkout_booking(booking_id: str, current_user: dict, payment_method: Optional[str] = None) -> dict:
    b = await _load(booking_id)
    _assert_staff_of(b, current_user)
    q = await compute_final_price(b)
    extra = {"final_price": int(q["amount"])}
    if payment_method in ("cash", "transfer"):
        extra.update({"payment_status": "paid", "payment_method": payment_method, "timestamps.paid_at": _now()})
    updated = await _transition(b, "checked_out", current_user, "checked_out_at", extra)
    await adjust_occupied(b["garage_id"], -1)
    await recompute_garage_stats(b["garage_id"])
    return format_booking(updated, {"price_breakdown": q})


async def mark_paid(booking_id: str, current_user: dict, payment_method: str) -> dict:
    b = await _load(booking_id)
    _assert_staff_of(b, current_user)
    if b.get("status") != "checked_out":
        raise HTTPException(status_code=409, detail="Chỉ ghi nhận thanh toán sau khi xe ra")
    await BookingModel.collection.update_one({"_id": b["_id"]}, {"$set": {
        "payment_status": "paid", "payment_method": payment_method,
        "timestamps.paid_at": _now(), "updated_at": _now(),
    }})
    return format_booking(await BookingModel.collection.find_one({"_id": b["_id"]}))


async def mark_no_show(booking_id: str, current_user: dict) -> dict:
    b = await _load(booking_id)
    _assert_staff_of(b, current_user)
    if _now() < b["grace_until"]:
        raise HTTPException(status_code=409, detail="Chưa hết thời gian giữ chỗ")
    updated = await _transition(b, "no_show", current_user, "no_show_at")
    await recompute_garage_stats(b["garage_id"])
    return format_booking(updated)


async def cancel_booking(booking_id: str, current_user: dict, reason: str = "") -> dict:
    """Khách huỷ lượt của mình (pending/reserved). Bãi huỷ lượt đã giữ → tính vào tỉ lệ giữ đúng chỗ."""
    b = await _load(booking_id)
    if str(b.get("customer_id")) == str(current_user.get("user_id")):
        by = "customer"
    else:
        _assert_staff_of(b, current_user)
        by = "garage"
        if b.get("status") == "pending":
            return await reject_booking(booking_id, current_user, reason)
    updated = await _transition(
        b, "cancelled", current_user, "cancelled_at",
        {"cancellation_reason": reason, "cancelled_by": by},
    )
    if by == "garage":
        await recompute_garage_stats(b["garage_id"])
    return format_booking(updated)


async def sweep_overdue(garage_oid: Optional[ObjectId] = None, customer_oid: Optional[ObjectId] = None) -> int:
    """Lazy sweep: reserved quá grace → no_show; pending quá giờ bắt đầu → expired."""
    now = _now()
    scope: Dict[str, Any] = {}
    if garage_oid:
        scope["garage_id"] = garage_oid
    if customer_oid:
        scope["customer_id"] = customer_oid
    r1 = await BookingModel.collection.update_many(
        {**scope, "status": "reserved", "grace_until": {"$lt": now}},
        {"$set": {"status": "no_show", "timestamps.no_show_at": now, "updated_at": now, "updated_by": "system"}},
    )
    r2 = await BookingModel.collection.update_many(
        {**scope, "status": "pending", "start_time": {"$lt": now}},
        {"$set": {"status": "expired", "timestamps.expired_at": now, "updated_at": now, "updated_by": "system"}},
    )
    return r1.modified_count + r2.modified_count


# ── Feedback ────────────────────────────────────────────────────

async def submit_feedback(
    booking_id: str, current_user: dict,
    rating: Optional[int] = None, quick_feedback: Optional[str] = None,
    comment: Optional[str] = None, complaint: Optional[bool] = None,
) -> dict:
    b = await _load(booking_id)
    _assert_customer_of(b, current_user)
    if b.get("status") != "checked_out":
        raise HTTPException(status_code=409, detail="Chỉ đánh giá sau khi xe đã ra bãi")

    fb = {}
    if rating is not None:
        if not 1 <= int(rating) <= 5:
            raise HTTPException(status_code=400, detail="Rating must be 1-5")
        fb["rating"] = int(rating)
    if quick_feedback in ("thumbs_up", "thumbs_down"):
        fb["quick_feedback"] = quick_feedback
    if comment:
        fb["comment"] = str(comment)[:1000]
    if complaint is not None:
        fb["complaint"] = bool(complaint)
    if not fb:
        raise HTTPException(status_code=400, detail="Empty feedback")

    await BookingModel.collection.update_one(
        {"_id": b["_id"]}, {"$set": {"feedback": {**(b.get("feedback") or {}), **fb}, "updated_at": _now()}},
    )
    await recompute_garage_stats(b["garage_id"])
    return format_booking(await BookingModel.collection.find_one({"_id": b["_id"]}))


# ── Queries ─────────────────────────────────────────────────────

async def list_bookings_for_user(current_user: dict, status_filter: Optional[str] = None,
                                 limit: int = 100) -> List[dict]:
    role = current_user.get("role", "")
    query: Dict[str, Any] = {}

    if role in STAFF_ROLES:
        query["tenant_id"] = current_user.get("tenant_id")
    elif current_user.get("tenant_id") == "super_admin":
        pass    # see all
    else:
        cust_oid = convert_mongo_object_id(current_user.get("user_id"))
        if not cust_oid:
            return []
        await sweep_overdue(customer_oid=cust_oid)
        query["customer_id"] = cust_oid

    if status_filter:
        statuses = [s.strip() for s in status_filter.split(",") if s.strip()]
        query["status"] = {"$in": statuses} if len(statuses) > 1 else statuses[0]

    docs = await BookingModel.collection.find(query).sort("start_time", -1).to_list(length=limit)
    return await enrich_bookings(docs)


async def get_booking(booking_id: str, current_user: dict) -> dict:
    doc = await _load(booking_id)
    if current_user.get("tenant_id") != "super_admin":
        if current_user.get("role") in STAFF_ROLES:
            if doc.get("tenant_id") != current_user.get("tenant_id"):
                raise HTTPException(status_code=403, detail="Not authorized")
        else:
            _assert_customer_of(doc, current_user)
    return (await enrich_bookings([doc]))[0]
