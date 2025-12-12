"""
Pydantic models used by the realtime dashboard service.
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class PricePoint(BaseModel):
    timestamp: datetime
    market_id: str
    commodity: str
    price: float
    region: Optional[str] = None


class IngestPayload(BaseModel):
    """
    Accepts the MarketDataStream payload (or similar). Prices should be a dict of commodity->price.
    Example:
    {
      "timestamp": "2025-12-12T12:34:56.789Z",
      "market_id": "PASAR-001",
      "region": "JAKARTA",
      "prices": {
        "cabai": 15000,
        "bawang": 9000,
        "beras": 12000
      }
    }
    """
    timestamp: datetime
    market_id: str
    prices: Dict[str, float]
    region: Optional[str] = None


class LatestPricesResponse(BaseModel):
    market_id: str
    region: Optional[str]
    timestamp: datetime
    prices: Dict[str, float]


class HistoryRequest(BaseModel):
    market_id: str
    commodity: str
    limit: int = 200
    region: Optional[str] = None


class HistoryResponse(BaseModel):
    market_id: str
    commodity: str
    series: List[PricePoint]