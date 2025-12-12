"""
Example FastAPI server to receive market data posts for local testing.

Run with:
uvicorn example_server.app:app --reload --port 8000
"""
from __future__ import annotations

from fastapi import FastAPI, Request
import logging

app = FastAPI()
logger = logging.getLogger("example_server")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(handler)


@app.post("/ingest")
async def ingest(request: Request):
    payload = await request.json()
    # Here you would validate, persist, or forward the data
    logger.info("Received payload: %s", payload)
    return {"status": "ok", "received": True}