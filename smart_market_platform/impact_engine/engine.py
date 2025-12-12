"""
Enhanced Impact Engine with Macro-Economic Fusion.
Uses the earlier heuristic impact engine ideas and applies macro adjustments.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime
import math

from ..macro_data.engine import MacroData
from ..core.impact_engine import compute_impact as base_compute_impact  # uses previous repo's compute_impact

@dataclass
class ImpactResult:
    price_change: float
    impact_score: float
    dominant_factor: str
    factors_with_weights: Dict[str, float]

def compute_impact_with_macro(prev_price: Optional[float], new_price: float, commodity: Optional[str]=None, market_id: Optional[str]=None, region: Optional[str]=None) -> ImpactResult:
    """
    Compute impact and fuse macroeconomic adjustments.
    """
    # Call base engine
    base = base_compute_impact(prev_price=prev_price, new_price=new_price, commodity=commodity, market_id=market_id, region=region)
    # Fetch macro coefficients (inflation, fuel, currency)
    macro = MacroData.get_current()
    # Adjust impact_score: e.g., if inflation high, amplify positive impact
    multiplier = 1.0 + (macro.inflation_rate * 0.5) + (macro.fuel_coefficient * 0.3)
    adjusted_score = min(100.0, base.impact_score * multiplier)
    # If currency depreciation is big, add small boost
    adjusted_score = round(adjusted_score, 2)
    return ImpactResult(price_change=base.price_change, impact_score=adjusted_score, dominant_factor=base.dominant_factor, factors_with_weights=base.factors_with_weights)