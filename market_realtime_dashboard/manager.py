"""
In-memory manager for price data and websocket broadcasting.

Extended to compute Price Impact via smart_market_stream.core.impact_engine.
Stores history entries with impact metadata so history and realtime streams include:
  price_change, impact_score, dominant_factor, factors_with_weights
"""
from __future__ import annotations

import asyncio
from collections import defaultdict, deque
from datetime import datetime
from typing import Deque, Dict, List, Optional, Tuple, Any

from .models import PricePoint  # used for typing clarity (we store dicts for flexibility)

# Import the impact engine from the main project package
from smart_market_stream.core.impact_engine import compute_impact, ImpactResult

MAX_HISTORY = 2000  # max points per market/commodity/region


class RealtimeManager:
    def __init__(self) -> None:
        # latest: market_id -> {"region":..., "timestamp": datetime, "prices": {...}, "impacts": {commodity: {...}}}
        self.latest: Dict[str, Dict[str, Any]] = {}
        # key: (market_id, commodity, region) -> deque[dict] (includes impact metadata)
        self.history: Dict[Tuple[str, str, Optional[str]], Deque[Dict[str, Any]]] = defaultdict(
            lambda: deque(maxlen=MAX_HISTORY)
        )
        # connected websockets: client_id -> (websocket, filters)
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

    async def process_payload(self, timestamp: datetime, market_id: str, prices: Dict[str, float], region: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Store prices into latest and history, compute impact metadata and broadcast produced entries.

        Returns the list of generated entry dicts (one per commodity) which include:
          - timestamp (datetime)
          - market_id
          - commodity
          - price
          - region
          - price_change
          - impact_score
          - dominant_factor
          - factors_with_weights
        """
        # Update latest structure
        self.latest[market_id] = {"region": region, "timestamp": timestamp, "prices": prices.copy(), "impacts": {}}

        produced: List[Dict[str, Any]] = []
        for commodity, price in prices.items():
            key = (market_id, commodity, region)
            dq = self.history.get(key, deque())

            prev_price = None
            if len(dq) > 0:
                prev_price = dq[-1].get("price")

            # Compute impact
            impact: ImpactResult = compute_impact(prev_price=prev_price, new_price=price, commodity=commodity, market_id=market_id, region=region)

            entry: Dict[str, Any] = {
                "timestamp": timestamp,
                "market_id": market_id,
                "commodity": commodity,
                "price": float(price),
                "region": region,
                "price_change": impact.price_change,
                "impact_score": impact.impact_score,
                "dominant_factor": impact.dominant_factor,
                "factors_with_weights": impact.factors_with_weights,
            }

            # Store in history and latest impacts
            self.history[key].append(entry)
            self.latest[market_id]["impacts"][commodity] = {
                "price_change": impact.price_change,
                "impact_score": impact.impact_score,
                "dominant_factor": impact.dominant_factor,
                "factors_with_weights": impact.factors_with_weights,
            }

            produced.append(entry)

        # Broadcast produced entries asynchronously
        asyncio.create_task(self._broadcast_updates(produced))
        return produced

    async def _broadcast_updates(self, points: List[Dict[str, Any]]) -> None:
        """
        Send price points (dicts) to connected clients filtered by their subscriptions.
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
                    if "market_id" in filters and filters["market_id"] and p.get("market_id") != filters["market_id"]:
                        continue
                    if "region" in filters and filters["region"] and p.get("region") != filters["region"]:
                        continue
                    if "commodities" in filters and filters["commodities"]:
                        if p.get("commodity") not in filters["commodities"]:
                            continue
                    filtered.append(p)

                if not filtered:
                    continue

                # prepare list of dicts with ISO timestamps
                payload_data = []
                for fp in filtered:
                    # shallow copy and convert timestamp
                    cp = fp.copy()
                    if isinstance(cp.get("timestamp"), datetime):
                        cp["timestamp"] = cp["timestamp"].isoformat()
                    payload_data.append(cp)

                payload = {"type": "price_update", "data": payload_data}
                await ws.send_json(payload)
            except Exception:
                # client likely disconnected or errored; remove it
                await self.unregister_client(cid)

    def get_latest(self, region: Optional[str] = None, commodities: Optional[List[str]] = None, markets: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Return list of latest prices respecting filters.
        Each item includes latest prices and impacts mapping per commodity.
        """
        out = []
        for market_id, meta in self.latest.items():
            if markets and market_id not in markets:
                continue
            if region and meta.get("region") != region:
                continue
            prices = meta.get("prices", {})
            impacts = meta.get("impacts", {})
            if commodities:
                prices = {c: prices.get(c) for c in commodities}
                impacts = {c: impacts.get(c) for c in commodities}
            out.append({
                "market_id": market_id,
                "region": meta.get("region"),
                "timestamp": meta.get("timestamp"),
                "prices": prices,
                "impacts": impacts,
            })
        return out

    def get_history(self, market_id: str, commodity: str, region: Optional[str] = None, limit: int = 200) -> List[Dict[str, Any]]:
        """
        Return historical time-series for a given market and commodity as list of dicts (latest last).
        Each item includes impact metadata.
        """
        key = (market_id, commodity, region)
        dq = self.history.get(key, deque())
        items = list(dq)[-limit:]
        return items