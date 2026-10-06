# -*- coding: utf-8 -*-
"""Tests for Capacity endpoints — cập nhật số xe trong bãi + dự đoán chỗ trống."""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestCapacityPublicEndpoints:
    async def test_current_and_predicted(
        self, client: AsyncClient, configured_garage,
    ):
        """Public — tài xế xem chỗ trống của bất kỳ bãi nào, không cần đăng nhập."""
        resp = await client.post(
            "/capacity/current_and_predicted",
            json={"garage_id": configured_garage["garage_id"],
                  "horizons_min": [15, 30, 60]},
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()["data"]
        assert {"has_data", "total_spots", "available", "status"} <= set(data["current"])
        assert set(data["predicted"].keys()) == {"t+15min", "t+30min", "t+60min"}
        for h in data["predicted"].values():
            assert "expected_available" in h
            assert "occupancy_rate" in h
            assert "confidence" in h


class TestCapacityUpdate:
    async def test_garage_owner_can_update_occupancy(
        self, client: AsyncClient, configured_garage,
    ):
        resp = await client.post(
            "/capacity/update_occupancy",
            cookies=configured_garage["cookies"],
            json={"garage_id": configured_garage["garage_id"], "occupied": 5},
        )
        assert resp.status_code == 200, resp.text

        detail = await client.post(
            "/capacity/current_and_predicted",
            json={"garage_id": configured_garage["garage_id"]},
        )
        current = detail.json()["data"]["current"]
        assert current["has_data"] is True
        assert current["occupied"] == 5
        assert current["available"] == current["total_spots"] - 5 - current["held"]

    async def test_occupancy_clamped_to_capacity(
        self, client: AsyncClient, configured_garage,
    ):
        resp = await client.post(
            "/capacity/update_occupancy",
            cookies=configured_garage["cookies"],
            json={"garage_id": configured_garage["garage_id"], "occupied": 99999},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["occupied"] == data["total_spots"]
        # trả lại trạng thái bình thường cho các test sau
        await client.post(
            "/capacity/update_occupancy",
            cookies=configured_garage["cookies"],
            json={"garage_id": configured_garage["garage_id"], "occupied": 0},
        )

    async def test_customer_cannot_update_occupancy(
        self, client: AsyncClient, configured_garage, registered_customer,
    ):
        resp = await client.post(
            "/capacity/update_occupancy",
            cookies=registered_customer["cookies"],
            json={"garage_id": configured_garage["garage_id"], "occupied": 5},
        )
        assert resp.status_code == 403
