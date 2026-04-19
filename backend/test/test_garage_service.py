# -*- coding: utf-8 -*-
"""Tests for Garage Services (per-garage service offerings + prices)."""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestGarageServiceConfig:
    async def test_configure_service_adds_to_offered(
        self, client: AsyncClient, configured_garage,
    ):
        garage_id = configured_garage["garage_id"]
        resp = await client.post(
            "/garage-services/list_by_garage",
            json={"garage_id": garage_id},
        )
        assert resp.status_code == 200
        services = resp.json()["data"]
        codes = {s["service_type_code"] for s in services}
        assert "wash_premium" in codes
        premium = next(s for s in services if s["service_type_code"] == "wash_premium")
        assert premium["price"] == 150000

    async def test_upsert_updates_existing(
        self, client: AsyncClient, configured_garage,
    ):
        # Change price
        cookies = configured_garage["cookies"]
        resp = await client.post(
            "/garage-services/upsert",
            cookies=cookies,
            json={
                "garage_id": configured_garage["garage_id"],
                "service_type_code": "wash_basic",
                "price": 95000,
            },
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["price"] == 95000

    async def test_upsert_forbidden_for_other_tenant(
        self, client: AsyncClient, configured_garage, registered_customer,
    ):
        """Customer cannot upsert services for a garage."""
        resp = await client.post(
            "/garage-services/upsert",
            cookies=registered_customer["cookies"],
            json={
                "garage_id": configured_garage["garage_id"],
                "service_type_code": "detailing",
                "price": 500000,
            },
        )
        # Customer role has no "service:create/edit" permission
        assert resp.status_code == 403

    async def test_upsert_invalid_service_type(
        self, client: AsyncClient, configured_garage,
    ):
        resp = await client.post(
            "/garage-services/upsert",
            cookies=configured_garage["cookies"],
            json={
                "garage_id": configured_garage["garage_id"],
                "service_type_code": "not_exist",
                "price": 100000,
            },
        )
        assert resp.status_code == 404

    async def test_remove_service(
        self, client: AsyncClient, configured_garage,
    ):
        # First add a new service (so we don't break other tests by removing wash_basic)
        await client.post(
            "/garage-services/upsert",
            cookies=configured_garage["cookies"],
            json={
                "garage_id": configured_garage["garage_id"],
                "service_type_code": "interior",
                "price": 200000,
            },
        )
        resp = await client.post(
            "/garage-services/remove",
            cookies=configured_garage["cookies"],
            json={
                "garage_id": configured_garage["garage_id"],
                "service_type_code": "interior",
            },
        )
        assert resp.status_code == 200

        # Verify no longer in list
        lst = await client.post(
            "/garage-services/list_by_garage",
            json={"garage_id": configured_garage["garage_id"]},
        )
        codes = {s["service_type_code"] for s in lst.json()["data"]}
        assert "interior" not in codes
