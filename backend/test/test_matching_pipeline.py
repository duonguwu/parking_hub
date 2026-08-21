# -*- coding: utf-8 -*-
"""Tests for /match/search full pipeline (OSM fallback, scoring, logging)."""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestMatchSearch:
    async def test_search_returns_configured_garage(
        self, client: AsyncClient, configured_garage,
    ):
        """
        User near the test garage searching park_overnight should find it.
        Public endpoint, no auth needed.
        """
        resp = await client.post(
            "/match/search",
            json={
                "current_location": {"lat": 10.7835, "lng": 106.6860},
                "service_type_code": "park_overnight",
                "max_travel_minutes": 30,
            },
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()["data"]
        assert data["results_count"] >= 1
        assert "matches" in data

        top = data["matches"][0]
        assert top["garage_id"] == configured_garage["garage_id"]
        assert 0 <= top["total_score"] <= 100
        assert set(top["component_scores"].keys()) >= {
            "distance", "wait", "quality", "fit",
            "affinity", "price", "reliability", "environment",
        }
        assert top["rank"] == 1

    async def test_search_filters_by_tier(
        self, client: AsyncClient, configured_garage,
    ):
        """Vehicle requiring tier 4 (super) should not match a tier-1 garage."""
        resp = await client.post(
            "/match/search",
            json={
                "current_location": {"lat": 10.7835, "lng": 106.6860},
                "service_type_code": "park_overnight",
                "vehicle_type": "super",  # requires tier 4
                "max_travel_minutes": 30,
            },
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        # The test garage defaults to tier 1 → not in results
        assert data["results_count"] == 0 or all(
            m["tier"] >= 4 for m in data["matches"]
        )

    async def test_search_returns_search_id_for_feedback(
        self, client: AsyncClient, configured_garage,
    ):
        resp = await client.post(
            "/match/search",
            json={
                "current_location": {"lat": 10.7835, "lng": 106.6860},
                "service_type_code": "park_overnight",
            },
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["search_id"]   # not empty

        # Feedback endpoint accepts it
        fb = await client.post(
            "/match/feedback",
            json={
                "search_id": data["search_id"],
                "action": "booked",
                "selected_garage_id": configured_garage["garage_id"],
                "selected_rank": 1,
                "time_spent_seconds": 12,
            },
        )
        assert fb.status_code == 200

    async def test_context_weights_returned(
        self, client: AsyncClient, configured_garage,
    ):
        resp = await client.post(
            "/match/search",
            json={
                "current_location": {"lat": 10.7835, "lng": 106.6860},
                "service_type_code": "park_overnight",
            },
        )
        data = resp.json()["data"]
        assert "weights" in data
        w = data["weights"]
        assert sum(w.values()) == pytest.approx(1.0, abs=0.01)
        # Cold-start user → affinity weight should be 0
        assert w["affinity"] == 0

    async def test_feedback_unknown_search_id(self, client: AsyncClient):
        resp = await client.post(
            "/match/feedback",
            json={
                "search_id": "000000000000000000000000",
                "action": "abandoned",
            },
        )
        assert resp.status_code == 404


class TestMatchReasons:
    async def test_reasons_and_tradeoffs_structure(
        self, client: AsyncClient, configured_garage,
    ):
        resp = await client.post(
            "/match/search",
            json={
                "current_location": {"lat": 10.7835, "lng": 106.6860},
                "service_type_code": "park_overnight",
            },
        )
        data = resp.json()["data"]
        assert data["results_count"] >= 1
        top = data["matches"][0]
        assert "reasons" in top
        assert "trade_offs" in top
        # At least distance should be a strong reason (garage very close)
        reason_types = {r["type"] for r in top["reasons"]}
        assert "best_distance" in reason_types or "low_wait" in reason_types or "no_wait" in reason_types
