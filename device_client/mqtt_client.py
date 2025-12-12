"""
MQTT client wrapper for publishing payloads.
Uses paho-mqtt and runs network loop in a background thread.
Provides async-friendly publish via run_in_executor.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Optional, Dict, Any

import paho.mqtt.client as mqtt

from .config import settings

logger = logging.getLogger("device_client.mqtt")

class MQTTClient:
    def __init__(self, device_id: str, token: Optional[str] = None) -> None:
        self.broker = settings.MQTT_BROKER
        self.port = settings.MQTT_PORT
        self.topic = settings.MQTT_TOPIC
        self._client = mqtt.Client(client_id=device_id)
        self._connected = False
        if token:
            # use token as password
            self._client.username_pw_set(username=device_id, password=token)
        if settings.MQTT_USE_TLS:
            self._client.tls_set(ca_certs=settings.MQTT_TLS_CA, certfile=settings.MQTT_TLS_CERT, keyfile=settings.MQTT_TLS_KEY)
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.loop_start()
        try:
            self._client.connect(self.broker, self.port, keepalive=60)
        except Exception:
            logger.exception("Initial MQTT connect failed (will attempt reconnects)")

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._connected = True
            logger.info("MQTT connected to %s:%s", self.broker, self.port)
        else:
            logger.warning("MQTT connect failed rc=%s", rc)

    def _on_disconnect(self, client, userdata, rc):
        self._connected = False
        logger.warning("MQTT disconnected (rc=%s)", rc)

    async def publish(self, payload: Dict[str, Any]) -> bool:
        loop = asyncio.get_running_loop()
        try:
            message = json.dumps(payload, default=str, ensure_ascii=False)
            # ensure basic connection
            if not self._connected:
                try:
                    await loop.run_in_executor(None, self._client.reconnect)
                    await asyncio.sleep(0.1)
                except Exception:
                    logger.debug("MQTT quick reconnect failed")
            await loop.run_in_executor(None, lambda: self._client.publish(self.topic, message, qos=1))
            logger.info("MQTT published topic=%s size=%d", self.topic, len(message))
            return True
        except Exception as exc:
            logger.exception("MQTT publish error: %s", exc)
            return False

    def close(self) -> None:
        try:
            self._client.loop_stop()
            self._client.disconnect()
        except Exception:
            logger.exception("MQTT close error")