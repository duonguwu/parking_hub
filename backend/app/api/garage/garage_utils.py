# -*- coding: utf-8 -*-
"""Garage Utils — Business logic for garage operations."""
import logging
from typing import List, Dict, Any, Optional

from fastapi import HTTPException
from app.api.garage.garage_models import GarageModel
from app.api.shared.tool.datetime_convert import get_current_time
from app.api.shared.tool.convert_object_id import convert_mongo_object_id

logger = logging.getLogger(__name__)


def format_garage(doc) -> dict:
    """Format garage document for API response."""
    if isinstance(doc, dict):
        data = doc
    else:
        data = doc.dump()

    return {
        "id": str(data.get("_id") or data.get("id") or ""),
        "tenant_id": data.get("tenant_id", ""),
        "name": data.get("name", ""),
        "slug": data.get("slug", ""),
        "location": data.get("location", {}),
        "address": data.get("address", {}),
        "tier": data.get("tier", 1),
        "tier_score": data.get("tier_score", 0),
        "capacity": data.get("capacity", {}),
        "operating_hours": data.get("operating_hours", {}),
        "services_offered": data.get("services_offered", []),
        "vehicle_types_accepted": data.get("vehicle_types_accepted", []),
        "amenities": data.get("amenities", []),
        "description": data.get("description", ""),
        "photos": data.get("photos", []),
        "status": data.get("status", ""),
        "is_verified": data.get("is_verified", False),
        "is_accepting_bookings": data.get("is_accepting_bookings", True),
        "current_load": data.get("current_load", {}),
        "stats": data.get("stats", {}),
        "created_at": str(data.get("created_at", "")),
    }


async def get_all_garages(
    current_user: dict,
    status_filter: str = "active",
    limit: int = 50,
) -> List[dict]:
    """Get all garages (tenant-filtered or platform-wide for customers)."""
    try:
        filter_dict = {}
        if status_filter:
            filter_dict["status"] = status_filter

        cursor = GarageModel.find(filter_dict, current_user=current_user)
        docs = await cursor.to_list(length=limit)
        return [format_garage(doc) for doc in docs]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading garages: {e}")
        raise HTTPException(status_code=500, detail="Failed to load garages")


async def get_garage_by_id(garage_id: str, current_user: dict) -> dict:
    """Get garage by ID."""
    oid = convert_mongo_object_id(garage_id)
    if not oid:
        raise HTTPException(status_code=400, detail="Invalid garage ID format")

    try:
        doc = await GarageModel.find_one({"_id": oid}, current_user=current_user)
        if not doc:
            raise HTTPException(status_code=404, detail="Garage not found")
        return format_garage(doc)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting garage {garage_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def search_garages_nearby(
    latitude: float,
    longitude: float,
    max_distance_km: float = 10,
    min_tier: int = 1,
    service_type: Optional[str] = None,
) -> List[dict]:
    """
    Search garages near a location using MongoDB 2dsphere index.
    Public endpoint — no tenant filter.
    """
    try:
        pipeline = [
            {
                "$geoNear": {
                    "near": {"type": "Point", "coordinates": [longitude, latitude]},
                    "distanceField": "distance_meters",
                    "maxDistance": max_distance_km * 1000,
                    "spherical": True,
                    "query": {
                        "status": "active",
                        "is_accepting_bookings": True,
                        "tier": {"$gte": min_tier},
                    },
                }
            },
            {"$limit": 20},
        ]

        if service_type:
            pipeline[0]["$geoNear"]["query"]["services_offered"] = service_type

        results = []
        async for doc in GarageModel.collection.aggregate(pipeline):
            garage = format_garage(doc)
            garage["distance_km"] = round(doc.get("distance_meters", 0) / 1000, 2)
            results.append(garage)

        return results
    except Exception as e:
        logger.error(f"Error searching garages: {e}")
        raise HTTPException(status_code=500, detail="Failed to search garages")


async def update_garage(
    garage_id: str,
    update_data: dict,
    current_user: dict,
) -> bool:
    """Update garage profile."""
    return await GarageModel.update_with_tenant_check(
        doc_id=garage_id,
        update_data=update_data,
        current_user=current_user,
    )


async def update_garage_capacity(
    garage_id: str,
    capacity_data: dict,
    current_user: dict,
) -> bool:
    """Update real-time capacity load for a garage."""
    oid = convert_mongo_object_id(garage_id)
    if not oid:
        raise HTTPException(status_code=400, detail="Invalid garage ID")

    doc = await GarageModel.find_one({"_id": oid}, current_user=current_user)
    if not doc:
        raise HTTPException(status_code=404, detail="Garage not found")

    update = {
        "current_load.vehicles_in_service": capacity_data["vehicles_in_service"],
        "current_load.vehicles_waiting": capacity_data["vehicles_waiting"],
        "current_load.estimated_wait_minutes": capacity_data.get("estimated_wait_minutes", 0),
        "current_load.last_updated": get_current_time(),
        "updated_at": get_current_time(),
        "updated_by": current_user.get("username", "system"),
    }

    result = await GarageModel.collection.update_one({"_id": oid}, {"$set": update})
    return result.modified_count > 0
