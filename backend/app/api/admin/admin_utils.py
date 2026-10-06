# -*- coding: utf-8 -*-
"""Admin utils — quản trị mạng lưới bãi đỗ, người dùng, danh mục dịch vụ."""
import logging
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException

from app.api.booking.booking_models import BookingModel
from app.api.capacity.capacity_utils import active_holds, availability_of
from app.api.garage.garage_models import GarageModel
from app.api.garage.garage_classification_utils import (
    LOT_TYPES, INTEGRATION_LEVELS, compute_grade, sanitize_checklist, suggest_checklist,
)
from app.api.garage.garage_utils import format_garage, format_garage_card, hourly_prices
from app.api.garage_service.pricing_utils import normalize_pricing, to_local, LOCAL_TZ
from app.api.service_type.service_type_models import ServiceTypeModel, SERVICE_CATEGORIES, SERVICE_UNITS
from app.api.service_type.service_type_utils import format_service_type, get_all_service_types
from app.api.tenant.tenant_models import TenantModel
from app.api.user.user_models import UserModel
from app.api.shared.tool.convert_object_id import convert_mongo_object_id
from app.api.shared.tool.datetime_convert import get_current_time

logger = logging.getLogger(__name__)

ADMIN_ROLES = ("super_admin", "platform_ops")
INSPECTION_INTERVAL_DAYS = 180


def _iso(v):
    return v.isoformat() if isinstance(v, datetime) else v


# ── Tổng quan ────────────────────────────────────────────────────

async def get_overview() -> dict:
    now = get_current_time()
    local = to_local(now)
    today = LOCAL_TZ.localize(datetime(local.year, local.month, local.day))
    since = today - timedelta(days=29)

    garages = await GarageModel.collection.find(
        {}, {"status": 1, "integration_level": 1, "lot_type": 1, "grade": 1, "address": 1,
             "capacity": 1, "occupancy": 1, "name": 1, "stats": 1, "quality_score": 1},
    ).to_list(length=10000)
    active = [g for g in garages if g.get("status") == "active"]
    holds = await active_holds([g["_id"] for g in active])

    total_spots = 0
    tracked_total = tracked_used = 0
    for g in active:
        a = availability_of(g, holds.get(g["_id"], 0))
        total_spots += a["total_spots"]
        if a["has_data"]:
            tracked_total += a["total_spots"]
            tracked_used += a["total_spots"] - (a["available"] or 0)

    by_district = Counter(((g.get("address") or {}).get("district") or "Khác") for g in active)
    by_level = Counter(int(g.get("integration_level") or 1) for g in active)
    by_type = Counter(g.get("lot_type", "outdoor_commercial") for g in active)
    by_grade = Counter(int(g.get("grade") or 1) for g in active)

    bookings = await BookingModel.collection.find(
        {"start_time": {"$gte": since}},
        {"status": 1, "final_price": 1, "start_time": 1, "source": 1, "garage_id": 1},
    ).to_list(length=200000)
    daily = defaultdict(lambda: {"bookings": 0, "revenue": 0})
    for b in bookings:
        key = to_local(b["start_time"]).strftime("%Y-%m-%d")
        if b.get("source") != "walk_in":
            daily[key]["bookings"] += 1
        if b.get("status") == "checked_out":
            daily[key]["revenue"] += int(b.get("final_price") or 0)
    chart = []
    for i in range(30):
        d = to_local(since + timedelta(days=i)).strftime("%Y-%m-%d")
        chart.append({"date": d[8:10] + "/" + d[5:7], **daily[d]})

    sessions = Counter(b["garage_id"] for b in bookings if b.get("status") == "checked_out")
    names = {g["_id"]: g.get("name", "") for g in garages}
    top = [{"id": str(gid), "name": names.get(gid, ""), "sessions": n} for gid, n in sessions.most_common(5)]

    roles = Counter()
    async for u in UserModel.collection.aggregate([{"$group": {"_id": "$role", "n": {"$sum": 1}}}]):
        roles[u["_id"]] = u["n"]

    app_bookings = [b for b in bookings if b.get("source") != "walk_in"]
    statuses = Counter(b.get("status") for b in app_bookings)
    return {
        "garages": {
            "total": len(garages), "active": len(active),
            "pending_review": sum(1 for g in garages if g.get("status") == "pending_review"),
            "suspended": sum(1 for g in garages if g.get("status") == "suspended"),
        },
        "spots": {
            "total": total_spots,
            "network_occupancy": round(tracked_used / tracked_total, 3) if tracked_total else None,
            "tracked_lots": sum(1 for g in active if int(g.get("integration_level") or 1) >= 2),
        },
        "bookings_30d": len(app_bookings),
        "revenue_30d": sum(int(b.get("final_price") or 0) for b in bookings if b.get("status") == "checked_out"),
        "fulfillment_30d": round(
            (statuses.get("checked_in", 0) + statuses.get("checked_out", 0)) /
            max(1, statuses.get("checked_in", 0) + statuses.get("checked_out", 0) + statuses.get("no_show", 0)), 3),
        "by_district": [{"name": k, "count": v} for k, v in by_district.most_common()],
        "by_level": [{"level": k, "label": INTEGRATION_LEVELS[k]["name"], "count": by_level.get(k, 0)} for k in (1, 2, 3, 4)],
        "by_type": [{"code": k, "label": LOT_TYPES.get(k, k), "count": v} for k, v in by_type.most_common()],
        "by_grade": [{"grade": k, "count": by_grade.get(k, 0)} for k in (1, 2, 3, 4, 5)],
        "daily": chart,
        "top_garages": top,
        "users": dict(roles),
    }


# ── Bãi đỗ ───────────────────────────────────────────────────────

def _garage_query(status: Optional[str], level: Optional[int], lot_type: Optional[str],
                  district: Optional[str], q: Optional[str]) -> dict:
    query: dict = {}
    if status:
        query["status"] = status
    if level:
        query["integration_level"] = level
    if lot_type:
        query["lot_type"] = lot_type
    if district:
        query["address.district"] = district
    if q:
        rx = {"$regex": re.escape(q.strip()[:50]), "$options": "i"}
        query["$or"] = [{"name": rx}, {"address.street": rx}, {"tenant_id": rx}]
    return query


async def list_garages(status=None, level=None, lot_type=None, district=None, q=None,
                       page: int = 1, limit: int = 20) -> dict:
    query = _garage_query(status, level, lot_type, district, q)
    total = await GarageModel.collection.count_documents(query)
    docs = await GarageModel.collection.find(query).sort([("status", -1), ("name", 1)]) \
        .skip((page - 1) * limit).limit(limit).to_list(length=limit)
    ids = [d["_id"] for d in docs]
    holds = await active_holds(ids)
    prices = await hourly_prices(ids)
    items = []
    for d in docs:
        card = format_garage_card(d, availability_of(d, holds.get(d["_id"], 0)), prices.get(d["_id"]))
        card.update({
            "tenant_id": d.get("tenant_id"),
            "grade_score": int(d.get("grade_score") or 0),
            "is_verified": d.get("is_verified", False),
            "total_spots": int((d.get("capacity") or {}).get("total_spots") or 0),
            "next_inspection_at": _iso(d.get("next_inspection_at")),
            "created_at": _iso(d.get("created_at")),
        })
        items.append(card)
    districts = sorted(x for x in await GarageModel.collection.distinct("address.district") if x)
    return {
        "items": items,
        "pagination": {"current_page": page, "total_pages": max(1, -(-total // limit)), "total_items": total},
        "districts": districts,
    }


async def network_map(status: Optional[str] = None, level: Optional[int] = None) -> list:
    query = _garage_query(status, level, None, None, None)
    docs = await GarageModel.collection.find(query).to_list(length=5000)
    holds = await active_holds([d["_id"] for d in docs])
    prices = await hourly_prices([d["_id"] for d in docs])
    return [format_garage_card(d, availability_of(d, holds.get(d["_id"], 0)), prices.get(d["_id"])) for d in docs]


async def _get(garage_id: str) -> dict:
    oid = convert_mongo_object_id(garage_id)
    if not oid:
        raise HTTPException(status_code=400, detail="Invalid garage id")
    g = await GarageModel.collection.find_one({"_id": oid})
    if not g:
        raise HTTPException(status_code=404, detail="Garage not found")
    return g


async def get_garage_admin(garage_id: str) -> dict:
    g = await _get(garage_id)
    holds = await active_holds([g["_id"]])
    owner = await UserModel.collection.find_one(
        {"tenant_id": g.get("tenant_id"), "role": "garage_owner"}, {"name": 1, "email": 1, "phone": 1, "username": 1},
    )
    tenant = await TenantModel.collection.find_one({"slug": g.get("tenant_id")}, {"name": 1, "status": 1})
    return {
        "garage": format_garage(g, availability_of(g, holds.get(g["_id"], 0))),
        "suggested_checklist": suggest_checklist(g),
        "grade_preview": compute_grade((g.get("grade_assessment") or {}).get("items")),
        "owner": {k: owner.get(k, "") for k in ("name", "email", "phone", "username")} if owner else None,
        "tenant": {"name": tenant.get("name", ""), "status": tenant.get("status", "")} if tenant else None,
    }


async def update_garage_admin(garage_id: str, data: dict, current_user: dict) -> dict:
    g = await _get(garage_id)
    upd: dict = {}
    if data.get("status") is not None:
        if data["status"] not in ("pending_review", "active", "suspended"):
            raise HTTPException(status_code=422, detail="Trạng thái không hợp lệ")
        upd["status"] = data["status"]
    if data.get("integration_level") is not None:
        lvl = int(data["integration_level"])
        if lvl not in INTEGRATION_LEVELS:
            raise HTTPException(status_code=422, detail="Cấp tích hợp phải từ 1 đến 4")
        upd["integration_level"] = lvl
        if lvl >= 3:
            upd["occupancy.source"] = "simulated"
            if not (g.get("occupancy") or {}).get("updated_at"):
                upd["occupancy.updated_at"] = get_current_time()
    if data.get("is_verified") is not None:
        upd["is_verified"] = bool(data["is_verified"])
    if data.get("is_accepting_bookings") is not None:
        upd["is_accepting_bookings"] = bool(data["is_accepting_bookings"])
    if not upd:
        raise HTTPException(status_code=422, detail="Không có thay đổi")
    upd["updated_at"] = get_current_time()
    upd["updated_by"] = current_user.get("username", "")
    await GarageModel.collection.update_one({"_id": g["_id"]}, {"$set": upd})
    return await get_garage_admin(garage_id)


async def save_assessment(garage_id: str, items: dict, note: str, current_user: dict) -> dict:
    """Lưu kết quả kiểm định → tính hạng sao, đánh dấu đã kiểm định, hẹn lần kế tiếp."""
    g = await _get(garage_id)
    clean = sanitize_checklist(items)
    result = compute_grade(clean)
    now = get_current_time()
    await GarageModel.collection.update_one({"_id": g["_id"]}, {"$set": {
        "grade_assessment": {"items": clean, "note": note or "", "assessed_at": now,
                             "assessed_by": current_user.get("username", "")},
        "grade": result["grade"],
        "grade_score": result["score"],
        "is_verified": True,
        "next_inspection_at": now + timedelta(days=INSPECTION_INTERVAL_DAYS),
        "updated_at": now,
        "updated_by": current_user.get("username", ""),
    }})
    return await get_garage_admin(garage_id)


# ── Người dùng ───────────────────────────────────────────────────

async def list_users(role: Optional[str], q: Optional[str], page: int, limit: int) -> dict:
    query: dict = {}
    if role:
        query["role"] = role
    if q:
        rx = {"$regex": re.escape(q.strip()[:50]), "$options": "i"}
        query["$or"] = [{"username": rx}, {"name": rx}, {"email": rx}, {"phone": rx}]
    total = await UserModel.collection.count_documents(query)
    docs = await UserModel.collection.find(query, {"password_hash": 0}).sort("created_at", -1) \
        .skip((page - 1) * limit).limit(limit).to_list(length=limit)
    tenant_ids = list({d.get("tenant_id") for d in docs if d.get("tenant_id")})
    garages = {g["tenant_id"]: g.get("name", "") async for g in GarageModel.collection.find(
        {"tenant_id": {"$in": tenant_ids}}, {"tenant_id": 1, "name": 1})}
    items = [{
        "id": str(d["_id"]), "username": d.get("username", ""), "name": d.get("name", ""),
        "email": d.get("email", ""), "phone": d.get("phone", ""), "role": d.get("role", ""),
        "tenant_id": d.get("tenant_id"), "garage_name": garages.get(d.get("tenant_id"), ""),
        "is_active": d.get("is_active", True), "created_at": _iso(d.get("created_at")),
    } for d in docs]
    return {"items": items,
            "pagination": {"current_page": page, "total_pages": max(1, -(-total // limit)), "total_items": total}}


async def set_user_active(user_id: str, is_active: bool, current_user: dict) -> dict:
    oid = convert_mongo_object_id(user_id)
    if not oid:
        raise HTTPException(status_code=400, detail="Invalid user id")
    u = await UserModel.collection.find_one({"_id": oid})
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    if u.get("role") == "super_admin":
        raise HTTPException(status_code=403, detail="Không thể khoá tài khoản super admin")
    await UserModel.collection.update_one({"_id": oid}, {"$set": {
        "is_active": bool(is_active), "updated_at": get_current_time(),
        "updated_by": current_user.get("username", ""),
    }})
    return {"id": user_id, "is_active": bool(is_active)}


# ── Danh mục dịch vụ ─────────────────────────────────────────────

SERVICE_TYPE_FIELDS = {"name", "description", "category", "unit", "icon", "base_price_min", "base_price_max",
                       "estimated_duration_minutes", "default_pricing", "is_popular", "sort_order", "is_active"}


def _clean_service_type(data: dict) -> dict:
    out = {k: v for k, v in data.items() if k in SERVICE_TYPE_FIELDS and v is not None}
    if "category" in out and out["category"] not in SERVICE_CATEGORIES:
        raise HTTPException(status_code=422, detail="Nhóm dịch vụ không hợp lệ")
    if "unit" in out and out["unit"] not in SERVICE_UNITS:
        raise HTTPException(status_code=422, detail="Đơn vị không hợp lệ")
    if "default_pricing" in out:
        out["default_pricing"] = normalize_pricing(out["default_pricing"])
    return out


async def list_service_types_admin() -> list:
    return await get_all_service_types(active_only=False)


async def create_service_type(data: dict, current_user: dict) -> dict:
    code = (data.get("code") or "").strip().lower()
    if not re.fullmatch(r"[a-z][a-z0-9_]{2,40}", code):
        raise HTTPException(status_code=422, detail="Mã dịch vụ chỉ gồm chữ thường, số, gạch dưới")
    if await ServiceTypeModel.collection.find_one({"code": code}):
        raise HTTPException(status_code=409, detail="Mã dịch vụ đã tồn tại")
    now = get_current_time()
    doc = {
        "code": code, "tenant_id": "platform", "is_active": True, "is_popular": False, "sort_order": 100,
        "category": "addon", "unit": "session", "icon": "clock", "description": "",
        "base_price_min": 0, "base_price_max": 0, "estimated_duration_minutes": 60,
        "default_pricing": {"mode": "flat", "flat_price": 0, "peak_rules": []},
        **_clean_service_type(data),
        "created_at": now, "updated_at": now,
        "created_by": current_user.get("username", ""), "updated_by": current_user.get("username", ""),
    }
    if not doc.get("name"):
        raise HTTPException(status_code=422, detail="Cần tên dịch vụ")
    await ServiceTypeModel.collection.insert_one(doc)
    return format_service_type(await ServiceTypeModel.collection.find_one({"code": code}))


async def update_service_type(code: str, data: dict, current_user: dict) -> dict:
    upd = _clean_service_type(data)
    if not upd:
        raise HTTPException(status_code=422, detail="Không có thay đổi")
    upd.update({"updated_at": get_current_time(), "updated_by": current_user.get("username", "")})
    res = await ServiceTypeModel.collection.update_one({"code": code}, {"$set": upd})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Service type not found")
    return format_service_type(await ServiceTypeModel.collection.find_one({"code": code}))
