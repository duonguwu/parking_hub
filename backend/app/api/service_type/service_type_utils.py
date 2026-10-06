# -*- coding: utf-8 -*-
"""Service Type utils."""
import logging
from typing import List, Optional

from app.api.service_type.service_type_models import ServiceTypeModel
from app.api.shared.tool.datetime_convert import get_current_time

logger = logging.getLogger(__name__)


def format_service_type(doc) -> dict:
    data = doc if isinstance(doc, dict) else doc.dump()
    return {
        "id": str(data.get("_id") or data.get("id") or ""),
        "code": data.get("code", ""),
        "name": data.get("name", ""),
        "category": data.get("category", "parking"),
        "unit": data.get("unit", "hour"),
        "icon": data.get("icon", "clock"),
        "description": data.get("description", ""),
        "base_price_min": data.get("base_price_min", 0),
        "base_price_max": data.get("base_price_max", 0),
        "estimated_duration_minutes": data.get("estimated_duration_minutes", 60),
        "default_pricing": data.get("default_pricing", {}),
        "is_popular": data.get("is_popular", False),
        "sort_order": data.get("sort_order", 100),
        "is_active": data.get("is_active", True),
    }


async def get_all_service_types(active_only: bool = True) -> List[dict]:
    """Public endpoint — no tenant filter."""
    query = {"is_active": True} if active_only else {}
    docs = await ServiceTypeModel.collection.find(query).sort("sort_order", 1).to_list(length=100)
    return [format_service_type(d) for d in docs]


async def get_service_type_by_code(code: str) -> Optional[dict]:
    doc = await ServiceTypeModel.collection.find_one({"code": code})
    return format_service_type(doc) if doc else None


async def get_service_type_map() -> dict:
    """{code: formatted service type} — dùng để enrich danh sách dịch vụ."""
    return {st["code"]: st for st in await get_all_service_types(active_only=False)}


def _block(first_min, first_price, next_min, next_price, cap=None, peak=None):
    return {
        "mode": "block",
        "first_block_minutes": first_min, "first_block_price": first_price,
        "next_block_minutes": next_min, "next_block_price": next_price,
        "daily_cap": cap, "peak_rules": peak or [],
    }


def _flat(price, unit_minutes=None):
    return {"mode": "flat", "flat_price": price, "flat_unit_minutes": unit_minutes, "peak_rules": []}


# Danh mục chuẩn của nền tảng. Mặt bằng giá ô tô tại TP.HCM (tham khảo).
DEFAULT_SERVICE_TYPES = [
    {
        "code": "park_hourly", "name": "Gửi theo giờ", "category": "parking", "unit": "hour",
        "icon": "clock", "is_popular": True, "sort_order": 10,
        "description": "Tính phí theo block, block đầu và block tiếp theo, có trần ngày",
        "base_price_min": 15000, "base_price_max": 40000, "estimated_duration_minutes": 120,
        "default_pricing": _block(60, 25000, 60, 15000, cap=200000, peak=[
            {"days": [0, 1, 2, 3, 4], "start": "17:00", "end": "20:00", "multiplier": 1.2},
        ]),
    },
    {
        "code": "park_overnight", "name": "Gửi qua đêm", "category": "parking", "unit": "night",
        "icon": "moon", "is_popular": False, "sort_order": 20,
        "description": "Trọn gói khung đêm, thường 18:00 – 07:00 hôm sau",
        "base_price_min": 50000, "base_price_max": 150000, "estimated_duration_minutes": 780,
        "default_pricing": _flat(80000),
    },
    {
        "code": "park_daily", "name": "Gửi theo ngày", "category": "parking", "unit": "day",
        "icon": "calendar-days", "is_popular": False, "sort_order": 30,
        "description": "Trọn gói mỗi 24 giờ, phù hợp đi công tác, đi sân bay",
        "base_price_min": 100000, "base_price_max": 300000, "estimated_duration_minutes": 1440,
        "default_pricing": _flat(150000, 1440),
    },
    {
        "code": "park_workday", "name": "Gói ngày làm việc", "category": "subscription", "unit": "month",
        "icon": "briefcase", "is_popular": True, "sort_order": 40,
        "description": "Gửi giờ hành chính thứ 2 – thứ 6 (07:00 – 19:00), tính theo tháng",
        "base_price_min": 800000, "base_price_max": 2000000, "estimated_duration_minutes": 43200,
        "default_pricing": _flat(1200000, 43200),
    },
    {
        "code": "park_monthly", "name": "Gói tháng 24/7", "category": "subscription", "unit": "month",
        "icon": "credit-card", "is_popular": True, "sort_order": 50,
        "description": "Giữ chỗ cả ngày lẫn đêm trong 30 ngày",
        "base_price_min": 1200000, "base_price_max": 4000000, "estimated_duration_minutes": 43200,
        "default_pricing": _flat(2000000, 43200),
    },
    {
        "code": "ev_charging", "name": "Sạc xe điện", "category": "addon", "unit": "hour",
        "icon": "zap", "is_popular": False, "sort_order": 60,
        "description": "Cổng sạc AC/DC tại bãi, tính theo giờ cắm sạc (chưa gồm phí gửi)",
        "base_price_min": 20000, "base_price_max": 60000, "estimated_duration_minutes": 60,
        "default_pricing": _block(60, 35000, 60, 35000),
    },
    {
        "code": "car_wash", "name": "Rửa xe trong lúc gửi", "category": "addon", "unit": "session",
        "icon": "droplets", "is_popular": False, "sort_order": 70,
        "description": "Rửa ngoài + hút bụi khi xe đang gửi",
        "base_price_min": 60000, "base_price_max": 200000, "estimated_duration_minutes": 45,
        "default_pricing": _flat(100000),
    },
    {
        "code": "valet", "name": "Đỗ hộ (valet)", "category": "addon", "unit": "session",
        "icon": "key-round", "is_popular": False, "sort_order": 80,
        "description": "Nhân viên nhận xe tại cổng và đỗ hộ",
        "base_price_min": 30000, "base_price_max": 100000, "estimated_duration_minutes": 10,
        "default_pricing": _flat(50000),
    },
]


async def seed_default_service_types():
    """
    Seed/đồng bộ danh mục dịch vụ chuẩn (idempotent, upsert theo code).
    Cập nhật các trường danh mục cho bản ghi đã có, giữ nguyên is_active do admin chỉnh.
    """
    now = get_current_time()
    count_new = 0
    for d in DEFAULT_SERVICE_TYPES:
        res = await ServiceTypeModel.collection.update_one(
            {"code": d["code"]},
            {
                "$set": {**d, "updated_at": now, "updated_by": "system"},
                "$unset": {"minimum_tier": "", "vehicle_type_multiplier": ""},
                "$setOnInsert": {
                    "tenant_id": "platform", "is_active": True,
                    "created_at": now, "created_by": "system",
                },
            },
            upsert=True,
        )
        if res.upserted_id:
            count_new += 1

    if count_new:
        logger.info(f"Seeded {count_new} service types")
    return count_new
