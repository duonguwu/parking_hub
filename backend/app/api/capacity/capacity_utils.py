# -*- coding: utf-8 -*-
"""
Capacity — chỗ trống realtime, snapshot theo giờ, dự đoán theo lịch sử cùng giờ/thứ.

Khái niệm:
  occupied   xe đang ở trong bãi (chủ bãi cập nhật tay / check-in / dữ liệu giả lập)
  held       chỗ đang giữ cho lượt đặt `reserved` sắp tới (trong 30' trước giờ hẹn → hết grace)
  available  total_spots − occupied − held
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Iterable, List, Optional

from bson import ObjectId
from fastapi import HTTPException

from app.api.capacity.capacity_models import CapacitySnapshotModel
from app.api.capacity.occupancy_profile_utils import occupancy_profile
from app.api.booking.booking_models import BookingModel
from app.api.garage.garage_models import GarageModel
from app.api.garage_service.pricing_utils import to_local
from app.api.shared.tool.datetime_convert import get_current_time
from app.api.shared.tool.convert_object_id import convert_mongo_object_id

logger = logging.getLogger(__name__)

HOLD_BEFORE_MINUTES = 30          # bắt đầu giữ chỗ trước giờ hẹn
HISTORY_WEEKS = 8


def _now() -> datetime:
    return get_current_time()


def total_spots(garage: dict) -> int:
    return max(1, int((garage.get("capacity") or {}).get("total_spots") or 1))


# ── Realtime availability ───────────────────────────────────────

async def active_holds(garage_ids: Iterable[ObjectId], at: Optional[datetime] = None) -> Dict[ObjectId, int]:
    """Số chỗ đang giữ cho lượt đặt `reserved` tại thời điểm `at`, gom theo bãi (1 query)."""
    ids = list(garage_ids)
    if not ids:
        return {}
    at = at or _now()
    pipeline = [
        {"$match": {
            "garage_id": {"$in": ids},
            "status": "reserved",
            "start_time": {"$lte": at + timedelta(minutes=HOLD_BEFORE_MINUTES)},
            "grace_until": {"$gte": at},
        }},
        {"$group": {"_id": "$garage_id", "n": {"$sum": 1}}},
    ]
    return {d["_id"]: d["n"] async for d in BookingModel.collection.aggregate(pipeline)}


def availability_of(garage: dict, held: int = 0) -> dict:
    """Tình trạng chỗ trống hiển thị cho tài xế. Cấp 1 → chưa có dữ liệu."""
    level = int(garage.get("integration_level") or 1)
    total = total_spots(garage)
    occ = garage.get("occupancy") or {}
    occupied = max(0, min(total, int(occ.get("occupied") or 0)))
    available = max(0, total - occupied - held)
    has_data = level >= 2 and occ.get("updated_at") is not None
    rate = (total - available) / total
    if not has_data:
        status = "unknown"
    elif available == 0:
        status = "full"
    elif rate >= 0.85 or available <= 3:
        status = "limited"
    else:
        status = "available"
    updated = occ.get("updated_at")
    return {
        "has_data": has_data,
        "total_spots": total,
        "occupied": occupied if has_data else None,
        "held": held if has_data else None,
        "available": available if has_data else None,
        "occupancy_rate": round(rate, 3) if has_data else None,
        "status": status,                     # available | limited | full | unknown
        "source": occ.get("source", "manual"),
        "updated_at": updated.isoformat() if isinstance(updated, datetime) else updated,
    }


async def get_availability(garage: dict) -> dict:
    holds = await active_holds([garage["_id"]])
    return availability_of(garage, holds.get(garage["_id"], 0))


# ── Cập nhật occupancy ──────────────────────────────────────────

def _assert_owner(garage: dict, current_user: dict) -> None:
    if (current_user.get("tenant_id") != "super_admin" and
            garage.get("tenant_id") != current_user.get("tenant_id")):
        raise HTTPException(status_code=403, detail="Không phải bãi của bạn")


async def set_occupied(garage_id, occupied: int, current_user: dict, source: str = "manual") -> dict:
    """Chủ bãi đặt số xe đang trong bãi (cách cập nhật của bãi cấp 2)."""
    oid = convert_mongo_object_id(garage_id) if isinstance(garage_id, str) else garage_id
    if not oid:
        raise HTTPException(status_code=400, detail="Invalid garage id")
    garage = await GarageModel.collection.find_one({"_id": oid})
    if not garage:
        raise HTTPException(status_code=404, detail="Garage not found")
    _assert_owner(garage, current_user)
    value = max(0, min(total_spots(garage), int(occupied)))
    await GarageModel.collection.update_one({"_id": oid}, {"$set": {
        "occupancy.occupied": value,
        "occupancy.source": source,
        "occupancy.updated_at": _now(),
    }})
    garage = await GarageModel.collection.find_one({"_id": oid})
    await take_snapshot(garage)
    return await get_availability(garage)


async def adjust_occupied(garage_oid: ObjectId, delta: int) -> None:
    """Check-in (+1) / check-out (−1). Giữ trong [0, total_spots]."""
    garage = await GarageModel.collection.find_one({"_id": garage_oid})
    if not garage:
        return
    occ = garage.get("occupancy") or {}
    value = max(0, min(total_spots(garage), int(occ.get("occupied") or 0) + delta))
    source = occ.get("source") if occ.get("source") == "simulated" else "checkin"
    await GarageModel.collection.update_one({"_id": garage_oid}, {"$set": {
        "occupancy.occupied": value,
        "occupancy.source": source,
        "occupancy.updated_at": _now(),
    }})
    garage["occupancy"] = {**occ, "occupied": value, "source": source}
    await take_snapshot(garage)


async def take_snapshot(garage: dict) -> None:
    """Upsert 1 snapshot cho giờ hiện tại (mỗi bãi tối đa 1 bản ghi / giờ)."""
    now = _now()
    hour_start = now.replace(minute=0, second=0, microsecond=0)
    local = to_local(hour_start)
    holds = await active_holds([garage["_id"]], now)
    total = total_spots(garage)
    occupied = int((garage.get("occupancy") or {}).get("occupied") or 0)
    held = holds.get(garage["_id"], 0)
    available = max(0, total - occupied - held)
    await CapacitySnapshotModel.collection.update_one(
        {"garage_id": garage["_id"], "timestamp": hour_start},
        {"$set": {
            "tenant_id": garage.get("tenant_id", "platform"),
            "total_spots": total, "occupied": occupied, "held": held, "available": available,
            "occupancy_rate": round(min(1.0, (occupied + held) / total), 3),
            "source": (garage.get("occupancy") or {}).get("source", "manual"),
            "hour_of_day": local.hour, "day_of_week": local.weekday(),
            "updated_at": now, "updated_by": "system",
        }, "$setOnInsert": {"created_at": now, "created_by": "system"}},
        upsert=True,
    )


# ── Dự đoán ─────────────────────────────────────────────────────

async def hourly_rates(garage: dict, day_of_week: Optional[int] = None) -> List[dict]:
    """24 giá trị lấp đầy trung bình theo giờ (lịch sử 8 tuần), thiếu dữ liệu → đường cong loại bãi."""
    match: dict = {"garage_id": garage["_id"], "timestamp": {"$gte": _now() - timedelta(weeks=HISTORY_WEEKS)}}
    if day_of_week is not None:
        match["day_of_week"] = day_of_week
    pipeline = [
        {"$match": match},
        {"$group": {"_id": "$hour_of_day", "rate": {"$avg": "$occupancy_rate"}, "n": {"$sum": 1}}},
    ]
    hist = {d["_id"]: d async for d in CapacitySnapshotModel.collection.aggregate(pipeline)}
    dow = day_of_week if day_of_week is not None else to_local(_now()).weekday()
    out = []
    for h in range(24):
        d = hist.get(h)
        if d and d["n"] >= 2:
            out.append({"hour": h, "rate": round(d["rate"], 3), "samples": d["n"], "from_history": True})
        else:
            out.append({"hour": h, "rate": round(occupancy_profile(garage.get("lot_type", ""), h, dow), 3),
                        "samples": 0, "from_history": False})
    return out


async def predict_availability(garage: dict, at_time: datetime) -> dict:
    """Dự đoán chỗ trống tại `at_time` = trung bình cùng giờ, cùng thứ trong 8 tuần qua."""
    local = to_local(at_time)
    docs = await CapacitySnapshotModel.collection.find({
        "garage_id": garage["_id"],
        "hour_of_day": local.hour,
        "day_of_week": local.weekday(),
        "timestamp": {"$gte": _now() - timedelta(weeks=HISTORY_WEEKS)},
    }, {"occupancy_rate": 1}).to_list(length=HISTORY_WEEKS * 2)
    total = total_spots(garage)
    if len(docs) >= 3:
        rate = sum(float(d.get("occupancy_rate") or 0) for d in docs) / len(docs)
        confidence = min(1.0, len(docs) / HISTORY_WEEKS)
    else:
        rate = occupancy_profile(garage.get("lot_type", ""), local.hour, local.weekday())
        confidence = 0.3
    expected_available = max(0, int(round(total * (1 - rate))))
    return {
        "at": at_time.isoformat(),
        "occupancy_rate": round(rate, 3),
        "expected_available": expected_available,
        "confidence": round(confidence, 2),
    }


async def get_current_and_predicted(garage_id: str, horizons_min: Optional[List[int]] = None) -> dict:
    """Public — chỗ trống hiện tại + dự đoán ở các mốc."""
    horizons_min = horizons_min or [30, 60, 120]
    oid = convert_mongo_object_id(garage_id)
    if not oid:
        raise HTTPException(status_code=400, detail="Invalid garage id")
    garage = await GarageModel.collection.find_one({"_id": oid})
    if not garage:
        raise HTTPException(status_code=404, detail="Garage not found")
    predicted = {}
    for mins in horizons_min:
        predicted[f"t+{mins}min"] = await predict_availability(garage, _now() + timedelta(minutes=mins))
    return {"garage_id": str(oid), "current": await get_availability(garage), "predicted": predicted}
