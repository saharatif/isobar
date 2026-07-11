"""Signal score — the transparent formula from ARCHITECTURE-BACKEND.md §5.

signal_score = round((0.55 * top_match_score
                    + 0.25 * market_depth_norm
                    + 0.10 * recency_bonus
                    + 0.10 * skill_breadth) * 100)

Every input is a 0..1 float so the result is bounded 0..100.
"""
import math
from typing import Sequence

MARKET_DEPTH_CEILING = 1000  # open roles at which market depth saturates
RECENCY_FULL_MONTHS = 3  # résumé this fresh gets the full bonus
RECENCY_ZERO_MONTHS = 36  # bonus decays to zero by here


def market_depth_norm(open_roles: int) -> float:
    if open_roles <= 0:
        return 0.0
    return min(1.0, math.log(open_roles + 1) / math.log(MARKET_DEPTH_CEILING))


def recency_bonus(months_since_last_role: int) -> float:
    if months_since_last_role <= RECENCY_FULL_MONTHS:
        return 1.0
    if months_since_last_role >= RECENCY_ZERO_MONTHS:
        return 0.0
    span = RECENCY_ZERO_MONTHS - RECENCY_FULL_MONTHS
    return 1.0 - (months_since_last_role - RECENCY_FULL_MONTHS) / span


def skill_breadth(domain_weights: Sequence[float]) -> float:
    """Normalized Shannon entropy over domain weights (0..1)."""
    weights = [w for w in domain_weights if w > 0]
    if len(weights) <= 1:
        return 0.0
    total = sum(weights)
    probs = [w / total for w in weights]
    entropy = -sum(p * math.log(p) for p in probs)
    return entropy / math.log(len(probs))


def signal_score(
    top_match_score: float,
    open_roles: int,
    months_since_last_role: int,
    domain_weights: Sequence[float],
) -> int:
    top = max(0.0, min(1.0, top_match_score))
    raw = (
        0.55 * top
        + 0.25 * market_depth_norm(open_roles)
        + 0.10 * recency_bonus(months_since_last_role)
        + 0.10 * skill_breadth(domain_weights)
    )
    return max(0, min(100, round(raw * 100)))
