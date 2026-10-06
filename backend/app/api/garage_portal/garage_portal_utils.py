# -*- coding: utf-8 -*-
"""
Garage Owner Portal — nghiệp vụ cho chủ bãi.

Mọi dữ liệu giới hạn trong bãi của tenant hiện tại.
Tái sử dụng booking_utils / capacity_utils / garage_utils, không lặp logic.
"""
import logging
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException

from app.api.booking.booking_models import BookingModel
from app.api.booking.booking_utils import enrich_bookings, sweep_overdue, compute_final_price, normalize_plate
from app.api.capacity.capacity_models import CapacitySnapshotModel
from app.api.capacity.capacity_utils import get_availability, hourly_rates
from app.api.garage.garage_models import GarageModel
from app.api.garage.garage_classification_utils import (
    compute_grade, GRADE_CHECKLIST, GRADE_GROUPS, INTEGRATION_LEVELS, compute_badges,
)
from app.api.garage.garage_stats_utils import MIN_SESSIONS_FOR_SCORE
from app.api.garage_service.garage_service_models import GarageServiceModel
from app.api.garage_service.garage_service_utils import upsert_garage_service, resolve_pricing
from app.api.garage_service.pricing_utils import to_local, LOCAL_TZ
from app.api.service_type.service_type_utils import get_service_type_by_code, get_service_type_map
from app.api.shared.tool.datetime_convert import get_current_time
from app.api.shared.tool.convert_object_id import convert_mongo_object_id

logger = logging.getLogger(__name__)

DOW_LABELS = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]


def _parse_range_days(range_str: str) -> int:
    return {"7D": 7, "30D": 30, "90D": 90}.get((range_str or "30D").upper(), 30)


def _local_day_start(now: datetime) -> datetime:
    """00:00 hôm nay theo giờ VN, trả về aware datetime."""
    local = to_local(now)
    return LOCAL_TZ.localize(datetime(local.year, local.month, local.day))


def _revenue(b: dict) -> int:
    return int(b.get("final_price") if b.get("final_price") is not None else 0)


# ── Garage Resolution ────────────────────────────────────────────

GARAGE_STAFF_ROLES = ("garage_owner", "garage_manager", "garage_staff")


def _is_admin(current_user: dict) -> bool:
    return current_user.get("role") == "super_admin" or current_user.get("tenant_id") == "super_admin"


async def get_garage_for_user(current_user: dict, garage_id_override: Optional[str] = None) -> dict:
    """Bãi đang thao tác. Nhân sự bãi chỉ chọn được bãi của tenant mình (chủ có thể có nhiều bãi);
    super_admin chọn được bất kỳ bãi nào qua garage_id."""
    if garage_id_override:
        oid = convert_mongo_object_id(garage_id_override)
        if not oid:
            raise HTTPException(status_code=400, detail="Invalid garage_id")
        garage = await GarageModel.collection.find_one({"_id": oid})
        if not garage:
            raise HTTPException(status_code=404, detail="Garage not found")
        if not _is_admin(current_user) and garage.get("tenant_id") != current_user.get("tenant_id"):
            raise HTTPException(status_code=403, detail="Access denied")
        return garage

    tenant_id = current_user.get("tenant_id")
    if not tenant_id or tenant_id == "super_admin":
        raise HTTPException(status_code=400, detail="Provide garage_id for super_admin access")
    if current_user.get("role") not in GARAGE_STAFF_ROLES:
        raise HTTPException(status_code=403, detail="Chỉ dành cho nhân sự bãi đỗ")

    garage = await GarageModel.collection.find_one(
        {"tenant_id": tenant_id, "status": {"$ne": "deleted"}}, sort=[("status", 1), ("name", 1)],
    )
    if not garage:
        raise HTTPException(status_code=404, detail="Tài khoản chưa có bãi đỗ")
    return garage


async def list_accessible_garages(current_user: dict, q: Optional[str] = None, limit: int = 50) -> list:
    """Danh sách bãi user được phép thao tác: bãi của tenant mình; super_admin xem được toàn mạng lưới."""
    query: dict = {"status": {"$ne": "deleted"}}
    if _is_admin(current_user):
        if q:
            import re
            query["name"] = {"$regex": re.escape(q.strip()[:50]), "$options": "i"}
    else:
        if current_user.get("role") not in GARAGE_STAFF_ROLES:
            raise HTTPException(status_code=403, detail="Chỉ dành cho nhân sự bãi đỗ")
        query["tenant_id"] = current_user.get("tenant_id")
    docs = await GarageModel.collection.find(query, {"name": 1, "address": 1, "status": 1, "lot_type": 1}) \
        .sort("name", 1).limit(limit).to_list(length=limit)
    return [{"id": str(d["_id"]), "name": d.get("name", ""), "district": (d.get("address") or {}).get("district", ""),
             "status": d.get("status"), "lot_type": d.get("lot_type")} for d in docs]


# ── Dashboard ────────────────────────────────────────────────────

async def get_dashboard_overview(garage: dict) -> dict:
    gid = garage["_id"]
    await sweep_overdue(garage_oid=gid)
    now = get_current_time()
    today = _local_day_start(now)
    yesterday = today - timedelta(days=1)

    availability = await get_availability(garage)
    inside = await BookingModel.collection.count_documents({"garage_id": gid, "status": "checked_in"})
    pending = await BookingModel.collection.count_documents({"garage_id": gid, "status": "pending"})

    upcoming_docs = await BookingModel.collection.find({
        "garage_id": gid, "status": {"$in": ["reserved", "pending"]},
        "start_time": {"$gte": now - timedelta(minutes=30), "$lte": now + timedelta(hours=2)},
    }).sort("start_time", 1).to_list(length=20)

    def _sum(docs):
        return sum(_revenue(b) for b in docs)

    out_today = await BookingModel.collection.find({
        "garage_id": gid, "status": "checked_out", "timestamps.checked_out_at": {"$gte": today},
    }, {"final_price": 1}).to_list(length=None)
    out_yday = await BookingModel.collection.find({
        "garage_id": gid, "status": "checked_out",
        "timestamps.checked_out_at": {"$gte": yesterday, "$lt": today},
    }, {"final_price": 1}).to_list(length=None)
    unpaid = await BookingModel.collection.count_documents({
        "garage_id": gid, "status": "checked_out", "payment_status": "unpaid",
    })

    # Lấp đầy 24 giờ qua theo snapshot
    snaps = await CapacitySnapshotModel.collection.find({
        "garage_id": gid, "timestamp": {"$gte": now - timedelta(hours=24)},
    }).sort("timestamp", 1).to_list(length=48)
    fill_24h = [{"time": to_local(s["timestamp"]).strftime("%H:00"),
                 "rate": round(float(s.get("occupancy_rate") or 0), 3)} for s in snaps]

    level = int(garage.get("integration_level") or 1)
    return {
        "garage": {
            "id": str(gid), "name": garage.get("name", ""), "status": garage.get("status"),
            "integration_level": level,
            "integration_label": INTEGRATION_LEVELS.get(level, {}).get("name", ""),
            "is_accepting_bookings": garage.get("is_accepting_bookings", True),
        },
        "availability": availability,
        "inside_count": inside,
        "pending_count": pending,
        "upcoming": await enrich_bookings(upcoming_docs),
        "revenue": {
            "today": _sum(out_today), "yesterday": _sum(out_yday),
            "sessions_today": len(out_today), "unpaid_count": unpaid,
        },
        "fill_24h": fill_24h,
    }


async def get_capacity_chart(garage: dict, range_str: str) -> dict:
    """24H: lấp đầy từng giờ hôm nay. 7D: trung bình theo giờ trong tuần (T2..CN)."""
    if (range_str or "24H").upper() == "7D":
        rates = await hourly_rates(garage)
        return {"range": "7D", "labels": [f"{r['hour']:02d}:00" for r in rates],
                "data": [round(r["rate"] * 100) for r in rates]}
    now = get_current_time()
    today = _local_day_start(now)
    snaps = await CapacitySnapshotModel.collection.find({
        "garage_id": garage["_id"], "timestamp": {"$gte": today},
    }).to_list(length=48)
    by_hour = {s.get("hour_of_day"): s for s in snaps}
    return {"range": "24H", "labels": [f"{h:02d}:00" for h in range(24)],
            "data": [round(float(by_hour[h]["occupancy_rate"]) * 100) if h in by_hour else None for h in range(24)]}


# ── Bookings (lượt đặt & vào/ra) ─────────────────────────────────

BOOKING_TABS = {
    "upcoming": {"status": "reserved"},
    "pending": {"status": "pending"},
    "inside": {"status": "checked_in"},
    "history": {"status": {"$in": ["checked_out", "cancelled", "rejected", "no_show", "expired"]}},
}


async def get_portal_bookings(garage: dict, tab: str, q: Optional[str], page: int, limit: int) -> dict:
    gid = garage["_id"]
    await sweep_overdue(garage_oid=gid)
    if tab not in BOOKING_TABS:
        tab = "upcoming"
    query: dict = {"garage_id": gid, **BOOKING_TABS[tab]}
    plate = normalize_plate(q)
    if plate:
        query["$or"] = [{"license_plate": {"$regex": plate}}, {"booking_code": {"$regex": plate}}]

    sort = [("start_time", 1)] if tab in ("upcoming", "pending") else [("start_time", -1)]
    if tab == "inside":
        sort = [("timestamps.checked_in_at", 1)]
    total = await BookingModel.collection.count_documents(query)
    docs = await BookingModel.collection.find(query).sort(sort).skip((page - 1) * limit).limit(limit).to_list(length=limit)
    items = await enrich_bookings(docs)

    # Ước tính tiền hiện tại cho xe đang trong bãi
    if tab == "inside":
        for item, d in zip(items, docs):
            item["current_charge"] = (await compute_final_price(d))["amount"]

    counts = {}
    for k, cond in BOOKING_TABS.items():
        if k == "history":
            continue
        counts[k] = await BookingModel.collection.count_documents({"garage_id": gid, **cond})

    return {
        "tab": tab,
        "counts": counts,
        "integration_level": int(garage.get("integration_level") or 1),
        "pagination": {"current_page": page, "total_pages": max(1, -(-total // limit)), "total_items": total},
        "items": items,
    }


# ── Analytics ────────────────────────────────────────────────────

async def get_analytics(garage: dict, range_str: str) -> dict:
    gid = garage["_id"]
    days = _parse_range_days(range_str)
    now = get_current_time()
    today = _local_day_start(now)
    start = today - timedelta(days=days - 1)
    prev_start = start - timedelta(days=days)

    docs = await BookingModel.collection.find({
        "garage_id": gid, "start_time": {"$gte": prev_start},
    }).to_list(length=50000)
    cur = [b for b in docs if b["start_time"] >= start]
    prev = [b for b in docs if b["start_time"] < start]

    def sessions(lst):
        return [b for b in lst if b.get("status") == "checked_out"]

    cur_s, prev_s = sessions(cur), sessions(prev)
    revenue = sum(_revenue(b) for b in cur_s)
    prev_revenue = sum(_revenue(b) for b in prev_s)

    def trend(a, b):
        if not b:
            return None
        return round((a - b) / b * 100, 1)

    # Doanh thu theo ngày
    by_day = defaultdict(int)
    for b in cur_s:
        ts = (b.get("timestamps") or {}).get("checked_out_at") or b["start_time"]
        by_day[to_local(ts).strftime("%Y-%m-%d")] += _revenue(b)
    labels, rev_data = [], []
    for i in range(days):
        d = to_local(start + timedelta(days=i))
        labels.append(d.strftime("%d/%m"))
        rev_data.append(by_day.get(d.strftime("%Y-%m-%d"), 0))

    # Thời lượng gửi trung bình (phút)
    durations = []
    for b in cur_s:
        t = b.get("timestamps") or {}
        if t.get("checked_in_at") and t.get("checked_out_at"):
            durations.append((t["checked_out_at"] - t["checked_in_at"]).total_seconds() / 60)
    avg_duration = round(sum(durations) / len(durations)) if durations else 0

    # Nguồn lượt
    src = Counter(b.get("source", "app") for b in cur_s)
    # Dịch vụ
    stype_map = await get_service_type_map()
    svc = Counter(b.get("service_type_code") for b in cur_s)
    services = [{"code": c, "name": stype_map.get(c, {}).get("name", c), "count": n,
                 "revenue": sum(_revenue(b) for b in cur_s if b.get("service_type_code") == c)}
                for c, n in svc.most_common()]

    # Trạng thái lượt đặt qua app
    app_bookings = [b for b in cur if b.get("source") != "walk_in"]
    status_counts = Counter(b.get("status") for b in app_bookings)

    # Lấp đầy theo giờ: ngày thường vs cuối tuần
    weekday = await hourly_rates(garage, day_of_week=2)
    weekend = await hourly_rates(garage, day_of_week=6)

    # Khách quay lại
    per_cust = Counter(str(b["customer_id"]) for b in cur_s if b.get("customer_id"))
    returning = sum(1 for n in per_cust.values() if n >= 2)

    return {
        "range": f"{days}D",
        "metrics": {
            "revenue": {"value": revenue, "trend": trend(revenue, prev_revenue)},
            "sessions": {"value": len(cur_s), "trend": trend(len(cur_s), len(prev_s))},
            "avg_duration_minutes": avg_duration,
            "avg_ticket": round(revenue / len(cur_s)) if cur_s else 0,
        },
        "revenue_chart": {"labels": labels, "data": rev_data},
        "source_split": {"app": src.get("app", 0) + src.get("matching", 0), "walk_in": src.get("walk_in", 0)},
        "services": services,
        "booking_status": dict(status_counts),
        "occupancy_by_hour": {
            "labels": [f"{h:02d}h" for h in range(24)],
            "weekday": [round(r["rate"] * 100) for r in weekday],
            "weekend": [round(r["rate"] * 100) for r in weekend],
        },
        "customers": {"total": len(per_cust), "returning": returning},
    }


# ── Quality / score ──────────────────────────────────────────────

def get_score_data(garage: dict) -> dict:
    stats = garage.get("stats") or {}
    level = int(garage.get("integration_level") or 1)
    assessment = garage.get("grade_assessment") or {}
    grade_info = compute_grade(assessment.get("items"))
    enough = int(stats.get("total_sessions") or 0) >= MIN_SESSIONS_FOR_SCORE

    tips = []
    if enough:
        if float(stats.get("fulfillment_rate") or 0) < 0.95:
            tips.append("Tỉ lệ giữ đúng chỗ dưới 95%. Hạn chế huỷ lượt đã xác nhận, cập nhật chỗ trống thường xuyên hơn.")
        if int(stats.get("complaint_count") or 0) > 0:
            tips.append(f"Có {stats.get('complaint_count')} lượt khiếu nại / đánh giá thấp. Xem lại phản hồi của khách trong mục Lượt đặt.")
        if float(stats.get("return_rate") or 0) < 0.3:
            tips.append("Tỉ lệ khách quay lại thấp. Cân nhắc gói ngày làm việc hoặc gói tháng cho khách quen.")
    else:
        tips.append(f"Cần ít nhất {MIN_SESSIONS_FOR_SCORE} lượt gửi hoàn tất để tính điểm chất lượng.")
    if level < 3:
        tips.append("Nâng cấp tích hợp lên cấp 3 để lượt đặt được tự xác nhận và hiển thị \"Thời gian thực\".")
    missing = [c for c in GRADE_CHECKLIST if not (assessment.get("items") or {}).get(c["key"])]
    missing.sort(key=lambda c: -c["points"])
    if missing:
        tips.append("Tiêu chí kiểm định chưa đạt nhiều điểm nhất: " + ", ".join(c["label"] for c in missing[:3]) + ".")

    return {
        "quality_score": float(garage.get("quality_score") or 0),
        "has_enough_data": enough,
        "stats": stats,
        "integration": {"level": level, **INTEGRATION_LEVELS.get(level, {})},
        "grade": {
            "stars": int(garage.get("grade") or grade_info["grade"]),
            "score": int(garage.get("grade_score") or grade_info["score"]),
            "groups": [{"key": k, "label": GRADE_GROUPS[k], **v} for k, v in grade_info["groups"].items()],
            "items": [{**c, "passed": bool((assessment.get("items") or {}).get(c["key"]))} for c in GRADE_CHECKLIST],
            "assessed_at": assessment.get("assessed_at").isoformat() if isinstance(assessment.get("assessed_at"), datetime) else None,
            "note": assessment.get("note", ""),
        },
        "badges": compute_badges(garage),
        "next_inspection_at": garage["next_inspection_at"].isoformat() if isinstance(garage.get("next_inspection_at"), datetime) else None,
        "tips": tips,
    }


# ── Services Overview ────────────────────────────────────────────

def _portal_service_item(doc: dict, stype: Optional[dict], tags: Optional[list] = None, bookings: int = 0) -> dict:
    code = doc.get("service_type_code", "")
    st = stype or {}
    return {
        "id": str(doc.get("_id") or doc.get("id") or ""),
        "service_type_code": code,
        "name": st.get("name", code),
        "description": st.get("description", ""),
        "category": st.get("category", "parking"),
        "unit": st.get("unit", "hour"),
        "icon": st.get("icon", "clock"),
        "price_vnd": int(doc.get("price", 0)),
        "pricing": resolve_pricing(doc),
        "note": doc.get("note", ""),
        "bookings_30d": bookings,
        "tags": tags or [],
    }


async def get_services_overview(garage: dict) -> dict:
    garage_oid = garage["_id"]

    services_docs = await GarageServiceModel.collection.find({
        "garage_id": garage_oid, "is_available": True,
    }).to_list(length=100)
    stype_map = await get_service_type_map()

    # Số lượt đặt 30 ngày theo dịch vụ
    since = get_current_time() - timedelta(days=30)
    svc_counts = Counter()
    for b in await BookingModel.collection.find(
        {"garage_id": garage_oid, "created_at": {"$gte": since}},
        {"service_type_code": 1},
    ).to_list(length=20000):
        svc_counts[b.get("service_type_code", "")] += 1
    most_popular_code = svc_counts.most_common(1)[0][0] if svc_counts else ""

    services = []
    for d in sorted(services_docs, key=lambda x: stype_map.get(x.get("service_type_code"), {}).get("sort_order", 999)):
        code = d.get("service_type_code", "")
        tags = ["Đặt nhiều nhất"] if code == most_popular_code else []
        services.append(_portal_service_item(d, stype_map.get(code), tags, svc_counts.get(code, 0)))

    offered = {d.get("service_type_code") for d in services_docs}
    available_types = [st for code, st in stype_map.items() if st.get("is_active") and code not in offered]
    available_types.sort(key=lambda s: s.get("sort_order", 999))

    return {
        "stats": {
            "active_services": len(services),
            "bookings_30d": sum(svc_counts.values()),
            "top_service": stype_map.get(most_popular_code, {}).get("name", "") if most_popular_code else "",
        },
        "services": services,
        "available_types": available_types,
    }


# ── Service CRUD helpers ─────────────────────────────────────────

async def create_portal_service(
    garage: dict,
    service_type_code: str,
    price: Optional[int],
    duration_minutes: Optional[int],
    current_user: dict,
    pricing: Optional[dict] = None,
    note: Optional[str] = None,
) -> dict:
    stype = await get_service_type_by_code(service_type_code)
    if not stype:
        raise HTTPException(status_code=404, detail=f"Không có dịch vụ '{service_type_code}' trong danh mục")

    result = await upsert_garage_service(
        garage_id=str(garage["_id"]),
        service_type_code=service_type_code,
        price=price,
        estimated_duration_minutes=duration_minutes,
        current_user=current_user,
        pricing=pricing,
        note=note,
    )
    return _portal_service_item(result, stype)


async def update_portal_service(
    service_id: str,
    price: Optional[int],
    duration_minutes: Optional[int],
    current_user: dict,
    pricing: Optional[dict] = None,
    note: Optional[str] = None,
) -> dict:
    oid = convert_mongo_object_id(service_id)
    if not oid:
        raise HTTPException(status_code=400, detail="Invalid service ID")
    doc = await GarageServiceModel.collection.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Service not found")
    if (current_user.get("tenant_id") != "super_admin" and
            doc.get("tenant_id") != current_user.get("tenant_id")):
        raise HTTPException(status_code=403, detail="Access denied")

    result = await upsert_garage_service(
        garage_id=str(doc["garage_id"]),
        service_type_code=doc["service_type_code"],
        price=price,
        estimated_duration_minutes=duration_minutes,
        current_user=current_user,
        pricing=pricing,
        note=note,
    )
    stype = await get_service_type_by_code(doc["service_type_code"])
    return _portal_service_item(result, stype)


async def delete_portal_service(service_id: str, current_user: dict) -> bool:
    oid = convert_mongo_object_id(service_id)
    if not oid:
        raise HTTPException(status_code=400, detail="Invalid service ID")
    doc = await GarageServiceModel.collection.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Service not found")
    if (current_user.get("tenant_id") != "super_admin" and
            doc.get("tenant_id") != current_user.get("tenant_id")):
        raise HTTPException(status_code=403, detail="Access denied")

    now = get_current_time()
    await GarageServiceModel.collection.update_one(
        {"_id": oid},
        {"$set": {"is_available": False, "updated_at": now, "updated_by": current_user.get("username", "")}},
    )

    # Remove from garage.services_offered if no other active service of same type remains
    garage_oid = doc.get("garage_id")
    code = doc.get("service_type_code", "")
    still_active = await GarageServiceModel.collection.find_one({
        "garage_id": garage_oid,
        "service_type_code": code,
        "is_available": True,
        "_id": {"$ne": oid},
    })
    if not still_active and garage_oid:
        await GarageModel.collection.update_one(
            {"_id": garage_oid}, {"$pull": {"services_offered": code}}
        )
    return True
