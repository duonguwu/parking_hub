# -*- coding: utf-8 -*-
"""Service Type utils."""
import logging
from typing import List, Optional
from fastapi import HTTPException

from app.api.service_type.service_type_models import ServiceTypeModel, SERVICE_CATEGORIES
from app.api.shared.tool.datetime_convert import get_current_time

logger = logging.getLogger(__name__)


def format_service_type(doc) -> dict:
    data = doc if isinstance(doc, dict) else doc.dump()
    return {
        "id": str(data.get("_id") or data.get("id") or ""),
        "code": data.get("code", ""),
        "name": data.get("name", ""),
        "category": data.get("category", "hourly"),
        "description": data.get("description", ""),
        "base_price_min": data.get("base_price_min", 0),
        "base_price_max": data.get("base_price_max", 0),
        "estimated_duration_minutes": data.get("estimated_duration_minutes", 30),
        "minimum_tier": data.get("minimum_tier", 1),
        "vehicle_type_multiplier": data.get("vehicle_type_multiplier", {}),
        "is_active": data.get("is_active", True),
    }


async def get_all_service_types(active_only: bool = True) -> List[dict]:
    """Public endpoint — no tenant filter."""
    query = {"is_active": True} if active_only else {}
    docs = await ServiceTypeModel.collection.find(query).to_list(length=100)
    return [format_service_type(d) for d in docs]


async def get_service_type_by_code(code: str) -> Optional[dict]:
    doc = await ServiceTypeModel.collection.find_one({"code": code})
    return format_service_type(doc) if doc else None


async def seed_default_service_types():
    """
    Seed danh mục dịch vụ mặc định (idempotent).

    Đây là DỮ LIỆU MẪU để các luồng đặt chỗ, tính giá và dashboard có dữ liệu chạy.
    Khi chốt nghiệp vụ đỗ xe, thay danh sách dưới đây bằng danh mục thật.
    Xem docs/04_technical/08_Codebase_Guide.md mục về service_type.
    """
    defaults = [
        {
            "code": "park_hourly",
            "name": "Gửi xe theo giờ",
            "category": "hourly",
            "description": "Tính phí theo thời gian gửi thực tế",
            "base_price_min": 15000, "base_price_max": 30000,
            "estimated_duration_minutes": 60,
            "minimum_tier": 1,
            "vehicle_type_multiplier": {"standard": 1.0, "premium": 1.0, "luxury": 1.0, "super": 1.0},
        },
        {
            "code": "park_overnight",
            "name": "Gửi xe qua đêm",
            "category": "overnight",
            "description": "Gửi trong khung giờ đêm theo giá cố định",
            "base_price_min": 50000, "base_price_max": 120000,
            "estimated_duration_minutes": 720,
            "minimum_tier": 1,
            "vehicle_type_multiplier": {"standard": 1.0, "premium": 1.0, "luxury": 1.0, "super": 1.0},
        },
        {
            "code": "park_daily",
            "name": "Gửi xe theo ngày",
            "category": "daily",
            "description": "Gửi nhiều ngày liên tục, ví dụ đi công tác",
            "base_price_min": 100000, "base_price_max": 250000,
            "estimated_duration_minutes": 1440,
            "minimum_tier": 1,
            "vehicle_type_multiplier": {"standard": 1.0, "premium": 1.0, "luxury": 1.0, "super": 1.0},
        },
        {
            "code": "park_monthly",
            "name": "Gói tháng",
            "category": "monthly",
            "description": "Cam kết theo tháng, khung giờ do bãi quy định",
            "base_price_min": 1000000, "base_price_max": 3000000,
            "estimated_duration_minutes": 43200,
            "minimum_tier": 2,
            "vehicle_type_multiplier": {"standard": 1.0, "premium": 1.0, "luxury": 1.0, "super": 1.0},
        },
    ]

    count_new = 0
    for d in defaults:
        exists = await ServiceTypeModel.collection.find_one({"code": d["code"]})
        if exists:
            continue
        doc = {
            **d,
            "tenant_id": "platform",
            "is_active": True,
            "created_at": get_current_time(),
            "updated_at": get_current_time(),
            "created_by": "system",
            "updated_by": "system",
        }
        await ServiceTypeModel.collection.insert_one(doc)
        count_new += 1

    if count_new:
        logger.info(f"Seeded {count_new} service types")
    return count_new
