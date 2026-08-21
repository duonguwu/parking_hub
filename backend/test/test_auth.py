# -*- coding: utf-8 -*-
"""Tests for Auth module — register, login, refresh, logout, me."""
import pytest
from app.core.config import settings
from httpx import AsyncClient, ASGITransport


pytestmark = pytest.mark.asyncio


# ═══════════════════════════════════════════════════════════════════
# 1. HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════

class TestHealthCheck:
    async def test_root(self, client: AsyncClient):
        resp = await client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["app"] == settings.APP_NAME

    async def test_health(self, client: AsyncClient):
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["api"] == "ok"
        assert data["mongodb"] == "ok"


# ═══════════════════════════════════════════════════════════════════
# 2. CUSTOMER REGISTRATION
# ═══════════════════════════════════════════════════════════════════

class TestCustomerRegistration:
    async def test_register_customer_success(self, registered_customer, customer_data):
        """Customer registered via fixture — verify response structure."""
        body = registered_customer["response"]
        assert body["status"] == "ok"
        assert body["data"]["user"]["username"] == customer_data["username"]
        assert body["data"]["user"]["role"] == "customer"
        assert body["data"]["user"]["tenant_id"] == "platform"

    async def test_register_duplicate_username(self, client: AsyncClient, customer_data,
                                                registered_customer):
        resp = await client.post("/auth/register", json=customer_data)
        assert resp.status_code == 409
        assert "already exists" in resp.json()["detail"]

    async def test_register_invalid_data(self, client: AsyncClient):
        resp = await client.post("/auth/register", json={
            "username": "ab",
            "email": "bad",
            "phone": "123",
            "password": "12345",
            "name": "",
        })
        assert resp.status_code == 422


# ═══════════════════════════════════════════════════════════════════
# 3. GARAGE REGISTRATION
# ═══════════════════════════════════════════════════════════════════

class TestGarageRegistration:
    async def test_register_garage_success(self, registered_garage, garage_owner_data):
        body = registered_garage["response"]
        assert body["status"] == "ok"
        user = body["data"]["user"]
        assert user["username"] == garage_owner_data["username"]
        assert user["role"] == "garage_owner"
        assert user["tenant_id"] != ""
        assert user["tenant_id"] != "platform"

    async def test_register_garage_duplicate(self, client: AsyncClient, garage_owner_data,
                                              registered_garage):
        resp = await client.post("/auth/register-garage", json=garage_owner_data)
        assert resp.status_code == 409


# ═══════════════════════════════════════════════════════════════════
# 4. LOGIN
# ═══════════════════════════════════════════════════════════════════

class TestLogin:
    async def test_login_customer_by_username(self, client: AsyncClient, customer_data,
                                               registered_customer):
        resp = await client.post("/auth/login", json={
            "username": customer_data["username"],
            "password": customer_data["password"],
        })
        assert resp.status_code == 200
        assert resp.json()["data"]["user"]["role"] == "customer"
        assert "access_token" in resp.cookies

    async def test_login_customer_by_email(self, client: AsyncClient, customer_data,
                                            registered_customer):
        resp = await client.post("/auth/login", json={
            "username": customer_data["email"],
            "password": customer_data["password"],
        })
        assert resp.status_code == 200

    async def test_login_garage_owner(self, client: AsyncClient, garage_owner_data,
                                       registered_garage):
        resp = await client.post("/auth/login", json={
            "username": garage_owner_data["username"],
            "password": garage_owner_data["password"],
        })
        assert resp.status_code == 200
        assert resp.json()["data"]["user"]["role"] == "garage_owner"

    async def test_login_superadmin(self, client: AsyncClient):
        resp = await client.post("/auth/login", json={
            "username": "superadmin",
            "password": "TestAdmin@2026",
        })
        assert resp.status_code == 200
        user = resp.json()["data"]["user"]
        assert user["role"] == "super_admin"
        assert user["tenant_id"] == "super_admin"

    async def test_login_wrong_password(self, client: AsyncClient, customer_data,
                                         registered_customer):
        resp = await client.post("/auth/login", json={
            "username": customer_data["username"],
            "password": "wrongpassword",
        })
        assert resp.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        resp = await client.post("/auth/login", json={
            "username": "nobody",
            "password": "anything",
        })
        assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════════
# 5. AUTH ME + REFRESH + LOGOUT
# ═══════════════════════════════════════════════════════════════════

class TestAuthFlow:
    async def test_get_me_authenticated(self, client: AsyncClient, registered_customer):
        resp = await client.get("/auth/me", cookies=registered_customer["cookies"])
        assert resp.status_code == 200
        user = resp.json()["data"]
        assert user["username"] == "customer_test"
        assert user["role"] == "customer"

    async def test_get_me_unauthenticated(self):
        """Request without cookies → 401."""
        from main import app as test_app
        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as fresh:
            resp = await fresh.get("/auth/me")
            assert resp.status_code == 401

    async def test_refresh_token(self, client: AsyncClient, registered_customer):
        resp = await client.post("/auth/refresh", cookies=registered_customer["cookies"])
        assert resp.status_code == 200
        assert resp.json()["message"] == "Token refreshed successfully"

    async def test_logout(self, client: AsyncClient, customer_data, registered_customer):
        login_resp = await client.post("/auth/login", json={
            "username": customer_data["username"],
            "password": customer_data["password"],
        })
        cookies = dict(login_resp.cookies)
        resp = await client.post("/auth/logout", cookies=cookies)
        assert resp.status_code == 200
        assert resp.json()["message"] == "Logged out successfully"
