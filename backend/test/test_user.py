# -*- coding: utf-8 -*-
"""Tests for User module — staff management (POST API)."""
import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


class TestUserList:
    async def test_list_users_as_garage_owner(self, client: AsyncClient, registered_garage):
        cookies = registered_garage["cookies"]
        resp = await client.post("/user/get_all", json={}, cookies=cookies)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_list_users_as_admin(self, client: AsyncClient, superadmin_cookies,
                                        registered_garage):
        resp = await client.post("/user/get_all", json={},
                                  cookies=superadmin_cookies)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data) >= 2


class TestUserCreate:
    async def test_create_staff_user(self, client: AsyncClient, registered_garage):
        cookies = registered_garage["cookies"]
        resp = await client.post("/user/create", cookies=cookies, json={
            "username": "staff_washer_01",
            "email": "washer01@test.com",
            "phone": "0933333333",
            "password": "Staff@123456",
            "name": "Nguyễn Thợ Rửa",
            "role": "garage_staff",
            "staff_profile": {
                "position": "washer",
                "shift": "morning",
            },
        })
        assert resp.status_code == 200
        user = resp.json()["data"]
        assert user["role"] == "garage_staff"
        assert user["staff_profile"]["position"] == "washer"

    async def test_create_manager_user(self, client: AsyncClient, registered_garage):
        cookies = registered_garage["cookies"]
        resp = await client.post("/user/create", cookies=cookies, json={
            "username": "manager_01",
            "email": "manager01@test.com",
            "phone": "0944444444",
            "password": "Manager@123456",
            "name": "Lê Quản Lý",
            "role": "garage_manager",
        })
        assert resp.status_code == 200
        assert resp.json()["data"]["role"] == "garage_manager"

    async def test_create_invalid_role(self, client: AsyncClient, registered_garage):
        cookies = registered_garage["cookies"]
        resp = await client.post("/user/create", cookies=cookies, json={
            "username": "hacker_01",
            "email": "hacker@test.com",
            "password": "Hack@123456",
            "name": "Hacker",
            "role": "super_admin",
        })
        assert resp.status_code == 400

    async def test_customer_cannot_create_users(self, client: AsyncClient,
                                                  registered_customer):
        cookies = registered_customer["cookies"]
        resp = await client.post("/user/create", cookies=cookies, json={
            "username": "notallowed",
            "email": "no@test.com",
            "password": "Test@123456",
            "name": "Not Allowed",
        })
        assert resp.status_code == 403


class TestUserUpdate:
    async def test_update_user(self, client: AsyncClient, registered_garage):
        cookies = registered_garage["cookies"]
        list_resp = await client.post("/user/get_all", json={}, cookies=cookies)
        users = list_resp.json()["data"]
        staff = next((u for u in users if u["role"] == "garage_staff"), None)

        if staff:
            resp = await client.post("/user/update", cookies=cookies, json={
                "id": staff["id"],
                "staff_profile": {"position": "washer", "shift": "full"},
            })
            assert resp.status_code == 200


class TestUserDeactivate:
    async def test_deactivate_user(self, client: AsyncClient, registered_garage):
        cookies = registered_garage["cookies"]
        list_resp = await client.post("/user/get_all", json={}, cookies=cookies)
        users = list_resp.json()["data"]
        staff = next((u for u in users if u["role"] == "garage_staff"), None)

        if staff:
            resp = await client.post("/user/delete", cookies=cookies,
                                      json={"id": staff["id"]})
            assert resp.status_code == 200

    async def test_cannot_deactivate_self(self, client: AsyncClient, registered_garage):
        cookies = registered_garage["cookies"]
        me_resp = await client.get("/auth/me", cookies=cookies)
        my_id = me_resp.json()["data"]["user_id"]

        resp = await client.post("/user/delete", cookies=cookies,
                                  json={"id": my_id})
        assert resp.status_code == 400
        assert "yourself" in resp.json()["detail"]
