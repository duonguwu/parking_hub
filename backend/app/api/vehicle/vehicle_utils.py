# -*- coding: utf-8 -*-
"""Vehicle Utils — Business logic for vehicle operations."""
import logging
from typing import List, Dict, Any

from fastapi import HTTPException
from app.api.vehicle.vehicle_models import VehicleModel, VEHICLE_TIER_MAP
from app.api.shared.tool.datetime_convert import get_current_time
from app.api.shared.tool.convert_object_id import convert_mongo_object_id

logger = logging.getLogger(__name__)


def format_vehicle(doc) -> dict:
    if isinstance(doc, dict):
        data = doc
    else:
        data = doc.dump()
    return {
        "id": str(data.get("_id", "")),
        "owner_user_id": data.get("owner_user_id", ""),
        "license_plate": data.get("license_plate", ""),
        "brand": data.get("brand", ""),
        "model": data.get("model", ""),
        "year": data.get("year", 0),
        "color": data.get("color", ""),
        "vehicle_type": data.get("vehicle_type", "standard"),
        "body_type": data.get("body_type", "sedan"),
        "size_class": data.get("size_class", "medium"),
        "minimum_garage_tier": data.get("minimum_garage_tier", 1),
        "vetc_linked": data.get("vetc_linked", False),
        "is_default": data.get("is_default", False),
        "is_active": data.get("is_active", True),
    }


async def get_user_vehicles(current_user: dict) -> List[dict]:
    """Get all vehicles for the current user."""
    try:
        # Query by owner_user_id, bypass tenant filter for platform-level entity
        docs = await VehicleModel.collection.find({
            "owner_user_id": current_user["user_id"],
            "is_active": True,
        }).to_list(length=50)
        return [format_vehicle(doc) for doc in docs]
    except Exception as e:
        logger.error(f"Error loading vehicles: {e}")
        raise HTTPException(status_code=500, detail="Failed to load vehicles")


async def get_vehicle_by_id(vehicle_id: str, current_user: dict) -> dict:
    """Get vehicle by ID (must belong to current user)."""
    oid = convert_mongo_object_id(vehicle_id)
    if not oid:
        raise HTTPException(status_code=400, detail="Invalid vehicle ID")

    doc = await VehicleModel.collection.find_one({
        "_id": oid,
        "owner_user_id": current_user["user_id"],
    })
    if not doc:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return format_vehicle(doc)


async def create_vehicle(data: dict, current_user: dict) -> dict:
    """Create a new vehicle for the current user."""
    # Check license plate uniqueness
    existing = await VehicleModel.collection.find_one({
        "license_plate": data["license_plate"],
        "is_active": True,
    })
    if existing:
        raise HTTPException(status_code=409, detail="License plate already registered")

    # Determine minimum tier from vehicle type
    vehicle_type = data.get("vehicle_type", "standard")
    min_tier = VEHICLE_TIER_MAP.get(vehicle_type, 1)

    # If setting as default, unset other defaults
    if data.get("is_default", False):
        await VehicleModel.collection.update_many(
            {"owner_user_id": current_user["user_id"]},
            {"$set": {"is_default": False}},
        )

    doc = VehicleModel(
        tenant_id="platform",
        owner_user_id=current_user["user_id"],
        license_plate=data["license_plate"],
        brand=data.get("brand", ""),
        model=data.get("model", ""),
        year=data.get("year", 2024),
        color=data.get("color", ""),
        vehicle_type=vehicle_type,
        body_type=data.get("body_type", "sedan"),
        size_class=data.get("size_class", "medium"),
        minimum_garage_tier=min_tier,
        is_default=data.get("is_default", False),
        is_active=True,
        created_at=get_current_time(),
        updated_at=get_current_time(),
        created_by=current_user.get("username", "system"),
        updated_by=current_user.get("username", "system"),
    )
    await doc.commit()

    result = await VehicleModel.collection.find_one({"_id": doc.pk})
    return format_vehicle(result)


async def update_vehicle(vehicle_id: str, update_data: dict, current_user: dict) -> bool:
    """Update a vehicle (must belong to current user)."""
    oid = convert_mongo_object_id(vehicle_id)
    if not oid:
        raise HTTPException(status_code=400, detail="Invalid vehicle ID")

    doc = await VehicleModel.collection.find_one({
        "_id": oid,
        "owner_user_id": current_user["user_id"],
    })
    if not doc:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    # Recalculate min tier if vehicle_type changed
    if "vehicle_type" in update_data:
        update_data["minimum_garage_tier"] = VEHICLE_TIER_MAP.get(
            update_data["vehicle_type"], 1
        )

    # Handle default toggle
    if update_data.get("is_default", False):
        await VehicleModel.collection.update_many(
            {"owner_user_id": current_user["user_id"]},
            {"$set": {"is_default": False}},
        )

    update_data["updated_at"] = get_current_time()
    update_data["updated_by"] = current_user.get("username", "system")

    result = await VehicleModel.collection.update_one(
        {"_id": oid}, {"$set": update_data}
    )
    return result.modified_count > 0


async def delete_vehicle(vehicle_id: str, current_user: dict) -> bool:
    """Soft-delete a vehicle."""
    oid = convert_mongo_object_id(vehicle_id)
    if not oid:
        raise HTTPException(status_code=400, detail="Invalid vehicle ID")

    result = await VehicleModel.collection.update_one(
        {"_id": oid, "owner_user_id": current_user["user_id"]},
        {"$set": {"is_active": False, "updated_at": get_current_time()}},
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return True
