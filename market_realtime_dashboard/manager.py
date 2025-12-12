"""
In-memory manager for price data and websocket broadcasting.

Stores:
- latest_prices: dict[market_id] -> {"region": ..., "timestamp": ..., "prices": {...}}
- history: dict[(market_id, commodity, region)] -> deque[PricePoint]

Broadcasts price updates to connected WebSocket clients.
"""
from __future__ import annotations

import asyncio
from collections import defaultdict, deque
from datetime import datetime
from typing import Deque, Dict, List, Optional, Tuple

from .models import PricePoint

MAX_HISTORY = 2000  # max points per market/commodity/region


class RealtimeManager:
    def __init__(self) -> None:
        self.latest: Dict[str, Dict] = {}  # market_id -> {"region":..., "timestamp":..., "prices": {...}}
        # key: (market_id, commodity, region) -> deque[PricePoint]
        self.history: Dict[Tuple[str, str, Optional[str]], Deque[PricePoint]] = defaultdict(lambda: deque(maxlen=MAX_HISTORY))
        # connected websockets: set of (websocket, filters)
        self._clients: Dict[int, Tuple["WebSocket", Dict]] = {}
        self._client_id_seq = 0
        self._lock = asyncio.Lock()

    async def register_client(self, websocket, filters: Dict) -> int:
        """
        Register a connected client and return assigned client_id.
        filters: dict with optional 'market_id' and 'commodities' (list) and 'region'
        """
        async with self._lock:
            self._client_id_seq += 1
            cid = self._client_id_seq
            self._clients[cid] = (websocket, filters)
            return cid

    async def unregister_client(self, client_id: int) -> None:
        async with self._lock:
            self._clients.pop(client_id, None)

    async def process_payload(self, timestamp: datetime, market_id: str, prices: Dict[str, float], region: Optional[str] = None) -> List[PricePoint]:
        """
        Store prices into latest and history and broadcast produced PricePoint list.
        Returns the list of generated PricePoint objects.
        """
        # Update latest
        self.latest[market_id] = {"region": region, "timestamp": timestamp, "prices": prices.copy()}

        produced: List[PricePoint] = []
        for commodity, price in prices.items():
            pp = PricePoint(timestamp=timestamp, market_id=market_id, commodity=commodity, price=float(price), region=region)
            key = (market_id, commodity, region)
            self.history[key].append(pp)
            produced.append(pp)

        # Broadcast asynchronously (do not await here; caller may await broadcast)
        asyncio.create_task(self._broadcast_updates(produced))
        return produced

    async def _broadcast_updates(self, points: List[PricePoint]) -> None:
        """
        Send price points to connected clients filtered by their subscriptions.
        If sending to a client fails, unregister it.
        """
        # snapshot clients to avoid long locking
        async with self._lock:
            clients_items = list(self._clients.items())

        for cid, (ws, filters) in clients_items:
            try:
                # determine which points match client's filters
                filtered = []
                for p in points:
                    if "market_id" in filters and filters["market_id"] and p.market_id != filters["market_id"]:
                        continue
                    if "region" in filters and filters["region"] and p.region != filters["region"]:
                        continue
                    if "commodities" in filters and filters["commodities"]:
                        if p.commodity not in filters["commodities"]:
                            continue
                    filtered.append(p)

                if not filtered:
                    continue

                # prepare list of dicts
                payload = {
                    "type": "price_update",
                    "data": [fp.dict() for fp in filtered],
                }
                await ws.send_json(payload)
            except Exception:
                # client likely disconnected or errored; remove it
                await self.unregister_client(cid)

    def get_latest(self, region: Optional[str] = None, commodities: Optional[List[str]] = None, markets: Optional[List[str]] = None) -> List[Dict]:
        """
        Return list of latest prices respecting filters.
        """
        out = []
        for market_id, meta in self.latest.items():
            if markets and market_id not in markets:
                continue
            if region and meta.get("region") != region:
                continue
            prices = meta.get("prices", {})
            if commodities:
                prices = {c: prices.get(c) for c in commodities}
            out.append({
                "market_id": market_id,
                "region": meta.get("region"),
                "timestamp": meta.get("timestamp"),
                "prices": prices,
            })
        return out

    def get_history(self, market_id: str, commodity: str, region: Optional[str] = None, limit: int = 200) -> List[PricePoint]:
        key = (market_id, commodity, region)
        dq = self.history.get(key, deque())
        # Return last `limit` points as list
        items = list(dq)[-limit:]
        return items