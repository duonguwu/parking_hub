# -*- coding: utf-8 -*-
"""
8 scoring functions + context-dependent weights.
Reference: phase2_matching_engine.md §2.5.
"""
from typing import Dict, List, Optional

from app.services.weather.weather_service import WeatherSnapshot


# ── Individual scoring functions (all return [0,1]) ──────────────────

def score_distance(travel_min: float, user_tolerance_min: float = 30.0) -> float:
    """Non-linear: 1.0 within comfort zone, steep decay beyond tolerance."""
    if travel_min <= 0:
        return 1.0
    half = user_tolerance_min * 0.5
    if travel_min <= half:
        return 1.0
    if travel_min <= user_tolerance_min:
        return 1.0 - 0.5 * (travel_min - half) / half
    return max(0.0, 0.5 * (1.0 - (travel_min - user_tolerance_min) / user_tolerance_min))


def score_wait(predicted_wait_min: float, user_tolerance_min: float = 20.0) -> float:
    if predicted_wait_min <= 0:
        return 1.0
    return max(0.0, 1.0 - predicted_wait_min / user_tolerance_min)


def score_quality(tier_score: float, days_since_assess: int = 0) -> float:
    base = max(0.0, min(100.0, tier_score)) / 100.0
    if days_since_assess <= 30:
        confidence = 1.0
    elif days_since_assess >= 120:
        confidence = 0.5
    else:
        confidence = max(0.5, 1.0 - (days_since_assess - 30) / 90.0)
    return base * confidence


def score_fit(vehicle_min_tier: int, garage_tier: int) -> float:
    delta = garage_tier - vehicle_min_tier
    if delta < 0:
        return 0.0    # should be filtered in stage 1
    mapping = {0: 1.00, 1: 0.85, 2: 0.65, 3: 0.45}
    return mapping.get(delta, 0.30)


def score_affinity(user_affinity: List[dict], garage_id: str) -> float:
    for aff in user_affinity or []:
        if str(aff.get("garage_id", "")) == str(garage_id):
            return max(0.0, min(1.0, float(aff.get("affinity", 0.0))))
    return 0.0


def score_price(service_price: int, price_sensitivity: str, area_prices: List[int]) -> float:
    if not area_prices:
        return 0.7  # no context
    if price_sensitivity == "low":
        return 0.8
    # Percentile rank: 0 = cheapest in area, 1 = most expensive
    sorted_prices = sorted(area_prices)
    below = sum(1 for p in sorted_prices if p <= service_price)
    pct = below / len(sorted_prices)
    if price_sensitivity == "high":
        return max(0.0, 1.0 - pct)
    return max(0.0, 1.0 - 0.5 * pct)   # medium


def score_reliability(stats: dict) -> float:
    if not stats:
        return 0.5    # neutral
    on_time = float(stats.get("on_time_rate", 0.5))
    complaint = float(stats.get("complaint_rate", 0.05))
    # completion: fallback if missing → compute from retention_rate
    completion = float(stats.get("completion_rate", 0.9))
    return max(0.0, min(1.0,
        0.5 * on_time + 0.3 * (1.0 - complaint) + 0.2 * completion
    ))


def score_environment(weather: Optional[WeatherSnapshot], amenities: List[str]) -> float:
    """Rain → strongly prefer covered bays."""
    if weather is None:
        return 1.0
    has_cover = "covered_bay" in (amenities or []) or "covered" in (amenities or [])
    if weather.is_raining:
        return 1.0 if has_cover else 0.3
    if weather.is_drizzling:
        return 1.0 if has_cover else 0.7
    return 1.0


# ── Context-dependent weights ────────────────────────────────────────

BASE_WEIGHTS = {
    "distance": 0.22,
    "wait": 0.18,
    "quality": 0.15,
    "fit": 0.12,
    "affinity": 0.10,
    "price": 0.10,
    "reliability": 0.08,
    "environment": 0.05,
}


def compute_context_weights(
    is_raining: bool = False,
    is_peak_hour: bool = False,
    price_sensitivity: str = "medium",
    has_affinity_history: bool = False,
    area_demand: str = "normal",   # low | normal | high | surge
) -> Dict[str, float]:
    w = dict(BASE_WEIGHTS)

    if is_raining:
        w["environment"] += 0.10
        w["distance"] -= 0.05
        w["wait"] -= 0.05

    if is_peak_hour:
        w["wait"] += 0.08
        w["distance"] -= 0.04
        w["quality"] -= 0.04

    if price_sensitivity == "high":
        w["price"] += 0.10
        w["quality"] -= 0.05
        w["reliability"] -= 0.05

    if not has_affinity_history:
        w["affinity"] = 0.0
        w["quality"] += 0.05
        w["reliability"] += 0.05

    if area_demand == "surge":
        w["wait"] += 0.08
        w["affinity"] -= 0.04 if w.get("affinity", 0) > 0.04 else 0
        w["quality"] -= 0.04

    # Clamp negatives to 0, then normalize
    w = {k: max(0.0, v) for k, v in w.items()}
    total = sum(w.values()) or 1.0
    return {k: v / total for k, v in w.items()}


# ── "Why this garage" — explanations ────────────────────────────────

REASON_TEMPLATES = {
    "best_distance": "Chỉ {travel_min} phút — gần nhất trong các lựa chọn phù hợp",
    "low_wait": "Chờ không đáng kể khi đến (~{wait_min} phút)",
    "no_wait": "Hiện trống, không phải chờ",
    "high_quality": "Tier {tier} — chất lượng cao",
    "good_fit": "Phù hợp loại xe của bạn",
    "favorite": "Gara bạn hay quay lại",
    "covered_rain": "Có mái che — phù hợp trời đang mưa",
    "reliable": "Đúng giờ, ít khiếu nại",
    "good_price": "Giá tốt so với khu vực",
}

TRADEOFF_TEMPLATES = {
    "far_distance": "Hơi xa — {travel_min} phút đi",
    "will_wait": "Có thể phải chờ ~{wait_min} phút",
    "overqualified": "Gara cao cấp hơn nhu cầu — giá có thể cao",
    "price_higher": "Giá cao hơn trung bình khu vực",
    "no_cover": "Không có mái che (trời đang mưa)",
    "low_reliability": "Chỉ số đúng giờ chưa cao",
}


def build_reasons_tradeoffs(
    component_scores: Dict[str, float], travel_min: int, wait_min: int,
    tier: int, weather_raining: bool,
) -> dict:
    reasons = []
    tradeoffs = []
    s = component_scores

    # Reasons (high scores)
    if s.get("distance", 0) >= 0.85:
        reasons.append({"type": "best_distance",
                        "text": REASON_TEMPLATES["best_distance"].format(travel_min=travel_min)})
    if s.get("wait", 0) >= 0.95:
        reasons.append({"type": "no_wait", "text": REASON_TEMPLATES["no_wait"]})
    elif s.get("wait", 0) >= 0.75:
        reasons.append({"type": "low_wait",
                        "text": REASON_TEMPLATES["low_wait"].format(wait_min=wait_min)})
    if s.get("quality", 0) >= 0.80:
        reasons.append({"type": "high_quality",
                        "text": REASON_TEMPLATES["high_quality"].format(tier=tier)})
    if s.get("affinity", 0) >= 0.4:
        reasons.append({"type": "favorite", "text": REASON_TEMPLATES["favorite"]})
    if weather_raining and s.get("environment", 0) >= 0.9:
        reasons.append({"type": "covered_rain", "text": REASON_TEMPLATES["covered_rain"]})
    if s.get("reliability", 0) >= 0.85:
        reasons.append({"type": "reliable", "text": REASON_TEMPLATES["reliable"]})
    if s.get("price", 0) >= 0.85:
        reasons.append({"type": "good_price", "text": REASON_TEMPLATES["good_price"]})

    # Trade-offs (low scores)
    if s.get("distance", 1) < 0.4:
        tradeoffs.append({"type": "far_distance",
                          "text": TRADEOFF_TEMPLATES["far_distance"].format(travel_min=travel_min)})
    if s.get("wait", 1) < 0.5:
        tradeoffs.append({"type": "will_wait",
                          "text": TRADEOFF_TEMPLATES["will_wait"].format(wait_min=wait_min)})
    if s.get("fit", 1) < 0.65:
        tradeoffs.append({"type": "overqualified", "text": TRADEOFF_TEMPLATES["overqualified"]})
    if s.get("price", 1) < 0.4:
        tradeoffs.append({"type": "price_higher", "text": TRADEOFF_TEMPLATES["price_higher"]})
    if weather_raining and s.get("environment", 1) < 0.5:
        tradeoffs.append({"type": "no_cover", "text": TRADEOFF_TEMPLATES["no_cover"]})
    if s.get("reliability", 1) < 0.5:
        tradeoffs.append({"type": "low_reliability", "text": TRADEOFF_TEMPLATES["low_reliability"]})

    return {"reasons": reasons[:3], "trade_offs": tradeoffs[:2]}
