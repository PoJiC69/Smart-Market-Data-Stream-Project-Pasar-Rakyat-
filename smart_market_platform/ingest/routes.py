from __future__ import annotations

from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

router = APIRouter()

# Try to import the realtime manager and payload model from the optional dashboard package.
# If that package/module isn't available in this environment, we'll still provide a safe /ingest
# endpoint that validates the payload shape and returns a helpful response.
try:
    from market_realtime_dashboard.models import IngestPayload
    from market_realtime_dashboard.app import manager as realtime_manager  # manager: RealtimeManager
    _HAS_REALTIME = True
except Exception:
    IngestPayload = None  # type: ignore
    realtime_manager = None  # type: ignore
    _HAS_REALTIME = False


@router.post("/ingest")
async def ingest(request: Request) -> JSONResponse:
    """
    Ingest endpoint for device clients and streamers.

    Expected JSON payload:
    {
      "timestamp": "2025-12-12T12:34:56.789Z",
      "market_id": "PASAR-001",
      "region": "JAKARTA",          # optional
      "prices": {"cabai": 15000, "bawang": 9000}
    }

    Behavior:
    - Validates payload shape.
    - If the realtime manager (market_realtime_dashboard) is available, it will process and broadcast the prices.
    - Returns a JSON summary including processed count or an informative message.
    """
    try:
        raw = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Basic validation with IngestPayload if available
    if IngestPayload is not None:
        try:
            p = IngestPayload(**raw)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Invalid payload: {exc}")
    else:
        # Minimal validation fallback
        if not isinstance(raw, dict) or "market_id" not in raw or "prices" not in raw:
            raise HTTPException(status_code=400, detail="Payload must include 'market_id' and 'prices' keys")
        # normalize timestamp
        p = raw  # type: ignore

    # Normalize timestamp to datetime
    ts = None
    try:
        if isinstance(p, dict):
            ts_raw = p.get("timestamp")
        else:
            ts_raw = p.timestamp  # p is pydantic model
        if ts_raw:
            # handle trailing Z
            if isinstance(ts_raw, str) and ts_raw.endswith("Z"):
                ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
            elif isinstance(ts_raw, str):
                ts = datetime.fromisoformat(ts_raw)
            else:
                ts = datetime.utcnow()
        else:
            ts = datetime.utcnow()
    except Exception:
        ts = datetime.utcnow()

    market_id = p.market_id if not isinstance(p, dict) else p["market_id"]
    prices = p.prices if not isinstance(p, dict) else p["prices"]
    region = getattr(p, "region", None) if not isinstance(p, dict) else p.get("region")

    processed = 0
    details = []

    if _HAS_REALTIME and realtime_manager is not None:
        # process_payload returns list of generated entries (one per commodity)
        produced = await realtime_manager.process_payload(timestamp=ts, market_id=market_id, prices=prices, region=region)
        processed = len(produced)
        # convert datetime to isoformat for JSON
        for e in produced:
            if isinstance(e.get("timestamp"), datetime):
                e["timestamp"] = e["timestamp"].isoformat()
            details.append(e)
        return JSONResponse({"status": "ok", "processed": processed, "details": details})
    else:
        # Realtime manager not available in this deployment; respond that ingest was received.
        # Optionally, you could persist to DB here if persistence models are present.
        return JSONResponse(
            {
                "status": "ok",
                "note": "ingest accepted by API but realtime manager not available in this deployment",
                "received": {"market_id": market_id, "region": region, "timestamp": ts.isoformat(), "prices_count": len(prices) if isinstance(prices, dict) else 0},
            }
        )