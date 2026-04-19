# -*- coding: utf-8 -*-
"""Garage Service utils — CRUD per-garage service offerings."""
import logging
from typing import List, Optional
from bson import ObjectId
from fastapi import HTTPException

from app.api.garage_service.garage_service_models import GarageServiceModel
from app.api.garage.garage_models import GarageModel
from app.api.service_type.service_type_models import ServiceTypeModel
from app.api.shared.tool.datetime_convert import get_current_time
from app.api.shared.tool.convert_object_id import convert_mongo_object_id

logger = logging.getLogger(__name__)


def format_garage_service(doc) -> dict:
    data = doc if isinstance(doc, dict) else doc.dump()
    return {
        "id": str(data.get("_id") or data.get("id") or ""),
        "garage_id": str(data.get("garage_id", "")),
        "service_type_code": data.get("service_type_code", ""),
        "price": data.get("price", 0),
        "estimated_duration_minutes": data.get("estimated_duration_minutes", 30),
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


async def get_price_for_garage_service(garage_id: str, service_type_code: str) -> Optional[int]:
    oid = convert_mongo_object_id(garage_id)
    if not oid:
        return None
    doc = await GarageServiceModel.collection.find_one({
        "garage_id": oid,
        "service_type_code": service_type_code,
        "is_available": True,
    })
    return int(doc["price"]) if doc else None


async def upsert_garage_service(
    garage_id: str, service_type_code: str, price: int,
    estimated_duration_minutes: Optional[int], current_user: dict,
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

    duration = estimated_duration_minutes or stype.get("estimated_duration_minutes", 30)

    existing = await GarageServiceModel.collection.find_one({
        "garage_id": oid, "service_type_code": service_type_code,
    })
    now = get_current_time()
    if existing:
        await GarageServiceModel.collection.update_one(
            {"_id": existing["_id"]},
            {"$set": {
                "price": price,
                "estimated_duration_minutes": duration,
                "is_available": True,
                "updated_at": now,
                "updated_by": current_user.get("username", "system"),
            }},
        )
        result = await GarageServiceModel.collection.find_one({"_id": existing["_id"]})
    else:
        doc = {
            "tenant_id": garage["tenant_id"],
            "garage_id": oid,
            "service_type_code": service_type_code,
            "price": price,
            "estimated_duration_minutes": duration,
            "is_available": True,
            "created_at": now, "updated_at": now,
            "created_by": current_user.get("username", "system"),
            "updated_by": current_user.get("username", "system"),
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
