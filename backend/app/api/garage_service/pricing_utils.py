# -*- coding: utf-8 -*-
"""
Bảng giá bãi đỗ — chuẩn hoá và tính giá (dùng chung cho báo giá, đặt chỗ, check-out).

Cấu trúc `pricing` của một garage_service:
{
  "mode": "block" | "flat",
  # block: block đầu + các block tiếp theo, có trần theo ngày (24h)
  "first_block_minutes": 60, "first_block_price": 25000,
  "next_block_minutes": 60,  "next_block_price": 15000,
  "daily_cap": 150000,               # None/0 = không trần
  # flat: giá cố định mỗi đơn vị; flat_unit_minutes None = trọn gói một lần
  "flat_price": 80000, "flat_unit_minutes": None,
  # giờ cao điểm: hệ số áp theo thời điểm bắt đầu block (block) / bắt đầu gửi (flat)
  "peak_rules": [{"days": [0,1,2,3,4], "start": "17:00", "end": "20:00", "multiplier": 1.2}]
}
"""
import math
from datetime import datetime, timedelta
from typing import Optional

import pytz
from fastapi import HTTPException

PRICING_MODES = ("block", "flat")
LOCAL_TZ = pytz.timezone("Asia/Ho_Chi_Minh")


def to_local(ts: datetime) -> datetime:
    """Giờ địa phương (naive coi là UTC, theo quy ước lưu DB)."""
    if ts.tzinfo is None:
        ts = pytz.utc.localize(ts)
    return ts.astimezone(LOCAL_TZ)


def _to_int(v, default: int = 0) -> int:
    try:
        return max(0, int(v))
    except (TypeError, ValueError):
        return default


def _parse_hhmm(s: str) -> int:
    """'17:30' -> 1050 (phút trong ngày)."""
    try:
        h, m = str(s).split(":")
        h, m = int(h), int(m)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=422, detail=f"Giờ không hợp lệ: {s}")
    if not (0 <= h <= 24 and 0 <= m < 60) or h * 60 + m > 1440:
        raise HTTPException(status_code=422, detail=f"Giờ không hợp lệ: {s}")
    return h * 60 + m


def normalize_pricing(pricing: Optional[dict], fallback_price: int = 0) -> dict:
    """Validate + điền mặc định. Raise 422 nếu sai."""
    p = dict(pricing or {})
    mode = p.get("mode") or "block"
    if mode not in PRICING_MODES:
        raise HTTPException(status_code=422, detail="pricing.mode phải là block hoặc flat")

    rules = []
    for r in p.get("peak_rules") or []:
        days = sorted({int(d) for d in (r.get("days") or []) if 0 <= int(d) <= 6})
        start, end = r.get("start", "00:00"), r.get("end", "00:00")
        s, e = _parse_hhmm(start), _parse_hhmm(end)
        if s == e:
            raise HTTPException(status_code=422, detail="Khung cao điểm phải có giờ bắt đầu khác giờ kết thúc")
        mult = float(r.get("multiplier") or 1.0)
        if not (0.5 <= mult <= 3.0):
            raise HTTPException(status_code=422, detail="Hệ số cao điểm phải trong khoảng 0.5–3.0")
        rules.append({"days": days or list(range(7)), "start": start, "end": end, "multiplier": round(mult, 2)})

    out = {"mode": mode, "peak_rules": rules}
    if mode == "block":
        out["first_block_minutes"] = _to_int(p.get("first_block_minutes"), 60) or 60
        out["first_block_price"] = _to_int(p.get("first_block_price"), fallback_price)
        out["next_block_minutes"] = _to_int(p.get("next_block_minutes"), 60) or 60
        out["next_block_price"] = _to_int(p.get("next_block_price"), out["first_block_price"])
        out["daily_cap"] = _to_int(p.get("daily_cap"), 0) or None
    else:
        out["flat_price"] = _to_int(p.get("flat_price"), fallback_price)
        unit = _to_int(p.get("flat_unit_minutes"), 0)
        out["flat_unit_minutes"] = unit or None
    return out


def display_price(pricing: dict) -> int:
    """Giá hiển thị ngắn gọn (giá block đầu hoặc giá trọn gói)."""
    if (pricing or {}).get("mode") == "flat":
        return int(pricing.get("flat_price") or 0)
    return int((pricing or {}).get("first_block_price") or 0)


def _multiplier_at(rules: list, ts: datetime) -> float:
    ts = to_local(ts)
    minute = ts.hour * 60 + ts.minute
    best = 1.0
    for r in rules or []:
        if ts.weekday() not in (r.get("days") or range(7)):
            continue
        s, e = _parse_hhmm(r["start"]), _parse_hhmm(r["end"])
        inside = s <= minute < e if s < e else (minute >= s or minute < e)  # khung qua nửa đêm
        if inside:
            best = max(best, float(r.get("multiplier") or 1.0))
    return best


def quote_price(pricing: dict, start: datetime, end: datetime) -> dict:
    """
    Tính giá cho khoảng [start, end). Trả về {amount, minutes, breakdown[]}.
    """
    if end <= start:
        raise HTTPException(status_code=422, detail="Giờ kết thúc phải sau giờ bắt đầu")
    start, end = to_local(start), to_local(end)
    p = normalize_pricing(pricing)
    minutes = math.ceil((end - start).total_seconds() / 60)
    rules = p.get("peak_rules") or []

    if p["mode"] == "flat":
        units = math.ceil(minutes / p["flat_unit_minutes"]) if p.get("flat_unit_minutes") else 1
        mult = _multiplier_at(rules, start)
        amount = int(round(p["flat_price"] * units * mult, -2))
        return {
            "amount": amount, "minutes": minutes,
            "breakdown": [{"label": f"{units} × trọn gói", "units": units,
                           "unit_price": p["flat_price"], "multiplier": mult, "amount": amount}],
        }

    # block mode — chia theo từng chu kỳ 24h để áp trần ngày
    breakdown = []
    total = 0
    day_start = start
    day_index = 0
    while day_start < end:
        day_end = min(day_start + timedelta(days=1), end)
        cursor = day_start
        day_amount = 0.0
        first = day_index == 0
        while cursor < day_end:
            blk = p["first_block_minutes"] if first else p["next_block_minutes"]
            price = p["first_block_price"] if first else p["next_block_price"]
            day_amount += price * _multiplier_at(rules, cursor)
            cursor += timedelta(minutes=blk)
            first = False
        cap = p.get("daily_cap")
        capped = bool(cap and day_amount > cap)
        day_amount = int(round(min(day_amount, cap) if capped else day_amount, -2))
        breakdown.append({"label": f"Ngày {day_index + 1}", "amount": day_amount, "capped": capped})
        total += day_amount
        day_start = day_end
        day_index += 1

    return {"amount": int(total), "minutes": minutes, "breakdown": breakdown}
