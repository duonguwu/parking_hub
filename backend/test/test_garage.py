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
            "is_accepting_bookings": True,
        })
        assert resp.status_code == 200


class TestGarageProfile:
    async def test_owner_updates_capacity_and_attributes(self, client: AsyncClient, registered_garage):
        cookies = registered_garage["cookies"]
        resp = await client.put("/garage-portal/garage", cookies=cookies, json={
            "capacity": {"total_spots": 40, "reservable_ratio": 0.5},
            "attributes": {"cover": "basement", "ev_chargers": {"count": 2}},
        })
        assert resp.status_code == 200, resp.text

        detail = await client.get("/garage-portal/garage", cookies=cookies)
        g = detail.json()["data"]
        assert g["capacity"]["total_spots"] == 40
        assert g["capacity"]["reservable_ratio"] == 0.5

    async def test_owner_cannot_set_integration_level(self, client: AsyncClient, registered_garage):
        cookies = registered_garage["cookies"]
        before = (await client.get("/garage-portal/garage", cookies=cookies)).json()["data"]
        await client.put("/garage-portal/garage", cookies=cookies, json={"integration_level": 4})
        after = (await client.get("/garage-portal/garage", cookies=cookies)).json()["data"]
        assert after["integration_level"] == before["integration_level"]


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

    async def test_search_nearby_grade_filter(self, client: AsyncClient, registered_garage):
        resp = await client.post("/garage/search_nearby", json={
            "latitude": 10.7800,
            "longitude": 106.6900,
            "max_distance_km": 15,
            "min_grade": 5,
        })
        assert resp.status_code == 200
        assert all(g["grade"] >= 5 for g in resp.json()["data"])
