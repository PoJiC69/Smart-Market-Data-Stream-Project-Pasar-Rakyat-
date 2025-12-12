"""
Public API endpoints for commodity data.
"""
from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException
from ...dashboard.charts.manager import stats_manager  # lightweight stats manager used by API

router = APIRouter()

@router.get("/commodity/price/live")
async def price_live(commodity: str, region: Optional[str] = None):
    """
    Return latest price per market for a commodity (optionally filtered by region).
    """
    return await stats_manager.get_latest_price_for_commodity(commodity=commodity, region=region)

@router.get("/commodity/price/history")
async def price_history(commodity: str, market_id: str, limit: int = Query(200, ge=1, le=2000)):
    return await stats_manager.get_price_history(market_id=market_id, commodity=commodity, limit=limit)

@router.get("/forecast")
async def get_forecast(commodity: str):
    # proxy to forecast_engine
    from ...forecast_engine.routes import forecast_for_commodity
    return await forecast_for_commodity(commodity)