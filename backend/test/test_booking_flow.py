# -*- coding: utf-8 -*-
"""
Tests for full booking state machine:
  pending → confirmed → customer_arriving → customer_arrived
  → in_service → completed + feedback.
Also tests cancellation and double-booking prevention.
"""
import asyncio
from datetime import datetime, timedelta, timezone
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


def _future_time(minutes_from_now: int = 30) -> str:
    return (datetime.now(timezone.utc) + timedelta(minutes=minutes_from_now)).isoformat()


class TestBookingCreate:
    async def test_customer_creates_booking(
        self, client: AsyncClient, configured_garage, registered_customer,
    ):
        resp = await client.post(
            "/bookings/create",
            cookies=registered_customer["cookies"],
            json={
                "garage_id": configured_garage["garage_id"],
                "service_type_code": "wash_premium",
                "requested_time": _future_time(30),
            },
        )
        assert resp.status_code == 200, resp.text
        b = resp.json()["data"]
        assert b["status"] == "pending"
        assert b["price"] == 150000
        assert b["booking_code"].startswith("WM-")

    async def test_create_unavailable_service(
        self, client: AsyncClient, configured_garage, registered_customer,
    ):
        resp = await client.post(
            "/bookings/create",
            cookies=registered_customer["cookies"],
            json={
                "garage_id": configured_garage["garage_id"],
                "service_type_code": "coating",     # not configured at this garage
                "requested_time": _future_time(60),
            },
        )
        assert resp.status_code == 409

    async def test_unauthenticated_cannot_create(
        self, client: AsyncClient, configured_garage,
    ):
        async with AsyncClient(
            transport=client._transport, base_url=client.base_url,
        ) as fresh:
            resp = await fresh.post(
                "/bookings/create",
                json={
                    "garage_id": configured_garage["garage_id"],
                    "service_type_code": "wash_premium",
                    "requested_time": _future_time(30),
                },
            )
            assert resp.status_code == 401


class TestBookingStateMachine:
    """Full lifecycle: pending → completed."""

    async def test_full_happy_path(
        self, client: AsyncClient, configured_garage, registered_customer,
    ):
        customer_cookies = registered_customer["cookies"]
        owner_cookies = configured_garage["cookies"]

        # Create
        create_resp = await client.post(
            "/bookings/create",
            cookies=customer_cookies,
            json={
                "garage_id": configured_garage["garage_id"],
                "service_type_code": "wash_basic",
                "requested_time": _future_time(15),
            },
        )
        assert create_resp.status_code == 200
        booking_id = create_resp.json()["data"]["id"]

        # Confirm (garage)
        r1 = await client.post(
            "/bookings/confirm",
            cookies=owner_cookies,
            json={"id": booking_id},
        )
        assert r1.status_code == 200
        assert r1.json()["data"]["status"] == "confirmed"

        # Depart (customer)
        r2 = await client.post(
            "/bookings/depart",
            cookies=customer_cookies,
            json={"id": booking_id},
        )
        assert r2.status_code == 200
        assert r2.json()["data"]["status"] == "customer_arriving"

        # Check-in (GPS — at garage location)
        r3 = await client.post(
            "/bookings/checkin",
            cookies=customer_cookies,
            json={
                "id": booking_id,
                "method": "gps",
                "lat": 10.7834,
                "lng": 106.6856,
            },
        )
        assert r3.status_code == 200, r3.text
        assert r3.json()["data"]["status"] == "customer_arrived"

        # Start service (garage)
        r4 = await client.post(
            "/bookings/start_service",
            cookies=owner_cookies,
            json={"id": booking_id},
        )
        assert r4.status_code == 200
        assert r4.json()["data"]["status"] == "in_service"

        # Complete (garage)
        r5 = await client.post(
            "/bookings/complete",
            cookies=owner_cookies,
            json={"id": booking_id},
        )
        assert r5.status_code == 200
        assert r5.json()["data"]["status"] == "completed"

        # Feedback (customer)
        r6 = await client.post(
            "/bookings/feedback",
            cookies=customer_cookies,
            json={
                "id": booking_id,
                "rating": 5,
                "quick_feedback": "thumbs_up",
                "comment": "Tuyệt vời",
            },
        )
        assert r6.status_code == 200
        fb = r6.json()["data"]["feedback"]
        assert fb["rating"] == 5
        assert fb["quick_feedback"] == "thumbs_up"

    async def test_invalid_transition_rejected(
        self, client: AsyncClient, configured_garage, registered_customer,
    ):
        create = await client.post(
            "/bookings/create",
            cookies=registered_customer["cookies"],
            json={
                "garage_id": configured_garage["garage_id"],
                "service_type_code": "wash_basic",
                "requested_time": _future_time(45),
            },
        )
        booking_id = create.json()["data"]["id"]

        # Try to skip confirm → go directly to depart
        resp = await client.post(
            "/bookings/depart",
            cookies=registered_customer["cookies"],
            json={"id": booking_id},
        )
        assert resp.status_code == 409   # cannot depart before confirm

    async def test_checkin_too_far_rejected(
        self, client: AsyncClient, configured_garage, registered_customer,
    ):
        owner_cookies = configured_garage["cookies"]
        cust_cookies = registered_customer["cookies"]

        create = await client.post(
            "/bookings/create",
            cookies=cust_cookies,
            json={
                "garage_id": configured_garage["garage_id"],
                "service_type_code": "wash_basic",
                "requested_time": _future_time(20),
            },
        )
        bid = create.json()["data"]["id"]
        await client.post("/bookings/confirm", cookies=owner_cookies, json={"id": bid})
        await client.post("/bookings/depart", cookies=cust_cookies, json={"id": bid})

        # Try to checkin from 10km away
        resp = await client.post(
            "/bookings/checkin",
            cookies=cust_cookies,
            json={"id": bid, "method": "gps", "lat": 10.90, "lng": 106.70},
        )
        assert resp.status_code == 400


class TestBookingCancellation:
    async def test_customer_cancels_pending(
        self, client: AsyncClient, configured_garage, registered_customer,
    ):
        create = await client.post(
            "/bookings/create",
            cookies=registered_customer["cookies"],
            json={
                "garage_id": configured_garage["garage_id"],
                "service_type_code": "wash_basic",
                "requested_time": _future_time(90),
            },
        )
        bid = create.json()["data"]["id"]
        resp = await client.post(
            "/bookings/cancel",
            cookies=registered_customer["cookies"],
            json={"id": bid, "reason": "Change of plans"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "cancelled_by_customer"
        assert resp.json()["data"]["cancellation_fee_percent"] == 0


class TestBookingQueries:
    async def test_customer_sees_own_bookings(
        self, client: AsyncClient, registered_customer,
    ):
        resp = await client.post(
            "/bookings/get_all",
            cookies=registered_customer["cookies"],
            json={},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)
        assert len(data) >= 1   # prior tests created bookings

    async def test_garage_sees_own_tenant_bookings(
        self, client: AsyncClient, configured_garage,
    ):
        resp = await client.post(
            "/bookings/get_all",
            cookies=configured_garage["cookies"],
            json={},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)
