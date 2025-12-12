"""
HTTP client to send payloads to the platform ingest endpoint.
Uses aiohttp for async requests and Authorization: Bearer <token>.
"""
from __future__ import annotations

import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional

from .config import settings

logger = logging.getLogger("device_client.http")

class HTTPClient:
    def __init__(self, token: Optional[str] = None) -> None:
        self.base = settings.PLATFORM_HTTP_BASE.rstrip("/")
        self.ingest_url = self.base + settings.INGEST_PATH
        self.validation_url = self.base + settings.VALIDATION_PATH
        self.token = token
        self._session: Optional[aiohttp.ClientSession] = None

    async def _session_get(self) -> aiohttp.ClientSession:
        if self._session:
            return self._session
        self._session = aiohttp.ClientSession()
        return self._session

    async def send_ingest(self, payload: Dict[str, Any]) -> bool:
        session = await self._session_get()
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        try:
            async with session.post(self.ingest_url, json=payload, timeout=10, headers=headers) as resp:
                text = await resp.text()
                logger.debug("HTTP ingest status=%s body=%s", resp.status, text)
                return 200 <= resp.status < 300
        except Exception as exc:
            logger.warning("HTTP ingest error: %s", exc)
            return False

    async def validate(self, market_id: str, commodity: str, price: float, region: Optional[str] = None) -> Dict[str, Any]:
        session = await self._session_get()
        headers = {"Content-Type": "application/json"}
        try:
            body = {"market_id": market_id, "commodity": commodity, "price": price}
            if region:
                body["region"] = region
            async with session.post(self.validation_url, json=body, timeout=8, headers=headers) as resp:
                return await resp.json()
        except Exception as exc:
            logger.warning("Validation request failed: %s", exc)
            return {"error": str(exc)}
    async def close(self) -> None:
        if self._session:
            await self._session.close()
            self._session = None