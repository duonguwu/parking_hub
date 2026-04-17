# -*- coding: utf-8 -*-
"""Tests for Tenant module — admin management (POST API)."""
import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


class TestTenantList:
    async def test_list_tenants_as_admin(self, client: AsyncClient, superadmin_cookies,
                                          registered_garage):
        resp = await client.post("/tenant/get_all", json={},
                                  cookies=superadmin_cookies)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_list_tenants_forbidden_for_customer(self, client: AsyncClient,
                                                         registered_customer):
        cookies = registered_customer["cookies"]
        resp = await client.post("/tenant/get_all", json={}, cookies=cookies)
        assert resp.status_code == 403

    async def test_list_tenants_forbidden_for_garage_owner(self, client: AsyncClient,
                                                             registered_garage):
        cookies = registered_garage["cookies"]
        resp = await client.post("/tenant/get_all", json={}, cookies=cookies)
        assert resp.status_code == 403


class TestTenantDetail:
    async def test_get_tenant_by_id(self, client: AsyncClient, superadmin_cookies,
                                      registered_garage):
        list_resp = await client.post("/tenant/get_all", json={},
                                       cookies=superadmin_cookies)
        tenant_id = list_resp.json()["data"][0]["id"]

        resp = await client.post("/tenant/get_by_id",
                                  json={"id": tenant_id},
                                  cookies=superadmin_cookies)
        assert resp.status_code == 200
        tenant = resp.json()["data"]
        assert tenant["id"] == tenant_id
        assert tenant["name"] != ""
        assert tenant["status"] in ["active", "pending", "suspended"]


class TestTenantUpdate:
    async def test_update_tenant(self, client: AsyncClient, superadmin_cookies,
                                   registered_garage):
        list_resp = await client.post("/tenant/get_all", json={},
                                       cookies=superadmin_cookies)
        tenant_id = list_resp.json()["data"][0]["id"]

        resp = await client.post("/tenant/update", cookies=superadmin_cookies, json={
            "id": tenant_id,
            "subscription_plan": "pro",
        })
        assert resp.status_code == 200

    async def test_update_tenant_forbidden_for_customer(self, client: AsyncClient,
                                                          superadmin_cookies,
                                                          registered_customer,
                                                          registered_garage):
        list_resp = await client.post("/tenant/get_all", json={},
                                       cookies=superadmin_cookies)
        tenant_id = list_resp.json()["data"][0]["id"]

        cookies = registered_customer["cookies"]
        resp = await client.post("/tenant/update", cookies=cookies, json={
            "id": tenant_id,
            "status": "suspended",
        })
        assert resp.status_code == 403
