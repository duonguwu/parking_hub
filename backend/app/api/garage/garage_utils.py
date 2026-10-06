# -*- coding: utf-8 -*-
"""Garage Utils — hồ sơ bãi, tìm kiếm/lọc trên bản đồ, cập nhật hồ sơ."""
import logging
from typing import List, Dict, Any, Optional

from fastapi import HTTPException

from app.api.garage.garage_models import GarageModel
from app.api.garage.garage_classification_utils import (
    LOT_TYPES, INTEGRATION_LEVELS, compute_badges,
)
from app.api.garage_service.garage_service_models import GarageServiceModel
from app.api.capacity.capacity_utils import active_holds, availability_of
from app.api.shared.tool.datetime_convert import get_current_time
from app.api.shared.tool.convert_object_id import convert_mongo_object_id

logger = logging.getLogger(__name__)

COVERED = ("basement", "full_roof")


def _latlng(point: Optional[dict]) -> Optional[Dict[str, float]]:
    coords = (point or {}).get("coordinates")
    if not coords or len(coords) < 2:
        return None
    return {"lat": coords[1], "lng": coords[0]}


def _iso(v):
    return v.isoformat() if hasattr(v, "isoformat") else v


def format_garage(doc, availability: Optional[dict] = None) -> dict:
    """Hồ sơ đầy đủ của bãi."""
    data = doc if isinstance(doc, dict) else doc.dump()
    lot_type = data.get("lot_type", "outdoor_commercial")
    level = int(data.get("integration_level") or 1)
    return {
        "id": str(data.get("_id") or data.get("id") or ""),
        "tenant_id": data.get("tenant_id", ""),
        "name": data.get("name", ""),
        "slug": data.get("slug", ""),
        "location": data.get("location", {}),
        "position": _latlng(data.get("location")),
        "entrance": _latlng(data.get("entrance_location")),
        "address": data.get("address", {}),
        "lot_type": lot_type,
        "lot_type_label": LOT_TYPES.get(lot_type, lot_type),
        "integration_level": level,
        "integration_label": INTEGRATION_LEVELS.get(level, {}).get("name", ""),
        "grade": int(data.get("grade") or 1),
        "grade_score": int(data.get("grade_score") or 0),
        "grade_assessment": {
            **(data.get("grade_assessment") or {}),
            "assessed_at": _iso((data.get("grade_assessment") or {}).get("assessed_at")),
        },
        "quality_score": float(data.get("quality_score") or 0),
        "next_inspection_at": _iso(data.get("next_inspection_at")),
        "capacity": data.get("capacity", {}),
        "attributes": data.get("attributes", {}),
        "occupancy": {**(data.get("occupancy") or {}),
                      "updated_at": _iso((data.get("occupancy") or {}).get("updated_at"))},
        "availability": availability,
        "operating_hours": data.get("operating_hours", {}),
        "services_offered": data.get("services_offered", []),
        "description": data.get("description", ""),
        "photos": data.get("photos", []),
        "contacts": data.get("contacts", {}),
        "status": data.get("status", ""),
        "is_verified": data.get("is_verified", False),
        "is_accepting_bookings": data.get("is_accepting_bookings", True),
        "stats": data.get("stats", {}),
        "badges": compute_badges(data),
        "created_at": _iso(data.get("created_at")),
    }


def format_garage_card(data: dict, availability: dict, hourly_price: Optional[int] = None,
                       distance_km: Optional[float] = None) -> dict:
    """Thẻ tóm tắt cho bản đồ / danh sách."""
    a = data.get("attributes") or {}
    lot_type = data.get("lot_type", "outdoor_commercial")
    return {
        "id": str(data["_id"]),
        "name": data.get("name", ""),
        "position": _latlng(data.get("location")),
        "address": ", ".join(x for x in [(data.get("address") or {}).get("street"),
                                         (data.get("address") or {}).get("district")] if x),
        "district": (data.get("address") or {}).get("district", ""),
        "lot_type": lot_type,
        "lot_type_label": LOT_TYPES.get(lot_type, lot_type),
        "integration_level": int(data.get("integration_level") or 1),
        "grade": int(data.get("grade") or 1),
        "quality_score": float(data.get("quality_score") or 0),
        "cover": a.get("cover", "open"),
        "max_height_m": a.get("max_height_m"),
        "ev_count": (a.get("ev_chargers") or {}).get("count", 0),
        "guard": a.get("guard", "none"),
        "flood_risk": a.get("flood_risk", "none"),
        "is_24h": bool((data.get("operating_hours") or {}).get("is_24h")),
        "hourly_price": hourly_price,
        "distance_km": distance_km,
        "availability": availability,
        "badges": compute_badges(data),
        "status": data.get("status", ""),
        "is_accepting_bookings": data.get("is_accepting_bookings", True),
    }


async def hourly_prices(garage_ids: list) -> Dict[Any, int]:
    if not garage_ids:
        return {}
    cur = GarageServiceModel.collection.find(
        {"garage_id": {"$in": garage_ids}, "service_type_code": "park_hourly", "is_available": True},
        {"garage_id": 1, "price": 1},
    )
    return {d["garage_id"]: int(d.get("price") or 0) async for d in cur}


async def search_garages(
    lat: Optional[float] = None, lng: Optional[float] = None, radius_km: float = 5,
    lot_types: Optional[List[str]] = None, covered: bool = False, ev: bool = False,
    min_height_m: Optional[float] = None, guard_24h: bool = False, no_flood: bool = False,
    min_grade: int = 1, min_level: int = 1, max_hourly_price: Optional[int] = None,
    service_type: Optional[str] = None, only_available: bool = False, is_24h: bool = False,
    statuses: Optional[List[str]] = None, q: Optional[str] = None, limit: int = 300,
) -> List[dict]:
    """Tìm bãi theo vị trí + bộ lọc. Không có toạ độ → toàn mạng lưới (dùng cho admin)."""
    query: Dict[str, Any] = {"status": {"$in": statuses or ["active"]}}
    if lot_types:
        query["lot_type"] = {"$in": lot_types}
    if covered:
        query["attributes.cover"] = {"$in": list(COVERED)}
    if ev:
        query["attributes.ev_chargers.count"] = {"$gt": 0}
    if min_height_m:
        query["$or"] = [{"attributes.max_height_m": {"$gte": min_height_m}}, {"attributes.cover": "open"}]
    if guard_24h:
        query["attributes.guard"] = "24h"
    if no_flood:
        query["attributes.flood_risk"] = "none"
    if min_grade > 1:
        query["grade"] = {"$gte": min_grade}
    if min_level > 1:
        query["integration_level"] = {"$gte": min_level}
    if service_type:
        query["services_offered"] = service_type
    if is_24h:
        query["operating_hours.is_24h"] = True
    if q:
        query["name"] = {"$regex": q.strip()[:50], "$options": "i"}

    try:
        if lat is not None and lng is not None:
            pipeline = [
                {"$geoNear": {
                    "near": {"type": "Point", "coordinates": [lng, lat]},
                    "distanceField": "distance_meters",
                    "maxDistance": radius_km * 1000,
                    "spherical": True,
                    "query": query,
                }},
                {"$limit": limit},
            ]
            docs = [d async for d in GarageModel.collection.aggregate(pipeline)]
        else:
            docs = await GarageModel.collection.find(query).limit(limit).to_list(length=limit)
    except Exception as e:
        logger.error(f"Error searching garages: {e}")
        raise HTTPException(status_code=500, detail="Failed to search garages")

    ids = [d["_id"] for d in docs]
    holds = await active_holds(ids)
    prices = await hourly_prices(ids)
    cards = []
    for d in docs:
        avail = availability_of(d, holds.get(d["_id"], 0))
        price = prices.get(d["_id"])
        if max_hourly_price and (price is None or price > max_hourly_price):
            continue
        if only_available and avail["status"] in ("full",):
            continue
        dist = round(d["distance_meters"] / 1000, 2) if "distance_meters" in d else None
        cards.append(format_garage_card(d, avail, price, dist))
    return cards


async def get_garage_detail(garage_id: str) -> dict:
    oid = convert_mongo_object_id(garage_id)
    if not oid:
        raise HTTPException(status_code=400, detail="Invalid garage ID format")
    doc = await GarageModel.collection.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Garage not found")
    holds = await active_holds([oid])
    return format_garage(doc, availability_of(doc, holds.get(oid, 0)))


async def get_all_garages(current_user: dict, status_filter: str = "active", limit: int = 50) -> List[dict]:
    """Get all garages (tenant-filtered)."""
    filter_dict = {"status": status_filter} if status_filter else {}
    cursor = GarageModel.find(filter_dict, current_user=current_user)
    docs = await cursor.to_list(length=limit)
    return [format_garage(doc) for doc in docs]


async def get_garage_by_id(garage_id: str, current_user: dict) -> dict:
    oid = convert_mongo_object_id(garage_id)
    if not oid:
        raise HTTPException(status_code=400, detail="Invalid garage ID format")
    doc = await GarageModel.find_one({"_id": oid}, current_user=current_user)
    if not doc:
        raise HTTPException(status_code=404, detail="Garage not found")
    return format_garage(doc)


# ── Cập nhật hồ sơ (chủ bãi) ─────────────────────────────────────

# Chủ bãi được sửa các trường này. Cấp tích hợp, hạng sao, trạng thái do admin đặt.
OWNER_EDITABLE = {"name", "description", "address", "contacts", "operating_hours",
                  "is_accepting_bookings", "photos", "lot_type"}
CAPACITY_KEYS = {"total_spots", "walk_in_spots", "monthly_spots", "reservable_ratio", "grace_minutes"}
ATTRIBUTE_KEYS = {"cover", "max_height_m", "guard", "guard_hours", "cctv", "ev_chargers", "flood_risk",
                  "parking_style", "vehicle_types", "large_vehicle_ok", "lighting", "surface",
                  "fire_safety", "restroom", "payment_methods"}


def build_profile_update(data: dict) -> dict:
    """Chuẩn hoá payload sửa hồ sơ thành $set (dot-path cho capacity/attributes)."""
    upd: Dict[str, Any] = {}
    for k in OWNER_EDITABLE:
        if k in data and data[k] is not None:
            if k == "lot_type" and data[k] not in LOT_TYPES:
                raise HTTPException(status_code=422, detail="Loại hình bãi không hợp lệ")
            upd[k] = data[k]
    cap = data.get("capacity") or {}
    for k, v in cap.items():
        if k in CAPACITY_KEYS and v is not None:
            upd[f"capacity.{k}"] = v
    if "capacity.total_spots" in upd:
        total = int(upd["capacity.total_spots"])
        if total < 1 or total > 5000:
            raise HTTPException(status_code=422, detail="Tổng số chỗ phải từ 1 đến 5000")
    if "capacity.reservable_ratio" in upd and not 0 <= float(upd["capacity.reservable_ratio"]) <= 1:
        raise HTTPException(status_code=422, detail="Tỉ lệ cho giữ trước phải từ 0 đến 1")
    for k, v in (data.get("attributes") or {}).items():
        if k in ATTRIBUTE_KEYS:
            upd[f"attributes.{k}"] = v
    if data.get("entrance"):
        e = data["entrance"]
        upd["entrance_location"] = {"type": "Point", "coordinates": [float(e["lng"]), float(e["lat"])]}
    return upd


async def update_garage_profile(garage: dict, data: dict, current_user: dict) -> dict:
    if (current_user.get("tenant_id") != "super_admin" and
            garage.get("tenant_id") != current_user.get("tenant_id")):
        raise HTTPException(status_code=403, detail="Không phải bãi của bạn")
    upd = build_profile_update(data)
    if not upd:
        raise HTTPException(status_code=422, detail="Không có thay đổi")
    upd["updated_at"] = get_current_time()
    upd["updated_by"] = current_user.get("username", "")
    await GarageModel.collection.update_one({"_id": garage["_id"]}, {"$set": upd})
    return await get_garage_detail(str(garage["_id"]))


async def update_garage(garage_id: str, update_data: dict, current_user: dict) -> dict:
    oid = convert_mongo_object_id(garage_id)
    if not oid:
        raise HTTPException(status_code=400, detail="Invalid garage ID")
    garage = await GarageModel.collection.find_one({"_id": oid})
    if not garage:
        raise HTTPException(status_code=404, detail="Garage not found")
    return await update_garage_profile(garage, update_data, current_user)
