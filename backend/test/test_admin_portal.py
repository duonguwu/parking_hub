# -*- coding: utf-8 -*-
"""Tests for Admin API (/admin/*) và cổng chủ bãi (/garage-portal/*)."""
from datetime import datetime, timedelta, timezone
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestAdminAccess:
    async def test_customer_forbidden(self, client: AsyncClient, registered_customer):
        resp = await client.get("/admin/overview", cookies=registered_customer["cookies"])
        assert resp.status_code == 403

    async def test_owner_forbidden(self, client: AsyncClient, registered_garage):
        resp = await client.patch(f"/admin/garages/{registered_garage['garage_id']}",
                                  cookies=registered_garage["cookies"], json={"integration_level": 4})
        assert resp.status_code == 403


class TestAdminGarages:
    async def test_overview(self, client: AsyncClient, superadmin_cookies, registered_garage):
        resp = await client.get("/admin/overview", cookies=superadmin_cookies)
        assert resp.status_code == 200, resp.text
        data = resp.json()["data"]
        assert data["garages"]["active"] >= 1
        assert len(data["daily"]) == 30
        assert {b["level"] for b in data["by_level"]} == {1, 2, 3, 4}

    async def test_list_and_map(self, client: AsyncClient, superadmin_cookies, registered_garage):
        resp = await client.get("/admin/garages?status=active", cookies=superadmin_cookies)
        assert resp.status_code == 200
        ids = [g["id"] for g in resp.json()["data"]["items"]]
        assert registered_garage["garage_id"] in ids

        m = await client.get("/admin/map", cookies=superadmin_cookies)
        assert m.status_code == 200
        assert any(g["id"] == registered_garage["garage_id"] for g in m.json()["data"])

    async def test_meta(self, client: AsyncClient, superadmin_cookies):
        resp = await client.get("/admin/meta", cookies=superadmin_cookies)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data["integration_levels"]) == 4
        assert data["grade_checklist"]

    async def test_assessment_sets_grade(self, client: AsyncClient, superadmin_cookies, registered_garage):
        gid = registered_garage["garage_id"]
        meta = (await client.get("/admin/meta", cookies=superadmin_cookies)).json()["data"]
        items = {c["key"]: True for c in meta["grade_checklist"]}
        resp = await client.put(f"/admin/garages/{gid}/assessment", cookies=superadmin_cookies,
                                json={"items": items, "note": "Đạt toàn bộ"})
        assert resp.status_code == 200, resp.text
        g = resp.json()["data"]["garage"]
        assert g["grade"] == 5
        assert g["is_verified"] is True

    async def test_invalid_level_rejected(self, client: AsyncClient, superadmin_cookies, registered_garage):
        resp = await client.patch(f"/admin/garages/{registered_garage['garage_id']}",
                                  cookies=superadmin_cookies, json={"integration_level": 7})
        assert resp.status_code == 422


class TestAdminUsersAndCatalog:
    async def test_list_users_by_role(self, client: AsyncClient, superadmin_cookies, registered_customer):
        resp = await client.get("/admin/users?role=customer", cookies=superadmin_cookies)
        assert resp.status_code == 200
        items = resp.json()["data"]["items"]
        assert items and all(u["role"] == "customer" for u in items)
        assert all("password_hash" not in u for u in items)

    async def test_cannot_lock_super_admin(self, client: AsyncClient, superadmin_cookies):
        users = (await client.get("/admin/users?role=super_admin", cookies=superadmin_cookies)).json()["data"]["items"]
        resp = await client.patch(f"/admin/users/{users[0]['id']}", cookies=superadmin_cookies,
                                  json={"is_active": False})
        assert resp.status_code == 403

    async def test_service_type_create_and_hide(self, client: AsyncClient, superadmin_cookies):
        resp = await client.post("/admin/service-types", cookies=superadmin_cookies, json={
            "code": "tire_check", "name": "Kiểm tra lốp", "category": "addon", "unit": "session",
        })
        assert resp.status_code == 200, resp.text
        upd = await client.patch("/admin/service-types/tire_check", cookies=superadmin_cookies,
                                 json={"is_active": False})
        assert upd.status_code == 200
        public = (await client.get("/service-types")).json()["data"]
        assert "tire_check" not in {s["code"] for s in public}


class TestGaragePortal:
    async def test_dashboard_overview(self, client: AsyncClient, configured_garage):
        resp = await client.get("/garage-portal/dashboard/overview", cookies=configured_garage["cookies"])
        assert resp.status_code == 200, resp.text
        data = resp.json()["data"]
        assert data["garage"]["id"] == configured_garage["garage_id"]
        assert {"today", "yesterday", "unpaid_count"} <= set(data["revenue"])

    async def test_capacity_chart(self, client: AsyncClient, configured_garage):
        for r in ("24H", "7D"):
            resp = await client.get(f"/garage-portal/dashboard/capacity?range={r}",
                                    cookies=configured_garage["cookies"])
            assert resp.status_code == 200
            assert len(resp.json()["data"]["labels"]) == 24

    async def test_walk_in_then_checkout(self, client: AsyncClient, configured_garage):
        cookies = configured_garage["cookies"]
        resp = await client.post("/garage-portal/walk-ins", cookies=cookies,
                                 json={"license_plate": "59C-11111", "service_type_code": "park_hourly"})
        assert resp.status_code == 200, resp.text
        bid = resp.json()["data"]["id"]

        dup = await client.post("/garage-portal/walk-ins", cookies=cookies,
                                json={"license_plate": "59C-11111", "service_type_code": "park_hourly"})
        assert dup.status_code == 409

        inside = (await client.get("/garage-portal/bookings?tab=inside", cookies=cookies)).json()["data"]
        assert any(i["id"] == bid for i in inside["items"])
        assert all("current_charge" in i for i in inside["items"])

        out = await client.post(f"/garage-portal/bookings/{bid}/actions", cookies=cookies,
                                json={"action": "checkout", "payment_method": "transfer"})
        assert out.status_code == 200, out.text
        assert out.json()["data"]["status"] == "checked_out"

    async def test_bookings_search_by_plate(self, client: AsyncClient, configured_garage, registered_customer):
        start = datetime.now(timezone.utc) + timedelta(days=20)
        await client.post("/bookings/create", cookies=registered_customer["cookies"], json={
            "garage_id": configured_garage["garage_id"], "service_type_code": "park_hourly",
            "start_time": start.isoformat(), "end_time": (start + timedelta(hours=2)).isoformat(),
            "license_plate": "43A-77777",
        })
        resp = await client.get("/garage-portal/bookings?tab=upcoming&q=43a-777", cookies=configured_garage["cookies"])
        assert resp.status_code == 200
        items = resp.json()["data"]["items"]
        assert items and all("43A-777" in i["license_plate"] for i in items)

    async def test_analytics_and_score(self, client: AsyncClient, configured_garage):
        a = await client.get("/garage-portal/analytics?range=7D", cookies=configured_garage["cookies"])
        assert a.status_code == 200, a.text
        assert len(a.json()["data"]["revenue_chart"]["labels"]) == 7
        s = await client.get("/garage-portal/score", cookies=configured_garage["cookies"])
        assert s.status_code == 200, s.text
        assert s.json()["data"]["tips"]

    async def test_services_crud(self, client: AsyncClient, configured_garage):
        cookies = configured_garage["cookies"]
        ov = (await client.get("/garage-portal/services", cookies=cookies)).json()["data"]
        codes = {s["service_type_code"] for s in ov["services"]}
        assert {"park_hourly", "park_overnight"} <= codes
        new_code = next(t["code"] for t in ov["available_types"])

        created = await client.post("/garage-portal/services", cookies=cookies,
                                    json={"service_type_code": new_code, "note": "Thử"})
        assert created.status_code == 200, created.text
        sid = created.json()["data"]["id"]

        upd = await client.put(f"/garage-portal/services/{sid}", cookies=cookies, json={"note": "Đã sửa"})
        assert upd.status_code == 200
        assert upd.json()["data"]["note"] == "Đã sửa"

        rm = await client.delete(f"/garage-portal/services/{sid}", cookies=cookies)
        assert rm.status_code == 200
        ov2 = (await client.get("/garage-portal/services", cookies=cookies)).json()["data"]
        assert new_code not in {s["service_type_code"] for s in ov2["services"]}

    async def test_customer_cannot_access_portal(self, client: AsyncClient, registered_customer):
        resp = await client.get("/garage-portal/dashboard/overview", cookies=registered_customer["cookies"])
        assert resp.status_code == 403
