# -*- coding: utf-8 -*-
"""
Test Configuration — Shared fixtures for all tests.

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
os.environ["MONGO_DB"] = "parkinghub_test"
os.environ["MONGO_URI"] = os.environ.get(
    "TEST_MONGO_URI",
    "mongodb://admin:password123@localhost:27017/parkinghub_test?authSource=admin",
)
if os.environ.get("TEST_REDIS_URL"):
    os.environ["REDIS_URL"] = os.environ["TEST_REDIS_URL"]
os.environ["JWT_SECRET_KEY"] = "test-secret-key-2026"
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
    await motor_client.drop_database("parkinghub_test")

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

    # Phase 2 collections
    from app.api.service_type.service_type_models import ServiceTypeModel
    from app.api.garage_service.garage_service_models import GarageServiceModel
    from app.api.booking.booking_models import BookingModel
    from app.api.capacity.capacity_models import CapacitySnapshotModel
    from app.api.search_log.search_log_models import SearchLogModel
    await ServiceTypeModel.collection.create_index("code", unique=True)
    await GarageServiceModel.collection.create_index(
        [("garage_id", 1), ("service_type_code", 1)], unique=True,
    )
    await BookingModel.collection.create_index("booking_code", unique=True)
    await CapacitySnapshotModel.collection.create_index(
        [("garage_id", 1), ("timestamp", -1)]
    )
    await SearchLogModel.collection.create_index([("created_at", -1)])

    # 4. Seed super admin + service types
    from app.api.auth.auth_utils import seed_super_admin
    from app.api.service_type.service_type_utils import seed_default_service_types
    await seed_super_admin()
    await seed_default_service_types()

    # Connect Redis (best-effort)
    from app.services.shared.redis_client import redis_client
    try:
        await redis_client.connect()
    except Exception:
        pass

    # 5. Create test client (follow_redirects=False, no cookie persistence)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # 6. Cleanup: drop test DB
    await motor_client.drop_database("parkinghub_test")
    close_mongo()

    # Disconnect Redis
    from app.services.shared.redis_client import redis_client
    try:
        await redis_client.disconnect()
    except Exception:
        pass


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
async def registered_garage(
    client: AsyncClient, garage_owner_data: dict, superadmin_cookies: dict,
) -> dict:
    """
    Register a garage (creates tenant + user + garage), then admin approves it.
    Bãi mới đăng ký ở trạng thái pending_review; admin duyệt và đặt cấp tích hợp 3
    (giữ chỗ tự xác nhận) để các luồng đặt chỗ chạy được.
    """
    resp = await client.post("/auth/register-garage", json=garage_owner_data)
    assert resp.status_code == 200, f"Garage register failed: {resp.text}"
    cookies = dict(resp.cookies)

    mine = await client.get("/garage-portal/garage", cookies=cookies)
    assert mine.status_code == 200, f"Load own garage failed: {mine.text}"
    garage_id = mine.json()["data"]["id"]
    approve = await client.patch(
        f"/admin/garages/{garage_id}", cookies=superadmin_cookies,
        json={"status": "active", "integration_level": 3},
    )
    assert approve.status_code == 200, f"Approve garage failed: {approve.text}"
    # Mở cửa 24h để các test tìm bãi không phụ thuộc giờ chạy test
    hours = await client.put("/garage-portal/garage", cookies=cookies, json={"operating_hours": {"is_24h": True}})
    assert hours.status_code == 200, f"Set 24h hours failed: {hours.text}"
    return {
        "response": resp.json(),
        "cookies": cookies,
        "garage_id": garage_id,
    }


@pytest.fixture(scope="session")
async def configured_garage(
    client: AsyncClient, registered_garage: dict, superadmin_cookies: dict,
) -> dict:
    """
    Garage with park_overnight + park_hourly configured.
    Returns {garage_id, cookies (owner), service_type_code, price}.
    """
    garage_id = registered_garage["garage_id"]

    # Configure park_overnight at 150000 VND
    owner_cookies = registered_garage["cookies"]
    upsert_resp = await client.post(
        "/garage-services/upsert",
        cookies=owner_cookies,
        json={
            "garage_id": garage_id,
            "service_type_code": "park_overnight",
            "price": 150000,
            "estimated_duration_minutes": 30,
        },
    )
    assert upsert_resp.status_code == 200, f"Upsert failed: {upsert_resp.text}"

    # Also add park_hourly so customers have a block-priced option
    await client.post(
        "/garage-services/upsert",
        cookies=owner_cookies,
        json={
            "garage_id": garage_id,
            "service_type_code": "park_hourly",
            "price": 80000,
            "estimated_duration_minutes": 20,
        },
    )

    return {
        "garage_id": garage_id,
        "cookies": owner_cookies,
        "service_type_code": "park_overnight",
        "price": 150000,
    }
