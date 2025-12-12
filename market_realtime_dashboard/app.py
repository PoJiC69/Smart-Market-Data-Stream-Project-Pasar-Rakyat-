"""
FastAPI application providing:

- /ingest            POST  -> accept MarketDataStream payloads and store/broadcast prices
- /prices/latest     GET   -> latest price per market (supports filters)
- /prices/history    GET   -> historical price series for market+commodity
- /ws/prices         WebSocket -> real-time price updates

Also serves a simple frontend dashboard at /dashboard (static HTML + JS using Chart.js).
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .manager import RealtimeManager
from .models import IngestPayload, LatestPricesResponse, HistoryResponse, PricePoint

app = FastAPI(title="Market Realtime Dashboard")

# Allow broad CORS for dashboard + local streamer/dev use
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static frontend
app.mount("/static", StaticFiles(directory="market_realtime_dashboard/static"), name="static")

manager = RealtimeManager()


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    """
    Simple redirect or HTML landing that links to dashboard.
    """
    html = """
    <html>
      <head><meta charset="utf-8"><title>Market Realtime Dashboard</title></head>
      <body>
        <h2>Market Realtime Dashboard</h2>
        <p>Open the dashboard: <a href="/static/index.html" target="_blank">Dashboard</a></p>
      </body>
    </html>
    """
    return HTMLResponse(html)


@app.post("/ingest")
async def ingest(payload: Dict) -> JSONResponse:
    """
    Accept incoming MarketDataStream payloads.

    Expected JSON fields:
    - timestamp (ISO string)
    - market_id
    - prices: dict of commodity->price
    - region (optional)
    """
    try:
        p = IngestPayload(**payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {exc}")

    # store and broadcast
    await manager.process_payload(timestamp=p.timestamp, market_id=p.market_id, prices=p.prices, region=p.region)
    return JSONResponse({"status": "ok", "processed": True})


@app.get("/prices/latest")
async def prices_latest(
    region: Optional[str] = Query(None),
    commodities: Optional[str] = Query(None, description="Comma-separated commodity list"),
    markets: Optional[str] = Query(None, description="Comma-separated market_id list"),
):
    """
    Return latest prices per market. Supports filtering by region, commodity list, or market list.

    Example:
    GET /prices/latest?commodities=cabai,bawang&region=JAKARTA
    """
    comms = commodities.split(",") if commodities else None
    mks = markets.split(",") if markets else None
    latest = manager.get_latest(region=region, commodities=comms, markets=mks)
    # Ensure timestamps are ISO strings
    for item in latest:
        if isinstance(item.get("timestamp"), datetime):
            item["timestamp"] = item["timestamp"].isoformat()
    return JSONResponse(latest)


@app.get("/prices/history")
async def prices_history(
    market_id: str = Query(...),
    commodity: str = Query(...),
    region: Optional[str] = Query(None),
    limit: int = Query(200, ge=1, le=2000),
):
    """
    Return historical time-series for a given market and commodity.

    Example:
    GET /prices/history?market_id=PASAR-001&commodity=cabai&limit=500
    """
    items = manager.get_history(market_id=market_id, commodity=commodity, region=region, limit=limit)
    # Convert PricePoint models to JSON-friendly dicts
    out = [p.dict() for p in items]
    # Convert timestamps to isoformat
    for o in out:
        o["timestamp"] = o["timestamp"].isoformat()
    return JSONResponse(out)


@app.websocket("/ws/prices")
async def websocket_prices(websocket: WebSocket):
    """
    WebSocket endpoint for real-time price updates.

    Optional query params on connect:
    - market_id
    - commodity (comma-separated)
    - region

    Alternatively, client may send a subscribe JSON message after connecting:
    {"action":"subscribe","market_id":"PASAR-001","commodities":["cabai","beras"],"region":"JAKARTA"}

    Server will send messages:
    {"type":"price_update","data":[{PricePoint}, ...]}
    """
    await websocket.accept()
    # parse filters from query params
    qs = dict(websocket.query_params)
    filters = {
        "market_id": qs.get("market_id"),
        "region": qs.get("region"),
        "commodities": qs.get("commodity").split(",") if qs.get("commodity") else None,
    }
    client_id = await manager.register_client(websocket, filters)
    try:
        # Keep connection active; allow client to send subscription messages
        while True:
            try:
                msg = await websocket.receive_json()
                if isinstance(msg, dict):
                    action = msg.get("action")
                    if action == "subscribe":
                        # update filters for this client
                        new_filters = {
                            "market_id": msg.get("market_id"),
                            "region": msg.get("region"),
                            "commodities": msg.get("commodities"),
                        }
                        # update stored filters
                        async with manager._lock:
                            if client_id in manager._clients:
                                ws, _ = manager._clients[client_id]
                                manager._clients[client_id] = (ws, new_filters)
                    # additional actions can be handled here
            except WebSocketDisconnect:
                break
            except Exception:
                # no message or invalid JSON; simply continue to keep connection open
                await asyncio.sleep(0.1)
    finally:
        await manager.unregister_client(client_id)