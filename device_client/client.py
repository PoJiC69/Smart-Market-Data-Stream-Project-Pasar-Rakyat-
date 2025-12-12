"""
Main DeviceClient that orchestrates sensors, network clients, queue persistence and retries.
Provides:
- device registration (optional)
- periodic reading and sending
- enqueue on failure and periodic flush
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Optional, Dict, Any
from datetime import datetime

from .config import settings
from .sensors import TemperatureSensor, HumiditySensor, CrowdSensor, CommodityPriceSensor
from .http_client import HTTPClient
from .mqtt_client import MQTTClient
from .storage import init_db, enqueue, get_all, delete
from pathlib import Path

logger = logging.getLogger("device_client")

TOKEN_PATH = Path(settings.TOKEN_FILE)
TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)

def save_token(token: str) -> None:
    TOKEN_PATH.write_text(json.dumps({"token": token}))

def load_token() -> Optional[str]:
    try:
        return json.loads(TOKEN_PATH.read_text())["token"]
    except Exception:
        return None

class DeviceClient:
    def __init__(self, device_id: Optional[str] = None, market_id: Optional[str] = None, mode: Optional[str] = None, mock: Optional[bool] = None, interval: Optional[float] = None) -> None:
        self.device_id = device_id or settings.DEVICE_ID
        self.market_id = market_id or settings.MARKET_ID
        self.mode = mode or settings.MODE
        self.mock = settings.MOCK if mock is None else mock
        self.interval = settings.INTERVAL if interval is None else interval
        self.token = load_token()
        self.http_client = HTTPClient(token=self.token)
        self.mqtt_client = None
        if self.mode == "mqtt":
            self.mqtt_client = MQTTClient(device_id=self.device_id, token=self.token)
        self.temp = TemperatureSensor(mock=self.mock)
        self.hum = HumiditySensor(mock=self.mock)
        self.crowd = CrowdSensor(mock=self.mock)
        self.price_sensor = CommodityPriceSensor(mock=self.mock)
        init_db()
        self._stop = False

    async def register(self, server_base: Optional[str] = None) -> Dict[str, Any]:
        """
        Registers device via platform register endpoint.
        Returns dict with token and qr data-url if successful.
        """
        url = (server_base or settings.PLATFORM_HTTP_BASE).rstrip("/") + settings.REGISTER_PATH
        payload = {"market_id": self.market_id, "device_id": self.device_id, "role": "operator"}
        import aiohttp
        try:
            async with aiohttp.ClientSession() as s:
                async with s.post(url, json=payload, timeout=10) as resp:
                    data = await resp.json()
                    token = data.get("token")
                    if token:
                        save_token(token)
                        self.token = token
                        # reinitialize clients with token
                        self.http_client = HTTPClient(token=self.token)
                        if self.mode == "mqtt":
                            self.mqtt_client = MQTTClient(device_id=self.device_id, token=self.token)
                    return data
        except Exception as exc:
            logger.exception("Device registration failed: %s", exc)
            return {"error": str(exc)}

    async def _build_payload(self) -> Dict[str, Any]:
        t = await self.temp.read()
        h = await self.hum.read()
        c = await self.crowd.read()
        prices = await self.price_sensor.read()
        payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "market_id": self.market_id,
            "device_id": self.device_id,
            "temperature": t,
            "humidity": h,
            "crowd": c,
            "prices": prices,
        }
        return payload

    async def send_payload(self, payload: Dict[str, Any]) -> bool:
        # perform optional pre-validation (first commodity only) to get feedback
        try:
            if self.mode == "http":
                ok = await self.http_client.send_ingest(payload)
                if not ok:
                    enqueue(payload)
                    return False
                return True
            else:
                # mqtt
                if not self.mqtt_client:
                    self.mqtt_client = MQTTClient(device_id=self.device_id, token=self.token)
                ok = await self.mqtt_client.publish(payload)
                if not ok:
                    enqueue(payload)
                    return False
                return True
        except Exception as exc:
            logger.exception("send_payload error: %s", exc)
            enqueue(payload)
            return False

    async def flush_queue(self) -> None:
        queued = get_all()
        if not queued:
            return
        logger.info("Flushing %d queued payload(s)", len(queued))
        for item in queued:
            id_ = item["id"]
            payload = item["payload"]
            try:
                ok = await self.send_payload(payload)
                if ok:
                    delete(id_)
                else:
                    logger.debug("Flush failed for id=%s; keep in queue", id_)
            except Exception:
                logger.exception("Error while flushing id=%s", id_)

    async def run(self) -> None:
        logger.info("DeviceClient starting with device_id=%s market_id=%s mode=%s", self.device_id, self.market_id, self.mode)
        # background task: periodic flush
        async def queue_worker():
            while not self._stop:
                try:
                    await self.flush_queue()
                except Exception:
                    logger.exception("Error in queue worker")
                await asyncio.sleep(settings.RETRY_INTERVAL)

        qtask = asyncio.create_task(queue_worker())

        try:
            while not self._stop:
                payload = await self._build_payload()
                logger.debug("Built payload: %s", payload)
                ok = await self.send_payload(payload)
                if ok:
                    logger.info("Payload sent successfully")
                else:
                    logger.warning("Payload enqueued due to send failure")
                await asyncio.sleep(self.interval)
        except asyncio.CancelledError:
            logger.info("DeviceClient cancelled")
        finally:
            self._stop = True
            qtask.cancel()
            await asyncio.sleep(0.1)
            # close http session
            await self.http_client.close()
            if self.mqtt_client:
                self.mqtt_client.close()