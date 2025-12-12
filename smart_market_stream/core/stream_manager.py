"""
MarketDataStream: collects sensors and pushes payloads to configured network client.
"""
from __future__ import annotations

import asyncio
import datetime
import json
from typing import Any, Dict, List

from ..core.config import LOGGER, load_config
from ..sensors.temperature import TemperatureSensor
from ..sensors.humidity import HumiditySensor
from ..sensors.crowd import CrowdSensor
from ..sensors.commodity import CommodityPriceSensor
from ..network.http_client import HTTPClient
from ..network.mqtt_client import MQTTClient


class MarketDataStream:
    """
    Collect readings from sensors and push unified payloads periodically.

    Usage:
        stream = MarketDataStream(...); await stream.start()
    """

    def __init__(
        self,
        market_id: str,
        http_client: HTTPClient | None = None,
        mqtt_client: MQTTClient | None = None,
        sensors: List[Any] | None = None,
        interval: float = 2.0,
    ) -> None:
        self.cfg = load_config()
        self.market_id = market_id
        self.interval = interval
        self.http_client = http_client
        self.mqtt_client = mqtt_client
        self._task: asyncio.Task | None = None
        self._stopped = asyncio.Event()

        # Default sensors if none provided
        if sensors is None:
            mock = bool(self.cfg.get("MOCK"))
            sensors = [
                TemperatureSensor(mock=mock),
                HumiditySensor(mock=mock),
                CrowdSensor(mock=mock),
                CommodityPriceSensor(mock=mock),
            ]
        self.sensors = sensors

    async def _collect(self) -> Dict[str, Any]:
        # call each sensor read concurrently
        # Map sensors by class name
        readings = {}
        coros = [s.read() for s in self.sensors]
        results = await asyncio.gather(*coros, return_exceptions=True)
        # Assign by type
        temp, hum, crowd, prices = None, None, None, None
        for r in results:
            if isinstance(r, Exception):
                LOGGER.warning("Sensor read returned exception: %s", r)
        # Matching based on sensor classes in order
        try:
            temp = float(results[0])
        except Exception:
            temp = None
        try:
            hum = float(results[1])
        except Exception:
            hum = None
        try:
            crowd = int(results[2])
        except Exception:
            crowd = None
        try:
            prices = results[3] if isinstance(results[3], dict) else {}
        except Exception:
            prices = {}

        payload = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "market_id": self.market_id,
            "temperature": temp if temp is not None else None,
            "humidity": hum if hum is not None else None,
            "crowd": crowd if crowd is not None else None,
            "prices": {
                "cabai": prices.get("cabai", None),
                "bawang": prices.get("bawang", None),
                "beras": prices.get("beras", None),
            },
        }
        return payload

    async def _push(self, payload: Dict[str, Any]) -> None:
        mode = self.cfg.get("PUSH_MODE", "mqtt")
        # Prefer explicit client passed in
        if mode == "http":
            client = self.http_client or HTTPClient()
            ok = await client.send(payload)
            if not ok:
                LOGGER.warning("Failed to push payload over HTTP")
        else:
            client = self.mqtt_client or MQTTClient()
            ok = await client.send(payload)
            if not ok:
                LOGGER.warning("Failed to push payload over MQTT")

    async def start(self) -> None:
        """Start the main loop until stop() is called."""
        LOGGER.info("MarketDataStream starting with interval=%s", self.interval)
        self._stopped.clear()
        try:
            while not self._stopped.is_set():
                payload = await self._collect()
                LOGGER.info("Collected payload: %s", json.dumps(payload, ensure_ascii=False))
                await self._push(payload)
                await asyncio.wait_for(self._stopped.wait(), timeout=self.interval)
        except asyncio.TimeoutError:
            # expected timeout for periodic loop; continue
            pass
        except asyncio.CancelledError:
            LOGGER.info("MarketDataStream cancelled")
        except Exception as exc:
            LOGGER.exception("MarketDataStream loop error: %s", exc)

    def run_forever(self) -> None:
        """Convenience sync runner for quick scripts."""
        try:
            asyncio.run(self.start())
        except KeyboardInterrupt:
            LOGGER.info("Stopped by keyboard interrupt")

    async def stop(self) -> None:
        """Stop the stream gracefully."""
        self._stopped.set()
        LOGGER.info("MarketDataStream stopping")