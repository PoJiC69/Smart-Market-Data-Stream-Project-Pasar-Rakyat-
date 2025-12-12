```markdown
# Market Realtime Dashboard (market_realtime_dashboard)

This module provides a FastAPI-based realtime dashboard and WebSocket feed for commodity prices across multiple Indonesian markets and regions.

Features:
- /ingest POST endpoint to accept incoming market payloads (same format as MarketDataStream)
- /prices/latest GET endpoint for current/latest prices per market
- /prices/history GET endpoint for historical time-series (market+commodity)
- /ws/prices WebSocket endpoint for streaming live price events to dashboard clients
- Simple frontend dashboard using Chart.js (served under /static)

Run the dashboard (development):
1. Install dependencies (see root `requirements.txt` for FastAPI / uvicorn)
2. Start the server:
   uvicorn market_realtime_dashboard.app:app --reload --port 8000
3. Open the dashboard:
   http://localhost:8000/static/index.html

Integrating with Smart Market Stream:
- Point Smart Market Stream's HTTP endpoint to http://localhost:8000/ingest (update .env or CLI)
- Example .env:
  HTTP_ENDPOINT=http://localhost:8000/ingest
- When the streamer POSTS its payload, the dashboard stores latest & history and broadcasts updates to connected WebSocket clients.

Endpoints:
- POST /ingest
  Accepts JSON IngestPayload:
  {
    "timestamp": "2025-12-12T12:34:56.789Z",
    "market_id": "PASAR-001",
    "region": "JAKARTA",
    "prices": {"cabai": 15000, "bawang": 9000}
  }

- GET /prices/latest
  Query params: region, commodities (comma separated), markets (comma separated)
  Returns a list of latest price objects.

- GET /prices/history
  Query params: market_id (required), commodity (required), region (optional), limit
  Returns an array of PricePoint objects.

- WS  /ws/prices
  Connect with optional query params: market_id, commodity (comma-separated), region
  Server will push:
  {"type": "price_update", "data":[{PricePoint}, ...]}

Notes:
- This module uses in-memory storage (fast & simple). For production use, plug a persistent store (TimescaleDB, InfluxDB, Redis streams, etc.)
- The WebSocket manager supports per-client filters so multiple markets/commodities can be streamed to different clients.
```