# -*- coding: utf-8 -*-
"""
Tests for booking state machine (giữ chỗ theo khoảng thời gian):
  pending (cấp 2) / reserved (cấp 3–4) → checked_in → checked_out + feedback.
Also tests cancellation, invalid transitions and double-booking prevention.
Bãi test được admin duyệt ở cấp 3 (xem conftest) nên lượt đặt tự xác nhận.
"""
from datetime import datetime, timedelta, timezone
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


def _future_time(minutes_from_now: int = 30) -> str:
    return (datetime.now(timezone.utc) + timedelta(minutes=minutes_from_now)).isoformat()


async def _create(client, cookies, garage_id, code="park_hourly", start_in=30, hours=2, plate="51A-12345"):
    start = datetime.now(timezone.utc) + timedelta(minutes=start_in)
    return await client.post("/bookings/create", cookies=cookies, json={
        "garage_id": garage_id,
        "service_type_code": code,
        "start_time": start.isoformat(),
        "end_time": (start + timedelta(hours=hours)).isoformat(),
        "license_plate": plate,
    })


class TestBookingCreate:
    async def test_customer_creates_booking(
        self, client: AsyncClient, configured_garage, registered_customer,
    ):
        resp = await _create(client, registered_customer["cookies"], configured_garage["garage_id"],
                             code="park_overnight", start_in=60 * 24 * 3, hours=10)
        assert resp.status_code == 200, resp.text
        b = resp.json()["data"]
        assert b["status"] == "reserved"          # cấp 3 → tự xác nhận
        assert b["quoted_price"] > 0
        assert b["booking_code"].startswith("PH-")
        assert b["license_plate"] == "51A-12345"
        assert b["grace_until"] is not None

    async def test_create_unavailable_service(
        self, client: AsyncClient, configured_garage, registered_customer,
    ):
        resp = await _create(client, registered_customer["cookies"], configured_garage["garage_id"],
                             code="park_monthly", start_in=60)
        assert resp.status_code == 409

    async def test_end_before_start_rejected(
        self, client: AsyncClient, configured_garage, registered_customer,
    ):
        resp = await client.post("/bookings/create", cookies=registered_customer["cookies"], json={
            "garage_id": configured_garage["garage_id"],
            "service_type_code": "park_hourly",
            "start_time": _future_time(120),
            "end_time": _future_time(60),
        })
        assert resp.status_code == 422

    async def test_overlapping_booking_rejected(
        self, client: AsyncClient, configured_garage, registered_customer,
    ):
        cookies = registered_customer["cookies"]
        first = await _create(client, cookies, configured_garage["garage_id"], start_in=60 * 24 * 5)
        assert first.status_code == 200, first.text
        dup = await _create(client, cookies, configured_garage["garage_id"], start_in=60 * 24 * 5 + 30)
        assert dup.status_code == 409

    async def test_unauthenticated_cannot_create(
        self, client: AsyncClient, configured_garage,
    ):
        async with AsyncClient(
            transport=client._transport, base_url=client.base_url,
        ) as fresh:
            resp = await fresh.post("/bookings/create", json={
                "garage_id": configured_garage["garage_id"],
                "service_type_code": "park_hourly",
                "start_time": _future_time(30),
            })
            assert resp.status_code == 401


class TestBookingStateMachine:
    """Full lifecycle: reserved → checked_in → checked_out → feedback."""

    async def test_full_happy_path(
        self, client: AsyncClient, configured_garage, registered_customer,
    ):
        customer_cookies = registered_customer["cookies"]
        owner_cookies = configured_garage["cookies"]

        create_resp = await _create(client, customer_cookies, configured_garage["garage_id"],
                                    start_in=15, plate="51B-99999")
        assert create_resp.status_code == 200, create_resp.text
        booking_id = create_resp.json()["data"]["id"]

        # Check-in bởi nhân viên, sai biển số bị từ chối
        bad = await client.post("/bookings/checkin", cookies=owner_cookies,
                                json={"id": booking_id, "license_plate": "30A-00000"})
        assert bad.status_code == 409

        r1 = await client.post("/bookings/checkin", cookies=owner_cookies,
                               json={"id": booking_id, "license_plate": "51b-99999"})
        assert r1.status_code == 200, r1.text
        assert r1.json()["data"]["status"] == "checked_in"

        # Check-out kèm thanh toán tiền mặt
        r2 = await client.post("/bookings/checkout", cookies=owner_cookies,
                               json={"id": booking_id, "payment_method": "cash"})
        assert r2.status_code == 200, r2.text
        out = r2.json()["data"]
        assert out["status"] == "checked_out"
        assert out["final_price"] is not None
        assert out["payment_status"] == "paid"

        # Feedback (customer)
        r3 = await client.post("/bookings/feedback", cookies=customer_cookies, json={
            "id": booking_id, "rating": 5, "quick_feedback": "thumbs_up", "comment": "Bãi rộng, dễ vào",
        })
        assert r3.status_code == 200, r3.text
        fb = r3.json()["data"]["feedback"]
        assert fb["rating"] == 5
        assert fb["quick_feedback"] == "thumbs_up"

    async def test_customer_cannot_checkin(
        self, client: AsyncClient, configured_garage, registered_customer,
    ):
        create = await _create(client, registered_customer["cookies"], configured_garage["garage_id"],
                               start_in=60 * 24 * 7)
        bid = create.json()["data"]["id"]
        resp = await client.post("/bookings/checkin", cookies=registered_customer["cookies"], json={"id": bid})
        assert resp.status_code == 403

    async def test_invalid_transition_rejected(
        self, client: AsyncClient, configured_garage, registered_customer,
    ):
        create = await _create(client, registered_customer["cookies"], configured_garage["garage_id"],
                               start_in=60 * 24 * 9)
        bid = create.json()["data"]["id"]
        # reserved → checked_out không hợp lệ
        resp = await client.post("/bookings/checkout", cookies=configured_garage["cookies"], json={"id": bid})
        assert resp.status_code == 409

    async def test_checkin_too_early_rejected(
        self, client: AsyncClient, configured_garage, registered_customer,
    ):
        create = await _create(client, registered_customer["cookies"], configured_garage["garage_id"],
                               start_in=60 * 24 * 11)
        bid = create.json()["data"]["id"]
        resp = await client.post("/bookings/checkin", cookies=configured_garage["cookies"], json={"id": bid})
        assert resp.status_code == 409

    async def test_no_show_before_grace_rejected(
        self, client: AsyncClient, configured_garage, registered_customer,
    ):
        create = await _create(client, registered_customer["cookies"], configured_garage["garage_id"],
                               start_in=60 * 24 * 13)
        bid = create.json()["data"]["id"]
        resp = await client.post("/bookings/no_show", cookies=configured_garage["cookies"], json={"id": bid})
        assert resp.status_code == 409


class TestBookingCancellation:
    async def test_customer_cancels_reserved(
        self, client: AsyncClient, configured_garage, registered_customer,
    ):
        create = await _create(client, registered_customer["cookies"], configured_garage["garage_id"],
                               start_in=60 * 24 * 15)
        bid = create.json()["data"]["id"]
        resp = await client.post("/bookings/cancel", cookies=registered_customer["cookies"],
                                 json={"id": bid, "reason": "Đổi kế hoạch"})
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["status"] == "cancelled"
        assert data["cancelled_by"] == "customer"

        again = await client.post("/bookings/cancel", cookies=registered_customer["cookies"], json={"id": bid})
        assert again.status_code == 409


class TestBookingQueries:
    async def test_customer_sees_own_bookings(
        self, client: AsyncClient, configured_garage, registered_customer,
    ):
        resp = await client.post("/bookings/get_all", cookies=registered_customer["cookies"], json={})
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)
        assert len(data) >= 1   # prior tests created bookings

    async def test_garage_sees_own_tenant_bookings(
        self, client: AsyncClient, configured_garage,
    ):
        resp = await client.post("/bookings/get_all", cookies=configured_garage["cookies"], json={})
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)
        assert len(data) >= 1
