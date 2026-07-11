"""Signal score formula — bounds, weights, and each component."""
import pytest

from app.services.scoring import (
    market_depth_norm,
    recency_bonus,
    signal_score,
    skill_breadth,
)


class TestMarketDepthNorm:
    def test_zero_roles_is_zero(self):
        assert market_depth_norm(0) == 0.0

    def test_negative_roles_is_zero(self):
        assert market_depth_norm(-5) == 0.0

    def test_saturates_at_one(self):
        assert market_depth_norm(10_000) == 1.0

    def test_monotonic(self):
        assert market_depth_norm(5) < market_depth_norm(50) < market_depth_norm(500)


class TestRecencyBonus:
    def test_fresh_role_full_bonus(self):
        assert recency_bonus(0) == 1.0
        assert recency_bonus(3) == 1.0

    def test_stale_role_no_bonus(self):
        assert recency_bonus(36) == 0.0
        assert recency_bonus(120) == 0.0

    def test_decays_between(self):
        assert 0.0 < recency_bonus(18) < 1.0
        assert recency_bonus(6) > recency_bonus(24)


class TestSkillBreadth:
    def test_empty_is_zero(self):
        assert skill_breadth([]) == 0.0

    def test_single_domain_is_zero(self):
        assert skill_breadth([1.0]) == 0.0

    def test_uniform_is_max(self):
        assert skill_breadth([0.25, 0.25, 0.25, 0.25]) == pytest.approx(1.0)

    def test_skewed_below_uniform(self):
        assert skill_breadth([0.9, 0.05, 0.05]) < skill_breadth([1 / 3, 1 / 3, 1 / 3])

    def test_ignores_zero_weights(self):
        assert skill_breadth([0.5, 0.5, 0.0]) == pytest.approx(1.0)


class TestSignalScore:
    def test_bounded_0_100(self):
        assert signal_score(0.0, 0, 120, []) == 0
        assert signal_score(1.0, 10_000, 0, [0.25] * 4) == 100

    def test_out_of_range_match_score_clamped(self):
        assert signal_score(5.0, 0, 120, []) <= 100
        assert signal_score(-1.0, 0, 120, []) == 0

    def test_monotonic_in_match_score(self):
        low = signal_score(0.2, 10, 0, [0.5, 0.5])
        high = signal_score(0.9, 10, 0, [0.5, 0.5])
        assert high > low

    def test_top_match_dominates(self):
        # 0.55 weight on top match: perfect match alone beats everything else combined
        match_only = signal_score(1.0, 0, 120, [])
        rest_only = signal_score(0.0, 10_000, 0, [0.25] * 4)
        assert match_only > rest_only

    def test_returns_int(self):
        assert isinstance(signal_score(0.5, 5, 6, [0.6, 0.4]), int)
