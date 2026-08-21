# -*- coding: utf-8 -*-
"""Tests for Garage module — CRUD, capacity update, nearby search (POST API)."""
import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


class TestGarageList:
    async def test_list_garages_as_admin(self, client: AsyncClient, superadmin_cookies,
                                         registered_garage):
        resp = await client.post("/garage/get_all", json={},
                                  cookies=superadmin_cookies)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_list_garages_as_garage_owner(self, client: AsyncClient, registered_garage):
        cookies = registered_garage["cookies"]
        resp = await client.post("/garage/get_all", json={}, cookies=cookies)
        assert resp.status_code == 200
        data = resp.json()["data"]
        # Garage owner should see at least their own garage
        assert len(data) >= 1

    async def test_list_garages_as_customer(self, client: AsyncClient, registered_customer):
        cookies = registered_customer["cookies"]
        resp = await client.post("/garage/get_all", json={}, cookies=cookies)
        assert resp.status_code == 200


class TestGarageDetail:
    async def test_get_garage_by_id(self, client: AsyncClient, superadmin_cookies,
                                     registered_garage):
        list_resp = await client.post("/garage/get_all", json={},
                                       cookies=superadmin_cookies)
        garages = list_resp.json()["data"]
        assert len(garages) > 0
        garage_id = garages[0]["id"]

        resp = await client.post("/garage/get_by_id",
                                  json={"id": garage_id},
                                  cookies=superadmin_cookies)
        assert resp.status_code == 200
        garage = resp.json()["data"]
        assert garage["id"] == garage_id
        assert garage["name"] != ""

    async def test_get_garage_not_found(self, client: AsyncClient, superadmin_cookies):
        resp = await client.post("/garage/get_by_id",
                                  json={"id": "000000000000000000000000"},
                                  cookies=superadmin_cookies)
        assert resp.status_code == 404


class TestGarageUpdate:
    async def test_update_garage(self, client: AsyncClient, registered_garage):
        cookies = registered_garage["cookies"]
        list_resp = await client.post("/garage/get_all", json={}, cookies=cookies)
        data = list_resp.json()["data"]
        if len(data) == 0:
            pytest.skip("No garages found for owner")
        garage_id = data[0]["id"]

        resp = await client.post("/garage/update", cookies=cookies, json={
            "id": garage_id,
            "description": "Bãi đỗ xe mẫu tại Q3",
            "amenities": ["wifi", "coffee", "waiting_area"],
            "is_accepting_bookings": True,
        })
        assert resp.status_code == 200


class TestGarageCapacity:
    async def test_update_capacity(self, client: AsyncClient, registered_garage):
        cookies = registered_garage["cookies"]
        list_resp = await client.post("/garage/get_all", json={}, cookies=cookies)
        data = list_resp.json()["data"]
        if len(data) == 0:
            pytest.skip("No garages found for owner")
        garage_id = data[0]["id"]

        resp = await client.post("/garage/update_capacity", cookies=cookies, json={
            "id": garage_id,
            "vehicles_in_service": 2,
            "vehicles_waiting": 1,
            "estimated_wait_minutes": 15,
        })
        assert resp.status_code == 200

        detail = await client.post("/garage/get_by_id",
                                    json={"id": garage_id}, cookies=cookies)
        load = detail.json()["data"]["current_load"]
        assert load["vehicles_in_service"] == 2
        assert load["vehicles_waiting"] == 1


class TestGarageNearbySearch:
    async def test_search_nearby(self, client: AsyncClient, registered_garage):
        resp = await client.post("/garage/search_nearby", json={
            "latitude": 10.7800,
            "longitude": 106.6900,
            "max_distance_km": 15,
        })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)

    async def test_search_nearby_tier_filter(self, client: AsyncClient, registered_garage):
        resp = await client.post("/garage/search_nearby", json={
            "latitude": 10.7800,
            "longitude": 106.6900,
            "max_distance_km": 15,
            "min_tier": 4,
        })
        assert resp.status_code == 200
        assert len(resp.json()["data"]) == 0
