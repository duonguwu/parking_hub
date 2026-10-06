# -*- coding: utf-8 -*-
"""Tests cho bảng giá (pricing_utils) và endpoint báo giá."""
from datetime import datetime, timedelta

import pytest
import pytz
from fastapi import HTTPException
from httpx import AsyncClient

from app.api.garage_service.pricing_utils import normalize_pricing, quote_price, display_price

VN = pytz.timezone("Asia/Ho_Chi_Minh")


def vn(y, mo, d, h, mi=0):
    return VN.localize(datetime(y, mo, d, h, mi))


BLOCK = {"mode": "block", "first_block_minutes": 60, "first_block_price": 25000,
         "next_block_minutes": 60, "next_block_price": 15000, "daily_cap": 100000}


class TestQuotePrice:
    def test_first_block_only(self):
        q = quote_price(BLOCK, vn(2026, 10, 7, 9), vn(2026, 10, 7, 9, 40))
        assert q["amount"] == 25000

    def test_partial_block_rounds_up(self):
        # 2h10' = block đầu + 2 block tiếp
        q = quote_price(BLOCK, vn(2026, 10, 7, 9), vn(2026, 10, 7, 11, 10))
        assert q["amount"] == 25000 + 2 * 15000

    def test_daily_cap(self):
        q = quote_price(BLOCK, vn(2026, 10, 7, 8), vn(2026, 10, 7, 20))
        assert q["amount"] == 100000
        assert q["breakdown"][0]["capped"] is True

    def test_multi_day_cap_each_day(self):
        q = quote_price(BLOCK, vn(2026, 10, 7, 8), vn(2026, 10, 9, 8))
        assert q["amount"] == 200000

    def test_peak_multiplier(self):
        p = {**BLOCK, "peak_rules": [{"days": [2], "start": "17:00", "end": "20:00", "multiplier": 1.2}]}
        # 7/10/2026 là thứ 4 (weekday=2)
        q = quote_price(p, vn(2026, 10, 7, 17), vn(2026, 10, 7, 18))
        assert q["amount"] == 30000

    def test_peak_across_midnight(self):
        p = {**BLOCK, "peak_rules": [{"days": list(range(7)), "start": "22:00", "end": "02:00", "multiplier": 2}]}
        q = quote_price(p, vn(2026, 10, 7, 23), vn(2026, 10, 7, 23, 30))
        assert q["amount"] == 50000

    def test_utc_input_converted_to_local(self):
        p = {**BLOCK, "peak_rules": [{"days": [2], "start": "17:00", "end": "20:00", "multiplier": 1.2}]}
        start = datetime(2026, 10, 7, 10, 0, tzinfo=pytz.utc)  # = 17:00 VN
        q = quote_price(p, start, start + timedelta(minutes=30))
        assert q["amount"] == 30000

    def test_flat_once(self):
        q = quote_price({"mode": "flat", "flat_price": 80000}, vn(2026, 10, 7, 18), vn(2026, 10, 8, 7))
        assert q["amount"] == 80000

    def test_flat_per_day(self):
        p = {"mode": "flat", "flat_price": 150000, "flat_unit_minutes": 1440}
        q = quote_price(p, vn(2026, 10, 7, 8), vn(2026, 10, 9, 9))
        assert q["amount"] == 450000

    def test_end_before_start(self):
        with pytest.raises(HTTPException):
            quote_price(BLOCK, vn(2026, 10, 7, 9), vn(2026, 10, 7, 8))


class TestNormalize:
    def test_defaults(self):
        p = normalize_pricing({"mode": "block", "first_block_price": 20000})
        assert p["next_block_price"] == 20000 and p["daily_cap"] is None
        assert display_price(p) == 20000

    def test_invalid_mode(self):
        with pytest.raises(HTTPException):
            normalize_pricing({"mode": "weird"})

    def test_invalid_multiplier(self):
        with pytest.raises(HTTPException):
            normalize_pricing({"peak_rules": [{"start": "17:00", "end": "18:00", "multiplier": 9}]})


@pytest.mark.asyncio
class TestPricingApi:
    async def test_upsert_with_pricing_and_quote(self, client: AsyncClient, configured_garage):
        gid = configured_garage["garage_id"]
        resp = await client.post("/garage-services/upsert", cookies=configured_garage["cookies"], json={
            "garage_id": gid, "service_type_code": "park_hourly",
            "pricing": BLOCK, "note": "Trần 100k/ngày",
        })
        assert resp.status_code == 200
        d = resp.json()["data"]
        assert d["price"] == 25000 and d["pricing"]["daily_cap"] == 100000

        q = await client.get("/garage-services/quote", params={
            "garage_id": gid, "service_type_code": "park_hourly",
            "start_time": "2026-10-07T09:00:00+07:00", "end_time": "2026-10-07T11:30:00+07:00",
        })
        assert q.status_code == 200
        assert q.json()["data"]["amount"] == 25000 + 2 * 15000

    async def test_new_service_uses_default_pricing(self, client: AsyncClient, configured_garage):
        resp = await client.post("/garage-services/upsert", cookies=configured_garage["cookies"], json={
            "garage_id": configured_garage["garage_id"], "service_type_code": "park_daily",
        })
        assert resp.status_code == 200
        d = resp.json()["data"]
        assert d["pricing"]["mode"] == "flat" and d["pricing"]["flat_unit_minutes"] == 1440
