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
        "category": data.get("category", "wash"),
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
    """Seed the default WashMind service catalog (idempotent)."""
    defaults = [
        {
            "code": "wash_basic",
            "name": "Rửa xe cơ bản",
            "category": "wash",
            "description": "Rửa xe ngoại thất cơ bản",
            "base_price_min": 50000, "base_price_max": 100000,
            "estimated_duration_minutes": 20,
            "minimum_tier": 1,
            "vehicle_type_multiplier": {"standard": 1.0, "premium": 1.2, "luxury": 1.5, "super": 2.0},
        },
        {
            "code": "wash_premium",
            "name": "Rửa xe Premium",
            "category": "wash",
            "description": "Rửa ngoại thất + nội thất cơ bản",
            "base_price_min": 80000, "base_price_max": 200000,
            "estimated_duration_minutes": 30,
            "minimum_tier": 2,
            "vehicle_type_multiplier": {"standard": 1.0, "premium": 1.3, "luxury": 1.6, "super": 2.0},
        },
        {
            "code": "interior",
            "name": "Vệ sinh nội thất",
            "category": "interior",
            "description": "Hút bụi, lau nội thất, khử mùi",
            "base_price_min": 150000, "base_price_max": 400000,
            "estimated_duration_minutes": 60,
            "minimum_tier": 2,
            "vehicle_type_multiplier": {"standard": 1.0, "premium": 1.3, "luxury": 1.6, "super": 2.0},
        },
        {
            "code": "detailing",
            "name": "Detailing chuyên sâu",
            "category": "detailing",
            "description": "Làm mới ngoại thất chuyên sâu",
            "base_price_min": 500000, "base_price_max": 2000000,
            "estimated_duration_minutes": 180,
            "minimum_tier": 3,
            "vehicle_type_multiplier": {"standard": 1.0, "premium": 1.3, "luxury": 1.6, "super": 2.2},
        },
        {
            "code": "coating",
            "name": "Phủ ceramic/nano",
            "category": "coating",
            "description": "Phủ bảo vệ sơn xe",
            "base_price_min": 3000000, "base_price_max": 15000000,
            "estimated_duration_minutes": 480,
            "minimum_tier": 4,
            "vehicle_type_multiplier": {"standard": 1.0, "premium": 1.2, "luxury": 1.5, "super": 2.0},
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
