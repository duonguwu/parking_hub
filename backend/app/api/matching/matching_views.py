# -*- coding: utf-8 -*-
"""Matching API — /match/search entry point."""
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

from app.api.matching.matching_engine import find_best_garages
from app.api.search_log.search_log_utils import log_search, update_search_action
from app.api.auth.dependencies import get_current_user_optional
from app.api.shared.common_utils import api_response
from app.api.shared.schemas import Operation, Resource
from app.api.shared.tool.datetime_convert import get_current_time
from app.services.osm.osm_client import LatLng

matching_router = APIRouter(prefix="/match", tags=["Smart Matching"])


class GeoPoint(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


class MatchSearchInput(BaseModel):
    current_location: GeoPoint
    service_type_code: str = Field(..., min_length=1)
    vehicle_id: Optional[str] = None
    vehicle_type: Optional[str] = None
    requested_time: Optional[datetime] = None
    max_travel_minutes: int = Field(default=30, ge=5, le=120)
    must_have_amenities: List[str] = []
    excluded_garage_ids: List[str] = []
    session_id: Optional[str] = None
    top_k: int = Field(default=3, ge=1, le=10)


class FeedbackInput(BaseModel):
    search_id: str = Field(..., min_length=1)
    action: str = Field(..., pattern="^(booked|viewed_details|abandoned)$")
    selected_garage_id: Optional[str] = None
    selected_rank: int = 0
    time_spent_seconds: int = 0


def _match_to_dict(m) -> dict:
    return {
        "garage_id": m.garage_id,
        "name": m.garage_name,
        "tier": m.tier,
        "rank": m.rank,
        "total_score": m.total_score,
        "travel_minutes": m.travel_minutes,
        "travel_distance_km": m.travel_distance_km,
        "predicted_arrival": m.predicted_arrival.isoformat() if m.predicted_arrival else None,
        "predicted_wait_minutes": m.predicted_wait_minutes,
        "service_price": m.service_price,
        "location": m.location,
        "component_scores": m.component_scores,
        "reasons": m.reasons,
        "trade_offs": m.trade_offs,
    }


@matching_router.post("/search")
async def match_search(
    input_data: MatchSearchInput,
    current_user: Optional[dict] = Depends(get_current_user_optional),
) -> Dict[str, Any]:
    """Full Smart Matching pipeline — PUBLIC (customer login optional for personalization)."""
    session_id = input_data.session_id or f"sess_{uuid.uuid4().hex[:12]}"
    current_loc = LatLng(lat=input_data.current_location.lat, lng=input_data.current_location.lng)
    requested_time = input_data.requested_time or get_current_time()

    # TODO Phase 3: load user_behavior_profile from DB when user_id given
    user_profile = None

    result = await find_best_garages(
        current_location=current_loc,
        service_type_code=input_data.service_type_code,
        vehicle_id=input_data.vehicle_id,
        vehicle_type=input_data.vehicle_type,
        requested_time=requested_time,
        max_travel_minutes=input_data.max_travel_minutes,
        must_have_amenities=input_data.must_have_amenities,
        excluded_garage_ids=input_data.excluded_garage_ids,
        user_profile=user_profile,
        top_k=input_data.top_k,
    )

    match_dicts = [_match_to_dict(m) for m in result["matches"]]

    # Log search (fire-and-forget — errors swallowed inside log_search)
    search_log_id = await log_search(
        customer_id=(current_user or {}).get("user_id") if current_user else None,
        session_id=session_id,
        location_lat=input_data.current_location.lat,
        location_lng=input_data.current_location.lng,
        vehicle_type=input_data.vehicle_type or "",
        service_type_code=input_data.service_type_code,
        requested_time=requested_time,
        matches=match_dicts,
        weights=result["weights"],
        context=result["context"],
    )

    return api_response(
        Operation.PROCESSED, Resource.MATCH_RESULTS,
        {
            "search_id": search_log_id,
            "session_id": session_id,
            "results_count": len(match_dicts),
            "matches": match_dicts,
            "context": result["context"],
            "weights": result["weights"],
        },
    )


@matching_router.post("/feedback")
async def match_feedback(input_data: FeedbackInput) -> Dict[str, Any]:
    """Implicit feedback signal for LTR training. Fire-and-forget."""
    ok = await update_search_action(
        input_data.search_id,
        action=input_data.action,
        selected_garage_id=input_data.selected_garage_id,
        selected_rank=input_data.selected_rank,
        time_spent_seconds=input_data.time_spent_seconds,
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Search log not found")
    return api_response(Operation.UPDATED, Resource.MATCH_RESULTS)
