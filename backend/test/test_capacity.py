# -*- coding: utf-8 -*-
"""Tests for Capacity endpoints — real-time update + prediction."""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestCapacityPublicEndpoints:
    async def test_current_and_predicted(
        self, client: AsyncClient, configured_garage,
    ):
        """Public — customer can see capacity for any garage."""
        resp = await client.post(
            "/capacity/current_and_predicted",
            json={"garage_id": configured_garage["garage_id"],
                  "horizons_min": [15, 30, 60]},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "current" in data
        assert "predicted" in data
        assert set(data["predicted"].keys()) == {"t+15min", "t+30min", "t+60min"}
        for h in data["predicted"].values():
            assert "available_bays" in h
            assert "wait_minutes" in h


class TestCapacityUpdate:
    async def test_garage_owner_can_update_load(
        self, client: AsyncClient, configured_garage,
    ):
        resp = await client.post(
            "/capacity/update_load",
            cookies=configured_garage["cookies"],
            json={
                "garage_id": configured_garage["garage_id"],
                "vehicles_in_service": 2,
                "vehicles_waiting": 1,
            },
        )
        assert resp.status_code == 200

        # Verify it's reflected
        detail = await client.post(
            "/capacity/current_and_predicted",
            json={"garage_id": configured_garage["garage_id"]},
        )
        current = detail.json()["data"]["current"]
        assert current["vehicles_in_service"] == 2
        assert current["vehicles_waiting"] == 1

    async def test_customer_cannot_update_load(
        self, client: AsyncClient, configured_garage, registered_customer,
    ):
        resp = await client.post(
            "/capacity/update_load",
            cookies=registered_customer["cookies"],
            json={
                "garage_id": configured_garage["garage_id"],
                "vehicles_in_service": 5,
                "vehicles_waiting": 5,
            },
        )
        assert resp.status_code == 403
