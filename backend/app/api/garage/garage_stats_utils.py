# -*- coding: utf-8 -*-
"""
Chỉ số vận hành của bãi và điểm chất lượng (quality_score 0–100).

  fulfillment_rate  lượt đã giữ được khách vào bãi / (đã vào + bãi huỷ sau khi giữ)
  no_show_rate      khách không đến / (đã vào + không đến)        — lỗi phía khách, không trừ điểm bãi
  complaint_count   lượt có khiếu nại hoặc đánh giá ≤ 2 sao
  return_rate       khách gửi ≥ 2 lần / khách đã gửi
  avg_rating        điểm đánh giá trung bình

quality_score = 45% giữ đúng chỗ + 20% (1 − tỉ lệ khiếu nại) + 15% quay lại + 20% đánh giá
"""
from collections import Counter
from datetime import timedelta
from typing import Optional

from bson import ObjectId

from app.api.booking.booking_models import BookingModel
from app.api.garage.garage_models import GarageModel
from app.api.shared.tool.datetime_convert import get_current_time

STATS_WINDOW_DAYS = 90
MIN_SESSIONS_FOR_SCORE = 5


def compute_stats(bookings: list) -> dict:
    honored = [b for b in bookings if b.get("status") in ("checked_in", "checked_out") and b.get("source") != "walk_in"]
    garage_failed = [b for b in bookings if b.get("status") == "cancelled" and b.get("cancelled_by") == "garage"]
    no_show = [b for b in bookings if b.get("status") == "no_show"]
    sessions = [b for b in bookings if b.get("status") == "checked_out"]

    n_honored = len(honored)
    fulfillment = n_honored / max(n_honored + len(garage_failed), 1) if (n_honored or garage_failed) else 0.0
    no_show_rate = len(no_show) / max(n_honored + len(no_show), 1) if (n_honored or no_show) else 0.0

    ratings = [int(b["feedback"]["rating"]) for b in sessions if (b.get("feedback") or {}).get("rating")]
    complaints = [b for b in sessions if (b.get("feedback") or {}).get("complaint")
                  or ((b.get("feedback") or {}).get("rating") or 5) <= 2]

    per_customer = Counter(str(b["customer_id"]) for b in sessions if b.get("customer_id"))
    returning = sum(1 for n in per_customer.values() if n >= 2)
    return_rate = returning / len(per_customer) if per_customer else 0.0

    avg_rating = sum(ratings) / len(ratings) if ratings else 0.0
    complaint_rate = len(complaints) / max(len(sessions), 1)

    if len(sessions) >= MIN_SESSIONS_FOR_SCORE:
        rating_part = (avg_rating / 5.0) if ratings else 0.8
        quality = 100 * (0.45 * fulfillment + 0.20 * (1 - complaint_rate) + 0.15 * return_rate + 0.20 * rating_part)
    else:
        quality = 0.0

    return {
        "stats": {
            "fulfillment_rate": round(fulfillment, 4),
            "no_show_rate": round(no_show_rate, 4),
            "complaint_count": len(complaints),
            "return_rate": round(return_rate, 4),
            "avg_rating": round(avg_rating, 2),
            "rating_count": len(ratings),
            "total_sessions": len(sessions),
        },
        "quality_score": round(quality, 1),
    }


async def recompute_garage_stats(garage_oid: ObjectId, now=None) -> Optional[dict]:
    now = now or get_current_time()
    bookings = await BookingModel.collection.find(
        {"garage_id": garage_oid, "start_time": {"$gte": now - timedelta(days=STATS_WINDOW_DAYS)}},
        {"status": 1, "source": 1, "cancelled_by": 1, "feedback": 1, "customer_id": 1},
    ).to_list(length=50000)
    result = compute_stats(bookings)
    await GarageModel.collection.update_one(
        {"_id": garage_oid},
        {"$set": {"stats": result["stats"], "quality_score": result["quality_score"]}},
    )
    return result
