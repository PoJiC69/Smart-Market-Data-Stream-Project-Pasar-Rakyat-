"""
Alerts manager: detects anomalies and pushes alerts via websocket and mock integrations.
"""
from __future__ import annotations

import asyncio
from datetime import datetime
from typing import List, Dict, Optional
import logging

from ..config import settings

logger = logging.getLogger("alerts")

class AlertsManager:
    _instance = None

    def __init__(self):
        self._recent: List[Dict] = []
        self._subscribers: List = []
        self._lock = asyncio.Lock()

    @classmethod
    def get_instance(cls) -> "AlertsManager":
        if cls._instance is None:
            cls._instance = AlertsManager()
        return cls._instance

    async def push_alert(self, alert: Dict):
        """
        Store and broadcast alert to websocket subscribers. Also send mock Telegram/WhatsApp.
        """
        alert["timestamp"] = datetime.utcnow().isoformat()
        async with self._lock:
            self._recent.insert(0, alert)
            self._recent = self._recent[:200]
        # broadcast to websocket subscribers
        for ws in list(self._subscribers):
            try:
                await ws.send_json({"type": "alert", "data": alert})
            except Exception:
                try:
                    self._subscribers.remove(ws)
                except Exception:
                    pass
        # mock external sends
        if settings.TELEGRAM_TOKEN:
            logger.info("Mock send to Telegram: %s", alert)
        if settings.WHATSAPP_TOKEN:
            logger.info("Mock send to WhatsApp: %s", alert)

    async def get_recent_alerts(self, limit: int = 50):
        return self._recent[:limit]

    async def register_ws(self, websocket):
        self._subscribers.append(websocket)

    async def unregister_ws(self, websocket):
        try:
            self._subscribers.remove(websocket)
        except Exception:
            pass

# background worker example
async def start_alert_worker():
    """
    Periodic worker that checks some condition and triggers alerts.
    For demo, it sleeps and does nothing. Could be extended to subscribe to price stream.
    """
    am = AlertsManager.get_instance()
    while True:
        await asyncio.sleep(60)  # placeholder