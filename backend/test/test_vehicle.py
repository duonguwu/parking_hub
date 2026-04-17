# -*- coding: utf-8 -*-
"""Tests for Vehicle module — CRUD (POST API)."""
import pytest
from httpx import AsyncClient, ASGITransport


pytestmark = pytest.mark.asyncio


class TestVehicleCreate:
    async def test_create_vehicle(self, client: AsyncClient, registered_customer):
        cookies = registered_customer["cookies"]
        resp = await client.post("/vehicle/create", cookies=cookies, json={
            "license_plate": "51A-12345",
            "brand": "Toyota",
            "model": "Camry",
            "year": 2023,
            "color": "White",
            "vehicle_type": "standard",
            "body_type": "sedan",
            "size_class": "medium",
            "is_default": True,
        })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["license_plate"] == "51A-12345"
        assert data["vehicle_type"] == "standard"
        assert data["minimum_garage_tier"] == 1
        assert data["is_default"] is True

    async def test_create_luxury_vehicle(self, client: AsyncClient, registered_customer):
        cookies = registered_customer["cookies"]
        resp = await client.post("/vehicle/create", cookies=cookies, json={
            "license_plate": "51A-99999",
            "brand": "Mercedes-Benz",
            "model": "S-Class",
            "year": 2024,
            "vehicle_type": "luxury",
            "body_type": "sedan",
        })
        assert resp.status_code == 200
        assert resp.json()["data"]["minimum_garage_tier"] == 3

    async def test_create_duplicate_plate(self, client: AsyncClient, registered_customer):
        cookies = registered_customer["cookies"]
        resp = await client.post("/vehicle/create", cookies=cookies, json={
            "license_plate": "51A-12345",
            "brand": "Honda",
            "model": "Civic",
        })
        assert resp.status_code == 409


class TestVehicleList:
    async def test_list_vehicles(self, client: AsyncClient, registered_customer):
        cookies = registered_customer["cookies"]
        resp = await client.post("/vehicle/get_all", json={}, cookies=cookies)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_list_vehicles_unauthenticated(self):
        from main import app as test_app
        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as fresh:
            resp = await fresh.post("/vehicle/get_all", json={})
            assert resp.status_code == 401


class TestVehicleDetail:
    async def test_get_vehicle(self, client: AsyncClient, registered_customer):
        cookies = registered_customer["cookies"]
        list_resp = await client.post("/vehicle/get_all", json={}, cookies=cookies)
        vehicle_id = list_resp.json()["data"][0]["id"]

        resp = await client.post("/vehicle/get_by_id",
                                  json={"id": vehicle_id}, cookies=cookies)
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == vehicle_id


class TestVehicleUpdate:
    async def test_update_vehicle(self, client: AsyncClient, registered_customer):
        cookies = registered_customer["cookies"]
        list_resp = await client.post("/vehicle/get_all", json={}, cookies=cookies)
        vehicle_id = list_resp.json()["data"][0]["id"]

        resp = await client.post("/vehicle/update", cookies=cookies, json={
            "id": vehicle_id,
            "color": "Black",
            "year": 2025,
        })
        assert resp.status_code == 200

    async def test_update_vehicle_type_updates_tier(self, client: AsyncClient,
                                                      registered_customer):
        cookies = registered_customer["cookies"]
        list_resp = await client.post("/vehicle/get_all", json={}, cookies=cookies)
        vehicles = list_resp.json()["data"]
        std = next((v for v in vehicles if v["vehicle_type"] == "standard"), None)
        if std:
            resp = await client.post("/vehicle/update", cookies=cookies, json={
                "id": std["id"],
                "vehicle_type": "premium",
            })
            assert resp.status_code == 200

            detail = await client.post("/vehicle/get_by_id",
                                        json={"id": std["id"]}, cookies=cookies)
            assert detail.json()["data"]["minimum_garage_tier"] == 2


class TestVehicleDelete:
    async def test_delete_vehicle(self, client: AsyncClient, registered_customer):
        cookies = registered_customer["cookies"]
        create_resp = await client.post("/vehicle/create", cookies=cookies, json={
            "license_plate": "51A-DELETE",
            "brand": "TestBrand",
            "model": "DeleteMe",
        })
        vehicle_id = create_resp.json()["data"]["id"]

        resp = await client.post("/vehicle/delete", cookies=cookies,
                                  json={"id": vehicle_id})
        assert resp.status_code == 200

        list_resp = await client.post("/vehicle/get_all", json={}, cookies=cookies)
        ids = [v["id"] for v in list_resp.json()["data"]]
        assert vehicle_id not in ids
