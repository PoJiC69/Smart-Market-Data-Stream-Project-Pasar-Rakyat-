"""
Supply chain API: stock monitoring and route analysis.
"""
from __future__ import annotations

from fastapi import APIRouter
from typing import Dict, Any

from .analyzer import analyze_route

router = APIRouter()

@router.get("/stock/{entity_id}")
async def get_stock(entity_id: str):
    # mock inventory status
    return {"entity_id": entity_id, "items": {"cabai": 1200, "beras": 5000, "bawang": 800}, "last_updated": "2025-01-01T00:00:00Z"}

@router.get("/route/analyze")
async def route_analyze(route_id: str, distance_km: float = 10.0):
    res = analyze_route(route_id, distance_km)
    return res.__dict__