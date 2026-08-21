# -*- coding: utf-8 -*-
"""Tests for Service Type catalog (public, seeded on startup)."""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestServiceTypeCatalog:
    async def test_list_catalog(self, client: AsyncClient):
        resp = await client.post("/service-types/get_all", json={})
        assert resp.status_code == 200
        data = resp.json()["data"]
        codes = {st["code"] for st in data}
        # 4 mục seed mặc định
        assert {"park_hourly", "park_overnight", "park_daily", "park_monthly"}.issubset(codes)

    async def test_get_by_code(self, client: AsyncClient):
        resp = await client.post("/service-types/get_by_code", json={"code": "park_monthly"})
        assert resp.status_code == 200
        d = resp.json()["data"]
        assert d["code"] == "park_monthly"
        assert d["minimum_tier"] == 2
        assert d["vehicle_type_multiplier"]["luxury"] == 1.0

    async def test_get_by_code_not_found(self, client: AsyncClient):
        resp = await client.post("/service-types/get_by_code", json={"code": "nonexistent"})
        assert resp.status_code == 404
