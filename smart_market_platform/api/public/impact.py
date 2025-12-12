"""
Public impact endpoint proxies to the impact engine.
"""
from __future__ import annotations

from typing import Dict
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/impact")
async def get_impact(commodity: str, market_id: str, prev_price: float, new_price: float) -> Dict:
    from ...impact_engine.engine import compute_impact_with_macro
    res = compute_impact_with_macro(prev_price=prev_price, new_price=new_price, commodity=commodity, market_id=market_id)
    return {
        "commodity": commodity,
        "market_id": market_id,
        "price_change": res.price_change,
        "impact_score": res.impact_score,
        "dominant_factor": res.dominant_factor,
        "factors_with_weights": res.factors_with_weights,
    }