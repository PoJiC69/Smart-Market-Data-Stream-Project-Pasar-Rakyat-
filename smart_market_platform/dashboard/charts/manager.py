"""
A tiny stats manager to serve public API endpoints; in production this would be backed by DB.
"""
from __future__ import annotations

import asyncio
from typing import Dict, List
from datetime import datetime, timedelta
import random

class StatsManager:
    def __init__(self):
        self._lock = asyncio.Lock()
        self._history = {}  # key -> list of dict entries

    async def get_latest_price_for_commodity(self, commodity: str, region: str = None):
        # return mock latest across markets
        return [
            {"market_id": "PASAR-001", "region": "JAKARTA", "commodity": commodity, "price": float(random.uniform(10000,25000)), "timestamp": datetime.utcnow().isoformat()},
            {"market_id": "PASAR-002", "region": "BANDUNG", "commodity": commodity, "price": float(random.uniform(9000,20000)), "timestamp": datetime.utcnow().isoformat()},
        ]

    async def get_price_history(self, market_id: str, commodity: str, limit: int = 200):
        data = []
        now = datetime.utcnow()
        for i in range(limit):
            data.append({"timestamp": (now - timedelta(minutes=limit-i)).isoformat(), "market_id": market_id, "commodity": commodity, "price": float(10000 + random.random()*5000)})
        return data

stats_manager = StatsManager()