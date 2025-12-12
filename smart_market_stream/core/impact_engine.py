"""
Price Impact Weighting Engine

Provides functions to compute price change, per-factor weights, an overall impact score,
and the dominant factor given a previous and current price.

The algorithm is heuristic-based and intended as a configurable starting point for
Project Pasar Rakyat. For production use, tune the factor table and mapping logic
or replace with a ML model / rules engine fed with external signals (weather, pests, logistics).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Tuple
import math


@dataclass
class ImpactResult:
    price_change: float  # relative change (new - prev) / prev
    impact_score: float  # 0-100
    dominant_factor: str
    factors_with_weights: Dict[str, float]  # percentages summing to ~100


# Predefined factor base multipliers.
# Positive multiplier suggests factor tends to increase price when active,
# negative multiplier suggests factor tends to decrease price when active.
# Values are heuristics and can be tuned or loaded from configuration.
DEFAULT_FACTOR_TABLE: Dict[str, float] = {
    "weather": 0.9,             # rain/drought causing shortages -> price up
    "pests": 0.8,               # pests reduce supply -> price up
    "distribution": 0.6,        # distribution issues -> price up
    "logistics": 0.6,           # logistic disruptions -> price up
    "oversupply": -0.9,         # oversupply pushes price down
    "seasonal_harvest": -0.7,   # harvest increases supply -> price down
    "national_demand": 0.7,     # increased national demand -> price up
}


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def compute_impact(
    prev_price: float | None,
    new_price: float,
    commodity: str | None = None,
    market_id: str | None = None,
    region: str | None = None,
    factor_table: Dict[str, float] = None,
    timestamp: datetime | None = None,
) -> ImpactResult:
    """
    Compute the impact result for a price change.

    Args:
        prev_price: previous price value or None if not available.
        new_price: current price.
        commodity, market_id, region: optional context (not used in this heuristic but provided for extensibility).
        factor_table: optional override of DEFAULT_FACTOR_TABLE.

    Returns:
        ImpactResult with price_change (relative), impact_score (0-100), dominant_factor and factors_with_weights.
    """
    if factor_table is None:
        factor_table = DEFAULT_FACTOR_TABLE

    # Compute relative price change
    if prev_price is None or prev_price <= 0:
        price_change = 0.0
    else:
        price_change = (new_price - prev_price) / prev_price

    magnitude = abs(price_change)  # 0.0 .. inf

    # If no meaningful change, return neutral impact
    if math.isclose(magnitude, 0.0, abs_tol=1e-9):
        neutral_weights = {k: 0.0 for k in factor_table.keys()}
        return ImpactResult(
            price_change=0.0,
            impact_score=0.0,
            dominant_factor="none",
            factors_with_weights=neutral_weights,
        )

    # Compute raw influence scores per factor: abs(base_multiplier) * magnitude
    raw: Dict[str, float] = {}
    for factor, base in factor_table.items():
        # The idea: factors with larger absolute base are more capable of explaining the price movement
        raw_score = abs(base) * magnitude
        # Optionally tweak by commodity/region heuristics here (not implemented)
        raw[factor] = raw_score

    # Normalize raw scores to percentages (sum to 100)
    total_raw = sum(raw.values()) or 1.0
    normalized = {f: (raw[f] / total_raw) * 100.0 for f in raw}

    # Determine dominant factor (largest normalized share)
    dominant_factor = max(normalized.items(), key=lambda it: it[1])[0]

    # Compute an overall impact_score on 0-100 scale.
    # Heuristic: impact should grow with magnitude but capped. We scale magnitude such that
    # 1.0 (100% change) yields a very strong impact (clamped to 100).
    # We apply a small boost based on concentration (if dominant factor is very dominant -> higher score).
    concentration = normalized[dominant_factor] / 100.0  # 0..1
    # base_score proportional to magnitude, scaled to 0..100 range:
    base_score = _clamp(magnitude * 500.0, 0.0, 100.0)
    # boost proportional to concentration (0..1) up to +20%
    boost = base_score * (concentration * 0.2)
    impact_score = _clamp(base_score + boost, 0.0, 100.0)

    # Round values for cleaner JSON
    normalized_rounded = {k: round(v, 2) for k, v in normalized.items()}
    impact_score_rounded = round(impact_score, 2)
    price_change_rounded = round(price_change, 6)

    return ImpactResult(
        price_change=price_change_rounded,
        impact_score=impact_score_rounded,
        dominant_factor=dominant_factor,
        factors_with_weights=normalized_rounded,
    )