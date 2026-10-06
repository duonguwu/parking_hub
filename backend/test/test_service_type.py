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
        # 8 mục danh mục chuẩn
        assert {"park_hourly", "park_overnight", "park_daily", "park_workday", "park_monthly",
                "ev_charging", "car_wash", "valet"} == codes
        orders = [st["sort_order"] for st in data]
        assert orders == sorted(orders)

    async def test_rest_list(self, client: AsyncClient):
        resp = await client.get("/service-types")
        assert resp.status_code == 200
        assert resp.json()["data"][0]["code"] == "park_hourly"

    async def test_get_by_code(self, client: AsyncClient):
        resp = await client.post("/service-types/get_by_code", json={"code": "park_monthly"})
        assert resp.status_code == 200
        d = resp.json()["data"]
        assert d["code"] == "park_monthly"
        assert d["category"] == "subscription"
        assert d["unit"] == "month"
        assert d["default_pricing"]["mode"] == "flat"

    async def test_get_by_code_not_found(self, client: AsyncClient):
        resp = await client.post("/service-types/get_by_code", json={"code": "nonexistent"})
        assert resp.status_code == 404
