# -*- coding: utf-8 -*-
"""Garage Service utils — CRUD per-garage service offerings + báo giá."""
import logging
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException

from app.api.garage_service.garage_service_models import GarageServiceModel
from app.api.garage_service.pricing_utils import normalize_pricing, display_price, quote_price
from app.api.garage.garage_models import GarageModel
from app.api.service_type.service_type_models import ServiceTypeModel
from app.api.shared.tool.datetime_convert import get_current_time
from app.api.shared.tool.convert_object_id import convert_mongo_object_id

logger = logging.getLogger(__name__)


def _with_price(pricing: dict, price: int) -> dict:
    """Ghi đè giá chính của mẫu bảng giá bằng `price`."""
    p = dict(pricing or {"mode": "block"})
    if p.get("mode") == "flat":
        p["flat_price"] = price
    else:
        p["first_block_price"] = price
        p.setdefault("next_block_price", price)
    return p


def resolve_pricing(doc: dict) -> dict:
    """Bảng giá của 1 garage_service; dữ liệu cũ chưa có pricing → block 60' theo `price`."""
    pricing = doc.get("pricing") or {}
    if not pricing:
        pricing = {"mode": "block", "first_block_minutes": 60, "first_block_price": int(doc.get("price", 0)),
                   "next_block_minutes": 60, "next_block_price": int(doc.get("price", 0))}
    return normalize_pricing(pricing, int(doc.get("price", 0)))


def format_garage_service(doc) -> dict:
    data = doc if isinstance(doc, dict) else doc.dump()
    return {
        "id": str(data.get("_id") or data.get("id") or ""),
        "garage_id": str(data.get("garage_id", "")),
        "service_type_code": data.get("service_type_code", ""),
        "price": data.get("price", 0),
        "estimated_duration_minutes": data.get("estimated_duration_minutes", 30),
        "pricing": resolve_pricing(data),
        "note": data.get("note", ""),
        "is_available": data.get("is_available", True),
    }


async def list_services_for_garage(garage_id: str) -> List[dict]:
    oid = convert_mongo_object_id(garage_id)
    if not oid:
        raise HTTPException(status_code=400, detail="Invalid garage id")
    docs = await GarageServiceModel.collection.find({
        "garage_id": oid, "is_available": True,
    }).to_list(length=100)
    return [format_garage_service(d) for d in docs]


async def get_garage_service_doc(garage_id: str, service_type_code: str) -> Optional[dict]:
    oid = convert_mongo_object_id(garage_id)
    if not oid:
        return None
    return await GarageServiceModel.collection.find_one({
        "garage_id": oid,
        "service_type_code": service_type_code,
        "is_available": True,
    })


async def get_price_for_garage_service(garage_id: str, service_type_code: str) -> Optional[int]:
    doc = await get_garage_service_doc(garage_id, service_type_code)
    return int(doc["price"]) if doc else None


async def quote_garage_service(
    garage_id: str, service_type_code: str, start: datetime, end: datetime,
) -> dict:
    """Báo giá cho 1 dịch vụ tại 1 bãi trong khoảng thời gian."""
    doc = await get_garage_service_doc(garage_id, service_type_code)
    if not doc:
        raise HTTPException(status_code=404, detail="Bãi không cung cấp dịch vụ này")
    q = quote_price(resolve_pricing(doc), start, end)
    return {"garage_id": garage_id, "service_type_code": service_type_code,
            "start_time": start, "end_time": end, **q}


async def upsert_garage_service(
    garage_id: str, service_type_code: str, price: Optional[int],
    estimated_duration_minutes: Optional[int], current_user: dict,
    pricing: Optional[dict] = None, note: Optional[str] = None,
) -> dict:
    """Add or update a service offering for a garage. Staff-scoped."""
    oid = convert_mongo_object_id(garage_id)
    if not oid:
        raise HTTPException(status_code=400, detail="Invalid garage id")

    # Validate service_type exists
    stype = await ServiceTypeModel.collection.find_one({"code": service_type_code})
    if not stype:
        raise HTTPException(status_code=404, detail="Service type not found")

    # Find garage — enforce tenant match
    garage = await GarageModel.collection.find_one({"_id": oid})
    if not garage:
        raise HTTPException(status_code=404, detail="Garage not found")
    if (current_user.get("tenant_id") != "super_admin" and
            garage.get("tenant_id") != current_user.get("tenant_id")):
        raise HTTPException(status_code=403, detail="Not your garage")

    existing = await GarageServiceModel.collection.find_one({
        "garage_id": oid, "service_type_code": service_type_code,
    })

    # Bảng giá: ưu tiên pricing gửi lên → bảng giá đang có → mẫu của danh mục
    if pricing:
        new_pricing = normalize_pricing(pricing, price or 0)
    else:
        base = (existing or {}).get("pricing") or stype.get("default_pricing") or {}
        if price is not None:
            base = _with_price(base, int(price))
        new_pricing = normalize_pricing(base, int(price or 0))
    new_price = display_price(new_pricing)

    duration = (estimated_duration_minutes
                or (existing or {}).get("estimated_duration_minutes")
                or stype.get("estimated_duration_minutes", 60))

    now = get_current_time()
    fields_to_set = {
        "price": new_price,
        "pricing": new_pricing,
        "estimated_duration_minutes": duration,
        "is_available": True,
        "updated_at": now,
        "updated_by": current_user.get("username", "system"),
    }
    if note is not None:
        fields_to_set["note"] = note

    if existing:
        await GarageServiceModel.collection.update_one({"_id": existing["_id"]}, {"$set": fields_to_set})
        result = await GarageServiceModel.collection.find_one({"_id": existing["_id"]})
    else:
        doc = {
            "tenant_id": garage["tenant_id"],
            "garage_id": oid,
            "service_type_code": service_type_code,
            "note": note or "",
            **fields_to_set,
            "created_at": now,
            "created_by": current_user.get("username", "system"),
        }
        res = await GarageServiceModel.collection.insert_one(doc)
        result = await GarageServiceModel.collection.find_one({"_id": res.inserted_id})

    # Also add to garage.services_offered if not already
    if service_type_code not in (garage.get("services_offered") or []):
        await GarageModel.collection.update_one(
            {"_id": oid},
            {"$addToSet": {"services_offered": service_type_code}},
        )

    return format_garage_service(result)


async def remove_garage_service(
    garage_id: str, service_type_code: str, current_user: dict,
) -> bool:
    oid = convert_mongo_object_id(garage_id)
    if not oid:
        raise HTTPException(status_code=400, detail="Invalid garage id")
    garage = await GarageModel.collection.find_one({"_id": oid})
    if not garage:
        raise HTTPException(status_code=404, detail="Garage not found")
    if (current_user.get("tenant_id") != "super_admin" and
            garage.get("tenant_id") != current_user.get("tenant_id")):
        raise HTTPException(status_code=403, detail="Not your garage")

    result = await GarageServiceModel.collection.update_one(
        {"garage_id": oid, "service_type_code": service_type_code},
        {"$set": {"is_available": False, "updated_at": get_current_time()}},
    )
    await GarageModel.collection.update_one(
        {"_id": oid},
        {"$pull": {"services_offered": service_type_code}},
    )
    return result.modified_count > 0
