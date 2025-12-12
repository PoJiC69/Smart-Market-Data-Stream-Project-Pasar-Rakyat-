"""
Device and market listing endpoints for public API (developer-focused).
"""
from __future__ import annotations

from typing import List
from fastapi import APIRouter

router = APIRouter()

# NOTE: In a real system this would query DB. For now, return sample list.
@router.get("/market/list")
async def market_list():
    return [
        {"market_id": "PASAR-001", "region": "JAKARTA"},
        {"market_id": "PASAR-002", "region": "BANDUNG"},
        {"market_id": "PASAR-003", "region": "SURABAYA"},
    ]