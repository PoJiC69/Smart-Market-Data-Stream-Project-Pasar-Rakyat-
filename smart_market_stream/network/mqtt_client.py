"""
MQTT client using paho-mqtt. Runs network loop in background thread.

Provides an async-friendly send() interface by delegating publish calls to executor.
"""
from __future__ import annotations

import asyncio
import json
import time
from typing import Any, Dict, Optional

import paho.mqtt.client as mqtt

from ..core.config import LOGGER, load_config


class MQTTClient:
    """
    MQTT client wrapper.

    Uses paho-mqtt under the hood and an executor to provide async send().
    """

    def __init__(self, broker: Optional[str] = None, port: Optional[int] = None, topic: Optional[str] = None, client_id: str = "smart-market-stream") -> None:
        cfg = load_config()
        self.broker = broker or cfg["MQTT_BROKER"]
        self.port = port or cfg["MQTT_PORT"]
        self.topic = topic or cfg["MQTT_TOPIC"]
        self.client_id = client_id
        self._client = mqtt.Client(client_id=self.client_id)
        self._connected = False
        self._connect_lock = asyncio.Lock()
        self._setup_callbacks()
        # Start connect in background
        self._client.loop_start()
        try:
            self._client.connect(self.broker, self.port, keepalive=60)
            LOGGER.info("MQTTClient connecting to %s:%s", self.broker, self.port)
        except Exception:
            LOGGER.exception("MQTTClient initial connect failed; will attempt reconnects later.")

    def _setup_callbacks(self) -> None:
        def on_connect(client, userdata, flags, rc):
            nonlocal self
            if rc == 0:
                self._connected = True
                LOGGER.info("MQTT connected to broker %s:%s", self.broker, self.port)
            else:
                LOGGER.warning("MQTT connect returned code %s", rc)

        def on_disconnect(client, userdata, rc):
            nonlocal self
            self._connected = False
            LOGGER.warning("MQTT disconnected (rc=%s). Will attempt reconnect.", rc)
            # Attempt reconnect in a dedicated thread (paho does reconnection automatically in loop_start if configured)
            try:
                client.reconnect()
            except Exception:
                LOGGER.debug("MQTT reconnect immediate attempt failed; paho will keep trying.")

        self._client.on_connect = on_connect
        self._client.on_disconnect = on_disconnect

    async def send(self, payload: Dict[str, Any]) -> bool:
        """
        Async-friendly publish wrapper. Publishes JSON to configured topic.

        Returns:
            bool: True if publish call was queued successfully.
        """
        loop = asyncio.get_running_loop()
        try:
            message = json.dumps(payload, default=str)
            # Ensure at least connected or try to (best-effort)
            if not self._connected:
                LOGGER.debug("MQTT client not connected, attempting quick reconnect")
                try:
                    # paho reconnect is blocking; run in executor
                    await loop.run_in_executor(None, self._client.reconnect)
                    # small delay for connect callback
                    await asyncio.sleep(0.1)
                except Exception:
                    LOGGER.debug("MQTT quick reconnect failed")
            # Run publish in executor because it's blocking/synchronous
            fut = loop.run_in_executor(None, lambda: self._client.publish(self.topic, message, qos=1))
            result = await fut
            LOGGER.info("MQTTClient published to %s payload_size=%s", self.topic, len(message))
            return True
        except Exception as exc:
            LOGGER.exception("MQTTClient publish error: %s", exc)
            return False

    async def close(self) -> None:
        try:
            self._client.loop_stop()
            self._client.disconnect()
        except Exception:
            LOGGER.exception("MQTTClient close error")