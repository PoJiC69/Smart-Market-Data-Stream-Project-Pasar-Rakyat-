"""
HTTP client to push market data to cloud server using aiohttp.
"""
from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, Optional

import aiohttp

from ..core.config import LOGGER, load_config


class HTTPClient:
    """
    Async HTTP client to push JSON payloads to a configured HTTP endpoint.
    """

    def __init__(self, endpoint: Optional[str] = None, session: Optional[aiohttp.ClientSession] = None) -> None:
        cfg = load_config()
        self.endpoint = endpoint or cfg["HTTP_ENDPOINT"]
        self.session = session
        self._internal_session: Optional[aiohttp.ClientSession] = None

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self.session:
            return self.session
        if not self._internal_session:
            self._internal_session = aiohttp.ClientSession()
        return self._internal_session

    async def send(self, payload: Dict[str, Any]) -> bool:
        """
        Send payload as JSON POST to configured endpoint.

        Returns:
            bool: True if successful
        """
        session = await self._ensure_session()
        try:
            async with session.post(self.endpoint, json=payload, timeout=10) as resp:
                text = await resp.text()
                if resp.status >= 200 and resp.status < 300:
                    LOGGER.info("HTTPClient pushed payload to %s status=%s", self.endpoint, resp.status)
                    return True
                else:
                    LOGGER.warning("HTTP push failed status=%s body=%s", resp.status, text)
                    return False
        except asyncio.TimeoutError:
            LOGGER.warning("HTTPClient timeout while pushing payload")
            return False
        except Exception as exc:
            LOGGER.exception("HTTPClient error: %s", exc)
            return False

    async def close(self) -> None:
        if self._internal_session:
            await self._internal_session.close()
            self._internal_session = None