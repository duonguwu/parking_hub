# -*- coding: utf-8 -*-
"""Unit tests for matching pipeline behavior that must not depend on MongoDB."""
from datetime import datetime, timezone

import pytest

from app.api.matching import matching_engine
from app.api.matching.matching_engine import (
    _build_candidate_query, stage2_enrich, stage3_score,
)
from app.services.osm.osm_client import LatLng, Matrix, estimate_route
from app.services.weather.weather_service import WeatherSnapshot


def test_stage1_applies_vehicle_minimum_tier():
    query = _build_candidate_query(
        current_location=LatLng(lat=10.78, lng=106.68),
        vehicle_min_tier=3,
        service_type_code="park_hourly",
        max_travel_minutes=30,
        must_have_amenities=[],
        excluded_garage_ids=[],
    )

    assert query["grade"] == {"$gte": 3}


@pytest.mark.asyncio
async def test_stage2_uses_requested_time_and_estimates_missing_matrix_cells(monkeypatch):
    origin = LatLng(lat=10.78, lng=106.68)
    destination = LatLng(lat=10.79, lng=106.70)
    expected_fallback = estimate_route(origin, destination)
    requested_time = datetime(2026, 10, 8, 2, 0, tzinfo=timezone.utc)
    garage = {
        "_id": "garage-1",
        "location": {"type": "Point", "coordinates": [destination.lng, destination.lat]},
        "capacity": {"total_spots": 20},
    }

    async def fake_matrix(origins, destinations):
        return Matrix(
            durations=[[None]],
            distances=[[None]],
            confidence=0.5,
            sources_count=1,
            destinations_count=1,
        )

    async def fake_weather(lat, lng):
        return WeatherSnapshot(condition="clear")

    async def fake_prediction(candidate, arrival):
        return {"expected_available": 10, "confidence": 0.3, "at": arrival.isoformat()}

    async def fake_service_price_doc(garage_id, service_type_code):
        return None

    monkeypatch.setattr(matching_engine.osm_client, "get_matrix", fake_matrix)
    monkeypatch.setattr(matching_engine.weather_service, "current", fake_weather)
    monkeypatch.setattr(matching_engine, "predict_availability", fake_prediction)
    monkeypatch.setattr(matching_engine, "_find_service_price_doc", fake_service_price_doc)

    enriched = await stage2_enrich(
        [garage], origin, "park_hourly", requested_time, traffic_multiplier=1.0,
    )

    assert len(enriched) == 1
    candidate = enriched[0]
    assert candidate.travel_min == pytest.approx(expected_fallback.duration_seconds / 60.0)
    assert candidate.travel_distance_km == pytest.approx(expected_fallback.distance_meters / 1000.0)
    assert candidate.arrival_time == requested_time + matching_engine.timedelta(
        seconds=expected_fallback.duration_seconds,
    )
    assert candidate.service_price is None


@pytest.mark.asyncio
async def test_stage3_fit_uses_vehicle_and_garage_tiers():
    requested_time = datetime(2026, 10, 8, 2, 0, tzinfo=timezone.utc)
    candidate = matching_engine.EnrichedCandidate(
        garage={
            "_id": "garage-1",
            "name": "Tier 2 Garage",
            "grade": 2,
            "quality_score": 70,
            "location": {"coordinates": [106.70, 10.79]},
            "capacity": {"total_spots": 20},
            "attributes": {"cover": "open"},
            "stats": {},
        },
        travel_min=10,
        travel_distance_km=3,
        route_confidence=1.0,
        arrival_time=requested_time,
        predicted={"expected_available": 10},
        weather_at_arrival=WeatherSnapshot(condition="clear"),
        service_price=None,
    )

    results = await stage3_score(
        [candidate],
        vehicle_min_tier=3,
        user_profile=None,
        weather=candidate.weather_at_arrival,
        is_peak_hour=False,
        area_demand="normal",
    )

    assert results[0].component_scores["fit"] == 0.0
    assert results[0].component_scores["price"] == 0.7
