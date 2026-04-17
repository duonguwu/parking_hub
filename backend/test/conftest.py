# -*- coding: utf-8 -*-
"""
WashMind Test Configuration — Shared fixtures for all tests.

Chạy tests:
    uv run pytest test/ -v
    uv run pytest test/test_auth.py -v        # chỉ chạy auth
    uv run pytest test/ -v -k "test_login"    # chỉ chạy test có tên chứa "login"
"""
import os
import sys
import pytest
from httpx import AsyncClient, ASGITransport

# Add backend root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Force test database BEFORE any app import
os.environ["MONGO_DB"] = "washmind_test"
os.environ["MONGO_URI"] = "mongodb://admin:password123@localhost:27017/washmind_test?authSource=admin"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-washmind-2026"
os.environ["SUPER_ADMIN_USERNAME"] = "superadmin"
os.environ["SUPER_ADMIN_PASSWORD"] = "TestAdmin@2026"

from main import app
from app.db.mongo import init_mongo, close_mongo, get_motor_client


# ── Async HTTP client with DB setup ─────────────────────────────

@pytest.fixture(scope="session")
async def client():
    """
    Async HTTP client with MongoDB initialized.
    ASGITransport does NOT trigger lifespan, so we init DB manually.
    """
    # 1. Init MongoDB + Umongo binding
    init_mongo()
    motor_client = get_motor_client()

    # 2. Drop test DB for clean state
    await motor_client.drop_database("washmind_test")

    # 3. Create indexes
    from app.api.user.user_models import UserModel
    from app.api.tenant.tenant_models import TenantModel
    from app.api.garage.garage_models import GarageModel
    from app.api.vehicle.vehicle_models import VehicleModel

    await UserModel.collection.create_index("username", unique=True)
    await UserModel.collection.create_index("email", unique=True)
    await TenantModel.collection.create_index("slug", unique=True)
    await GarageModel.collection.create_index([("location", "2dsphere")])
    await VehicleModel.collection.create_index("license_plate", unique=True)

    # 4. Seed super admin
    from app.api.auth.auth_utils import seed_super_admin
    await seed_super_admin()

    # 5. Create test client (follow_redirects=False, no cookie persistence)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # 6. Cleanup: drop test DB
    await motor_client.drop_database("washmind_test")
    close_mongo()


# ── Helper: login and get cookies ────────────────────────────────

async def login_and_get_cookies(client: AsyncClient, username: str, password: str) -> dict:
    """Helper to login and extract cookies dict."""
    resp = await client.post("/auth/login", json={
        "username": username,
        "password": password,
    })
    assert resp.status_code == 200, f"Login failed for {username}: {resp.text}"
    return dict(resp.cookies)


# ── Auth helper fixtures ─────────────────────────────────────────

@pytest.fixture(scope="session")
async def superadmin_cookies(client: AsyncClient) -> dict:
    """Login as super admin and return cookies."""
    return await login_and_get_cookies(client, "superadmin", "TestAdmin@2026")


@pytest.fixture(scope="session")
async def customer_data() -> dict:
    return {
        "username": "customer_test",
        "email": "customer@test.com",
        "phone": "0901234567",
        "password": "Test@123456",
        "name": "Nguyễn Văn Test",
    }


@pytest.fixture(scope="session")
async def garage_owner_data() -> dict:
    return {
        "username": "garage_owner_test",
        "email": "garage@test.com",
        "phone": "0912345678",
        "password": "Test@123456",
        "owner_name": "Trần Garage Owner",
        "garage_name": "AutoSpa Test Q3",
        "address_street": "123 Nguyễn Huệ",
        "address_district": "Quận 3",
        "address_city": "TP Hồ Chí Minh",
        "address_province": "HCM",
        "latitude": 10.7834,
        "longitude": 106.6856,
        "total_bays": 3,
    }


@pytest.fixture(scope="session")
async def registered_customer(client: AsyncClient, customer_data: dict) -> dict:
    """Register a customer and return response data + cookies."""
    resp = await client.post("/auth/register", json=customer_data)
    assert resp.status_code == 200, f"Customer register failed: {resp.text}"
    cookies = dict(resp.cookies)
    return {
        "response": resp.json(),
        "cookies": cookies,
    }


@pytest.fixture(scope="session")
async def registered_garage(client: AsyncClient, garage_owner_data: dict) -> dict:
    """Register a garage (creates tenant + user + garage) and return cookies."""
    resp = await client.post("/auth/register-garage", json=garage_owner_data)
    assert resp.status_code == 200, f"Garage register failed: {resp.text}"
    cookies = dict(resp.cookies)
    return {
        "response": resp.json(),
        "cookies": cookies,
    }
