# -*- coding: utf-8 -*-
"""
Smart Matching Engine — 5-stage pipeline.

Stages:
    1. Hard filter (geo + tier + service + operating hours)
    2. Feature enrichment (OSM matrix, weather, capacity predictions, prices)
    3. Scoring (8 component scores × context-dependent weights)
    4. Personalization (cold-start: user profile adjustments)
    5. Rank + MMR diversity + reasons
"""
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from bson import ObjectId

from app.api.garage.garage_models import GarageModel
from app.api.garage_service.garage_service_models import GarageServiceModel
from app.api.vehicle.vehicle_models import VehicleModel
from app.api.capacity.capacity_utils import predict_capacity, CapacityState
from app.api.matching.scoring import (
    score_distance, score_wait, score_quality, score_fit, score_affinity,
    score_price, score_reliability, score_environment,
    compute_context_weights, build_reasons_tradeoffs,
)
from app.api.shared.tool.datetime_convert import get_current_time
from app.api.shared.tool.convert_object_id import convert_mongo_object_id
from app.services.osm.osm_client import osm_client, LatLng, haversine_meters
from app.services.weather.weather_service import weather_service, WeatherSnapshot

logger = logging.getLogger(__name__)


# ── Config ──────────────────────────────────────────────────────────

PEAK_HOUR_RANGES = [(17, 19)]      # 17:00-19:00 Mon-Fri
DEFAULT_MAX_TRAVEL_MIN = 30


def _is_peak_hour(dt: datetime) -> bool:
    if dt.weekday() >= 5:   # Sat/Sun
        return False
    return any(lo <= dt.hour < hi for lo, hi in PEAK_HOUR_RANGES)


def _is_garage_open_at(garage: dict, at_time: datetime) -> bool:
    """Check if garage's operating_hours covers at_time."""
    hours = (garage.get("capacity") or {}).get("operating_hours") or {}
    day_keys = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    day_key = day_keys[at_time.weekday()]
    slot = hours.get(day_key)
    if not slot:
        # No schedule → assume open
        return True
    open_s = slot.get("open", "00:00")
    close_s = slot.get("close", "23:59")
    try:
        open_h, open_m = map(int, open_s.split(":"))
        close_h, close_m = map(int, close_s.split(":"))
        open_mins = open_h * 60 + open_m
        close_mins = close_h * 60 + close_m
        now_mins = at_time.hour * 60 + at_time.minute
        return open_mins <= now_mins <= close_mins
    except Exception:
        return True


# ── Data classes ────────────────────────────────────────────────────

@dataclass
class EnrichedCandidate:
    garage: dict
    travel_min: float
    travel_distance_km: float
    route_confidence: float
    arrival_time: datetime
    predicted_state: CapacityState
    weather_at_arrival: Optional[WeatherSnapshot]
    service_price: Optional[int]


@dataclass
class MatchResult:
    garage_id: str
    garage_name: str
    tier: int
    total_score: float
    rank: int = 0
    travel_minutes: int = 0
    travel_distance_km: float = 0.0
    predicted_arrival: Optional[datetime] = None
    predicted_wait_minutes: int = 0
    service_price: int = 0
    component_scores: Dict[str, float] = field(default_factory=dict)
    reasons: List[Dict[str, Any]] = field(default_factory=list)
    trade_offs: List[Dict[str, Any]] = field(default_factory=list)
    location: Dict[str, Any] = field(default_factory=dict)


# ── Stage 1: Hard filter ────────────────────────────────────────────

async def stage1_filter(
    current_location: LatLng, vehicle_min_tier: int, service_type_code: str,
    max_travel_minutes: int, must_have_amenities: List[str],
    excluded_garage_ids: List[str], requested_time: datetime,
    max_candidates: int = 30,
) -> List[dict]:
    # Approx: in urban VN, 1 min ~= 0.8km straight-line
    # So max_distance_meters = max_travel_minutes * 800  (conservative)
    max_dist_m = int(max_travel_minutes * 800)

    query: Dict[str, Any] = {
        "location": {
            "$nearSphere": {
                "$geometry": {"type": "Point", "coordinates": [current_location.lng, current_location.lat]},
                "$maxDistance": max_dist_m,
            }
        },
        "tier": {"$gte": vehicle_min_tier},
        "status": "active",
        "is_accepting_bookings": True,
        "services_offered": service_type_code,
    }
    if must_have_amenities:
        query["amenities"] = {"$all": must_have_amenities}
    if excluded_garage_ids:
        oids = [convert_mongo_object_id(g) for g in excluded_garage_ids]
        query["_id"] = {"$nin": [o for o in oids if o]}

    docs = await GarageModel.collection.find(query).limit(max_candidates).to_list(length=max_candidates)
    # Filter by operating hours in Python
    return [g for g in docs if _is_garage_open_at(g, requested_time)]


# ── Stage 2: Enrichment ─────────────────────────────────────────────

async def stage2_enrich(
    candidates: List[dict], current_location: LatLng, service_type_code: str,
    requested_time: datetime, traffic_multiplier: float = 1.0,
) -> List[EnrichedCandidate]:
    if not candidates:
        return []

    dests = [LatLng(lat=g["location"]["coordinates"][1], lng=g["location"]["coordinates"][0])
             for g in candidates]

    # Batch routing
    matrix = await osm_client.get_matrix([current_location], dests)

    # Weather (use user location — typically same broad area for all candidates)
    try:
        weather = await weather_service.current(current_location.lat, current_location.lng)
    except Exception:
        weather = WeatherSnapshot()

    now = get_current_time()
    enriched: List[EnrichedCandidate] = []
    for idx, g in enumerate(candidates):
        try:
            travel_sec = matrix.durations[0][idx] if matrix.durations else 0
        except (IndexError, TypeError):
            travel_sec = 0
        travel_min = (travel_sec / 60.0) * traffic_multiplier
        try:
            dist_m = matrix.distances[0][idx] if matrix.distances else 0
        except (IndexError, TypeError):
            dist_m = 0

        arrival = now + timedelta(minutes=travel_min)
        predicted = await predict_capacity(str(g["_id"]), arrival)

        # Price lookup (per-garage service override)
        price_doc = await GarageServiceModel.collection.find_one({
            "garage_id": g["_id"],
            "service_type_code": service_type_code,
            "is_available": True,
        })
        price = int(price_doc["price"]) if price_doc else None

        enriched.append(EnrichedCandidate(
            garage=g,
            travel_min=travel_min,
            travel_distance_km=dist_m / 1000.0,
            route_confidence=matrix.confidence,
            arrival_time=arrival,
            predicted_state=predicted,
            weather_at_arrival=weather,
            service_price=price,
        ))
    return enriched


# ── Stage 3+4: Scoring + Personalization ───────────────────────────

async def stage3_score(
    enriched: List[EnrichedCandidate],
    vehicle_min_tier: int,
    user_profile: Optional[dict],
    weather: Optional[WeatherSnapshot],
    is_peak_hour: bool,
    area_demand: str,
) -> List[MatchResult]:
    if not enriched:
        return []

    # Collect area prices for percentile-based S_price
    area_prices = [c.service_price for c in enriched if c.service_price is not None]

    # User parameters
    prefs = (user_profile or {}).get("preferences") or {}
    distance_tol = float(prefs.get("distance_tolerance_km", 30))   # interpret as minutes for MVP
    # Map km tolerance to min tolerance: 30km → 30min for urban
    user_dist_tol_min = max(10.0, distance_tol)
    wait_tol_min = float(prefs.get("wait_tolerance_minutes", 20))
    price_sensitivity = str(prefs.get("price_sensitivity", "medium"))
    user_affinity = (user_profile or {}).get("garage_affinity") or []
    has_affinity = bool(user_affinity)

    weights = compute_context_weights(
        is_raining=(weather is not None and weather.is_raining),
        is_peak_hour=is_peak_hour,
        price_sensitivity=price_sensitivity,
        has_affinity_history=has_affinity,
        area_demand=area_demand,
    )

    now = get_current_time()
    results: List[MatchResult] = []
    for c in enriched:
        g = c.garage
        tier = int(g.get("tier", 1))
        tier_score = float(g.get("tier_score", 0))
        stats = g.get("stats") or {}
        amenities = g.get("amenities") or []

        # days since last tier_assessment
        assess = (g.get("tier_assessment") or {}).get("last_assessed_at")
        if assess:
            try:
                days = (now - assess).days
            except Exception:
                days = 0
        else:
            days = 9999    # never assessed → low confidence

        s = {
            "distance": score_distance(c.travel_min, user_dist_tol_min),
            "wait": score_wait(float(c.predicted_state.wait_minutes), wait_tol_min),
            "quality": score_quality(tier_score, days),
            "fit": score_fit(vehicle_min_tier, tier),
            "affinity": score_affinity(user_affinity, str(g["_id"])),
            "price": score_price(c.service_price or 0, price_sensitivity, area_prices),
            "reliability": score_reliability(stats),
            "environment": score_environment(c.weather_at_arrival, amenities),
        }

        total = sum(weights.get(k, 0) * v for k, v in s.items())
        total_scaled = total * 100.0

        reasons_dict = build_reasons_tradeoffs(
            s, int(round(c.travel_min)), int(c.predicted_state.wait_minutes), tier,
            weather.is_raining if weather else False,
        )

        results.append(MatchResult(
            garage_id=str(g["_id"]),
            garage_name=str(g.get("name", "")),
            tier=tier,
            total_score=round(total_scaled, 2),
            travel_minutes=int(round(c.travel_min)),
            travel_distance_km=round(c.travel_distance_km, 2),
            predicted_arrival=c.arrival_time,
            predicted_wait_minutes=int(c.predicted_state.wait_minutes),
            service_price=int(c.service_price or 0),
            component_scores={k: round(v, 3) for k, v in s.items()},
            reasons=reasons_dict["reasons"],
            trade_offs=reasons_dict["trade_offs"],
            location={"lat": g["location"]["coordinates"][1], "lng": g["location"]["coordinates"][0]},
        ))

    return results


# ── Stage 5: Rank + MMR diversity ────────────────────────────────

def _similarity(a: MatchResult, b: MatchResult) -> float:
    """0 = different, 1 = identical (geo + tier)."""
    la = LatLng(lat=a.location["lat"], lng=a.location["lng"])
    lb = LatLng(lat=b.location["lat"], lng=b.location["lng"])
    dist_m = haversine_meters(la, lb)
    geo_sim = max(0.0, 1.0 - dist_m / 5000.0)    # within 5km → similar
    tier_sim = 1.0 if a.tier == b.tier else 0.5
    return 0.7 * geo_sim + 0.3 * tier_sim


def stage5_rank_diverse(
    scored: List[MatchResult], k: int = 3, lambda_: float = 0.7,
) -> List[MatchResult]:
    """MMR — mix relevance with diversity."""
    if not scored:
        return []
    remaining = sorted(scored, key=lambda r: r.total_score, reverse=True)
    selected: List[MatchResult] = [remaining.pop(0)]

    while remaining and len(selected) < k:
        best_idx = 0
        best_mmr = float("-inf")
        for idx, cand in enumerate(remaining):
            max_sim = max(_similarity(cand, s) for s in selected)
            mmr = lambda_ * cand.total_score - (1.0 - lambda_) * max_sim * 100.0
            if mmr > best_mmr:
                best_mmr = mmr
                best_idx = idx
        selected.append(remaining.pop(best_idx))

    # Assign ranks
    for rk, m in enumerate(selected, start=1):
        m.rank = rk
    return selected


# ── Top-level entry ─────────────────────────────────────────────

async def find_best_garages(
    current_location: LatLng,
    service_type_code: str,
    vehicle_id: Optional[str] = None,
    vehicle_type: Optional[str] = None,
    requested_time: Optional[datetime] = None,
    max_travel_minutes: int = DEFAULT_MAX_TRAVEL_MIN,
    must_have_amenities: Optional[List[str]] = None,
    excluded_garage_ids: Optional[List[str]] = None,
    user_profile: Optional[dict] = None,
    top_k: int = 3,
) -> Dict[str, Any]:
    """
    Full pipeline. Returns dict with 'matches', 'context', 'weights', etc.
    """
    now = get_current_time()
    requested_time = requested_time or now
    must_have_amenities = must_have_amenities or []
    excluded_garage_ids = excluded_garage_ids or []

    # Derive vehicle tier
    vehicle_min_tier = 1
    if vehicle_id:
        void = convert_mongo_object_id(vehicle_id)
        if void:
            v = await VehicleModel.collection.find_one({"_id": void})
            if v:
                vehicle_min_tier = int(v.get("minimum_garage_tier", 1))
    elif vehicle_type:
        from app.api.vehicle.vehicle_models import VEHICLE_TIER_MAP
        vehicle_min_tier = int(VEHICLE_TIER_MAP.get(vehicle_type, 1))

    # Context flags
    is_peak = _is_peak_hour(requested_time)

    # Stage 1
    candidates = await stage1_filter(
        current_location=current_location,
        vehicle_min_tier=vehicle_min_tier,
        service_type_code=service_type_code,
        max_travel_minutes=max_travel_minutes,
        must_have_amenities=must_have_amenities,
        excluded_garage_ids=excluded_garage_ids,
        requested_time=requested_time,
    )

    # Stage 2
    traffic_mult = 1.15 if is_peak else 1.0
    enriched = await stage2_enrich(
        candidates, current_location, service_type_code, requested_time, traffic_mult,
    )

    # Stage 3+4
    weather = enriched[0].weather_at_arrival if enriched else None
    area_demand = "normal"
    if weather and weather.precipitation_mm_last_hour > 5:
        area_demand = "surge"

    scored = await stage3_score(
        enriched, vehicle_min_tier, user_profile, weather, is_peak, area_demand,
    )

    # Stage 5
    top = stage5_rank_diverse(scored, k=top_k)

    # Compute weights used (for logging)
    prefs = (user_profile or {}).get("preferences") or {}
    weights = compute_context_weights(
        is_raining=(weather is not None and weather.is_raining),
        is_peak_hour=is_peak,
        price_sensitivity=str(prefs.get("price_sensitivity", "medium")),
        has_affinity_history=bool((user_profile or {}).get("garage_affinity")),
        area_demand=area_demand,
    )

    return {
        "matches": top,
        "all_scored_count": len(scored),
        "context": {
            "weather": weather.condition if weather else "unknown",
            "is_raining": weather.is_raining if weather else False,
            "is_peak_hour": is_peak,
            "area_demand": area_demand,
            "traffic_multiplier": traffic_mult,
        },
        "weights": {k: round(v, 3) for k, v in weights.items()},
    }
