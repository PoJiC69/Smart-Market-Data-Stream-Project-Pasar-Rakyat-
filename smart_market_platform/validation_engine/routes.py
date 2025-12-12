"""
API router to expose validation endpoints.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from .engine import validate_price

router = APIRouter()

class ValidatePayload(BaseModel):
    market_id: str
    commodity: str
    price: float
    region: Optional[str] = None

@router.post("/price/check")
async def price_check(payload: ValidatePayload):
    res = validate_price(payload.market_id, payload.commodity, payload.price, payload.region)
    return res