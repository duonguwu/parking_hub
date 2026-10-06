# -*- coding: utf-8 -*-
"""
Tạo tài khoản test cho đủ các vai trò (idempotent).

Chạy trong container backend:
    docker exec -i parkinghub-backend-app python - < scripts/create_test_accounts.py

Mật khẩu chung: test123@
"""
import asyncio

from app.db.mongo import init_mongo
from app.api.auth.auth_utils import (
    get_user_by_username, hash_password, register_customer, register_garage,
)
from app.api.shared.tool.datetime_convert import get_current_time

PASSWORD = "test123@"
OWNER_TENANT = "bai-xe-test-q1"


async def _insert_user(username, name, role, tenant_id, email):
    from app.api.user.user_models import UserModel
    if await get_user_by_username(username):
        return "exists"
    now = get_current_time()
    await UserModel.collection.insert_one({
        "tenant_id": tenant_id, "username": username, "email": email,
        "phone": "0900000000", "password_hash": hash_password(PASSWORD),
        "name": name, "role": role, "is_active": True,
        "allowed_tenant_ids": [], "customer_profile": {}, "staff_profile": {},
        "created_at": now, "updated_at": now,
        "created_by": "test_seed", "updated_by": "test_seed",
    })
    return "created"


async def main():
    init_mongo()
    results = {}

    # Chủ bãi — tạo kèm tenant + 1 bãi đỗ (Q1, gần chợ Bến Thành)
    if await get_user_by_username("owner"):
        results["owner"] = "exists"
    else:
        await register_garage({
            "username": "owner", "email": "owner@test.parkinghub.asia",
            "phone": "0900000001", "password": PASSWORD, "owner_name": "Chủ Bãi Test",
            "garage_name": "Bai Xe Test Q1", "address_street": "45 Lê Lợi",
            "address_district": "Quận 1", "address_city": "TP. Hồ Chí Minh",
            "latitude": 10.7725, "longitude": 106.6980, "total_bays": 50,
        })
        results["owner"] = "created"

    from app.api.user.user_models import UserModel
    owner = await UserModel.collection.find_one({"username": "owner"})
    tenant = owner["tenant_id"]

    results["manager"] = await _insert_user("manager", "Quản Lý Bãi Test", "garage_manager", tenant, "manager@test.parkinghub.asia")
    results["staff"] = await _insert_user("staff", "Bảo Vệ Test", "garage_staff", tenant, "staff@test.parkinghub.asia")
    results["ops"] = await _insert_user("ops", "Vận Hành Nền Tảng", "platform_ops", "platform", "ops@test.parkinghub.asia")
    results["fleet"] = await _insert_user("fleet", "Quản Lý Đội Xe", "fleet_manager", "platform", "fleet@test.parkinghub.asia")
    results["admin"] = await _insert_user("admin", "Admin Test", "super_admin", "super_admin", "admin@test.parkinghub.asia")

    if await get_user_by_username("driver"):
        results["driver"] = "exists"
    else:
        await register_customer({
            "username": "driver", "email": "driver@test.parkinghub.asia",
            "phone": "0900000002", "password": PASSWORD, "name": "Tài Xế Test",
        })
        results["driver"] = "created"

    for k, v in results.items():
        print(f"{k:8s} {v}")
    print(f"owner tenant: {tenant}")


asyncio.run(main())
