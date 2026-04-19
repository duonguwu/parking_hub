# -*- coding: utf-8 -*-
"""Unit tests for the 8 scoring functions + context weights (no DB needed)."""
import pytest

from app.api.matching.scoring import (
    score_distance, score_wait, score_quality, score_fit,
    score_affinity, score_price, score_reliability, score_environment,
    compute_context_weights, build_reasons_tradeoffs,
)
from app.services.weather.weather_service import WeatherSnapshot


class TestDistanceScore:
    def test_very_close_is_perfect(self):
        assert score_distance(5, 30) == 1.0

    def test_at_half_tolerance_is_perfect(self):
        assert score_distance(15, 30) == 1.0

    def test_at_full_tolerance_is_mid(self):
        assert score_distance(30, 30) == pytest.approx(0.5, abs=0.01)

    def test_beyond_tolerance_steep_decay(self):
        assert score_distance(45, 30) < 0.3

    def test_very_far_is_zero(self):
        assert score_distance(100, 30) == 0.0


class TestWaitScore:
    def test_zero_wait_is_perfect(self):
        assert score_wait(0, 20) == 1.0

    def test_full_tolerance_is_zero(self):
        assert score_wait(20, 20) == 0.0

    def test_half_tolerance(self):
        assert score_wait(10, 20) == pytest.approx(0.5, abs=0.01)


class TestQualityScore:
    def test_perfect_fresh(self):
        assert score_quality(100, 0) == 1.0

    def test_old_assessment_penalty(self):
        recent = score_quality(80, 10)
        old = score_quality(80, 120)
        assert old < recent
        assert old >= 0.5 * 0.8   # confidence floor

    def test_clamps(self):
        assert 0 <= score_quality(120, 0) <= 1.0
        assert score_quality(-10, 0) == 0


class TestFitScore:
    def test_exact_match_best(self):
        assert score_fit(3, 3) == 1.0

    def test_overqualified_decay(self):
        assert score_fit(1, 2) == 0.85
        assert score_fit(1, 3) == 0.65
        assert score_fit(1, 4) == 0.45

    def test_mismatch_returns_zero(self):
        assert score_fit(3, 2) == 0.0   # vehicle needs tier 3, garage only tier 2


class TestAffinityScore:
    def test_empty_profile(self):
        assert score_affinity([], "gid") == 0.0
        assert score_affinity(None, "gid") == 0.0

    def test_known_garage(self):
        aff = [{"garage_id": "gid1", "affinity": 0.6}]
        assert score_affinity(aff, "gid1") == 0.6

    def test_unknown_garage(self):
        aff = [{"garage_id": "gid1", "affinity": 0.6}]
        assert score_affinity(aff, "gid2") == 0.0


class TestPriceScore:
    def test_empty_area(self):
        assert score_price(100, "medium", []) == 0.7   # neutral

    def test_low_sensitivity_constant(self):
        assert score_price(50, "low", [10, 20, 30, 40, 50]) == 0.8
        assert score_price(999, "low", [10, 20, 30, 40, 50]) == 0.8

    def test_high_sensitivity_cheap_wins(self):
        # cheapest in area
        assert score_price(10, "high", [10, 50, 100]) > score_price(100, "high", [10, 50, 100])

    def test_medium_sensitivity_gentler(self):
        # "More sensitive" means bigger penalty for expensive items,
        # not that cheap items score differently.
        prices = [10, 50, 100]
        m_exp = score_price(100, "medium", prices)
        h_exp = score_price(100, "high", prices)
        assert h_exp < m_exp   # high penalizes expensive more
        # Both favor cheap vs expensive
        m_cheap = score_price(10, "medium", prices)
        h_cheap = score_price(10, "high", prices)
        assert m_cheap > m_exp   # medium: cheap > expensive
        assert h_cheap > h_exp   # high: cheap > expensive


class TestReliabilityScore:
    def test_no_stats_neutral(self):
        assert score_reliability({}) == 0.5

    def test_perfect_stats(self):
        s = {"on_time_rate": 1.0, "complaint_rate": 0.0, "completion_rate": 1.0}
        assert score_reliability(s) == pytest.approx(1.0, abs=0.01)

    def test_bad_stats(self):
        s = {"on_time_rate": 0.2, "complaint_rate": 0.5, "completion_rate": 0.3}
        result = score_reliability(s)
        assert result < 0.5


class TestEnvironmentScore:
    def test_no_weather_neutral(self):
        assert score_environment(None, []) == 1.0

    def test_raining_covered(self):
        w = WeatherSnapshot(precipitation_mm=2.0)
        assert score_environment(w, ["covered_bay"]) == 1.0

    def test_raining_no_cover(self):
        w = WeatherSnapshot(precipitation_mm=2.0)
        assert score_environment(w, ["wifi"]) == 0.3

    def test_drizzle_no_cover(self):
        w = WeatherSnapshot(precipitation_mm=0.2)
        assert score_environment(w, []) == 0.7

    def test_clear_weather(self):
        w = WeatherSnapshot(precipitation_mm=0)
        assert score_environment(w, []) == 1.0


class TestContextWeights:
    def test_baseline_sums_to_one(self):
        w = compute_context_weights()
        assert sum(w.values()) == pytest.approx(1.0, abs=0.001)

    def test_rain_bumps_environment(self):
        baseline = compute_context_weights()
        rainy = compute_context_weights(is_raining=True)
        assert rainy["environment"] > baseline["environment"]

    def test_peak_hour_bumps_wait(self):
        baseline = compute_context_weights()
        peak = compute_context_weights(is_peak_hour=True)
        assert peak["wait"] > baseline["wait"]

    def test_high_price_sensitivity_bumps_price(self):
        baseline = compute_context_weights()
        frugal = compute_context_weights(price_sensitivity="high")
        assert frugal["price"] > baseline["price"]

    def test_new_user_zeros_affinity(self):
        w = compute_context_weights(has_affinity_history=False)
        assert w["affinity"] == 0.0
        assert sum(w.values()) == pytest.approx(1.0, abs=0.001)


class TestReasonsTradeoffs:
    def test_best_distance_flagged(self):
        scores = {"distance": 0.9, "wait": 0.5, "quality": 0.5, "fit": 0.7,
                  "affinity": 0.0, "price": 0.5, "reliability": 0.5, "environment": 1.0}
        out = build_reasons_tradeoffs(scores, 12, 5, 3, False)
        assert any(r["type"] == "best_distance" for r in out["reasons"])

    def test_price_tradeoff(self):
        scores = {"distance": 0.9, "wait": 0.9, "quality": 0.9, "fit": 0.9,
                  "affinity": 0.5, "price": 0.2, "reliability": 0.8, "environment": 1.0}
        out = build_reasons_tradeoffs(scores, 10, 0, 3, False)
        assert any(t["type"] == "price_higher" for t in out["trade_offs"])

    def test_rain_covered_reason(self):
        scores = {"distance": 0.7, "wait": 0.6, "quality": 0.7, "fit": 0.9,
                  "affinity": 0.0, "price": 0.5, "reliability": 0.7, "environment": 1.0}
        out = build_reasons_tradeoffs(scores, 15, 8, 3, True)
        assert any(r["type"] == "covered_rain" for r in out["reasons"])
