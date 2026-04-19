# -*- coding: utf-8 -*-
"""Search log writers — one row per match query + async updates on user action."""
import logging
from datetime import datetime
from typing import List, Optional

from bson import ObjectId

from app.api.search_log.search_log_models import SearchLogModel
from app.api.shared.tool.datetime_convert import get_current_time
from app.api.shared.tool.convert_object_id import convert_mongo_object_id

logger = logging.getLogger(__name__)


async def log_search(
    customer_id: Optional[str], session_id: str,
    location_lat: float, location_lng: float,
    vehicle_type: str, service_type_code: str,
    requested_time: datetime,
    matches: List[dict],           # serialized MatchResult dicts (rank, garage_id, score, components)
    weights: dict,
    context: dict,                 # weather, is_peak_hour, district, ...
) -> str:
    """Fire-and-forget style: failure here should not break search."""
    cust_oid = convert_mongo_object_id(customer_id) if customer_id else None
    now = get_current_time()
    doc = {
        "tenant_id": "platform",
        "customer_id": cust_oid,
        "session_id": session_id or "",
        "search_location": {"type": "Point", "coordinates": [location_lng, location_lat]},
        "vehicle_type": vehicle_type or "",
        "service_type_code": service_type_code or "",
        "requested_time": requested_time,
        "context": context or {},
        "results_count": len(matches),
        "results_shown": matches,
        "weights_used": weights or {},
        "action": "shown",
        "selected_garage_id": "",
        "selected_rank": 0,
        "time_spent_seconds": 0,
        "created_at": now, "updated_at": now,
        "created_by": "system", "updated_by": "system",
    }
    try:
        res = await SearchLogModel.collection.insert_one(doc)
        return str(res.inserted_id)
    except Exception as e:
        logger.warning(f"Failed to log search: {e}")
        return ""


async def update_search_action(
    search_log_id: str, action: str,
    selected_garage_id: Optional[str] = None,
    selected_rank: int = 0,
    time_spent_seconds: int = 0,
) -> bool:
    """
    Update action (booked | viewed_details | abandoned).
    Fire-and-forget — implicit feedback signal.
    """
    oid = convert_mongo_object_id(search_log_id)
    if not oid:
        return False
    try:
        result = await SearchLogModel.collection.update_one(
            {"_id": oid},
            {"$set": {
                "action": action,
                "selected_garage_id": selected_garage_id or "",
                "selected_rank": int(selected_rank or 0),
                "time_spent_seconds": int(time_spent_seconds or 0),
                "updated_at": get_current_time(),
            }},
        )
        return result.matched_count > 0
    except Exception as e:
        logger.warning(f"Failed to update search action: {e}")
        return False
