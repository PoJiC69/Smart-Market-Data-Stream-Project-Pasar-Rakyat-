#!/usr/bin/env python3
"""
CLI Runner for smart_market_stream.

Usage:
    python main.py --mode mqtt --mock true
    python main.py --mode http --mock false
"""
from __future__ import annotations

import argparse
import asyncio
import signal
import sys

from smart_market_stream.core.config import LOGGER, load_config
from smart_market_stream.core.stream_manager import MarketDataStream
from smart_market_stream.network.http_client import HTTPClient
from smart_market_stream.network.mqtt_client import MQTTClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smart Market Data Stream Runner")
    parser.add_argument("--mode", choices=("mqtt", "http"), default=None, help="Push mode: mqtt or http")
    parser.add_argument("--mock", type=str, default=None, help="Enable mock sensors: true/false")
    parser.add_argument("--market-id", type=str, default=None, help="Market ID (default from .env or PASAR-001)")
    parser.add_argument("--interval", type=float, default=None, help="Push interval in seconds")
    return parser.parse_args()


async def _main() -> None:
    args = parse_args()
    cfg = load_config()

    # Override config with CLI args if provided
    if args.mode:
        cfg["PUSH_MODE"] = args.mode
    if args.mock is not None:
        cfg["MOCK"] = args.mock.lower() in ("1", "true", "yes")
    if args.market_id:
        cfg["MARKET_ID"] = args.market_id
    if args.interval:
        cfg["INTERVAL"] = args.interval

    LOGGER.info("Starting Smart Market Stream with config: %s", cfg)

    # Prepare clients
    http_client = None
    mqtt_client = None
    if cfg["PUSH_MODE"] == "http":
        http_client = HTTPClient(endpoint=cfg["HTTP_ENDPOINT"])
    else:
        mqtt_client = MQTTClient(broker=cfg["MQTT_BROKER"], port=cfg["MQTT_PORT"], topic=cfg["MQTT_TOPIC"])

    # Create stream
    from smart_market_stream.sensors.temperature import TemperatureSensor
    from smart_market_stream.sensors.humidity import HumiditySensor
    from smart_market_stream.sensors.crowd import CrowdSensor
    from smart_market_stream.sensors.commodity import CommodityPriceSensor

    sensors = [
        TemperatureSensor(mock=cfg["MOCK"]),
        HumiditySensor(mock=cfg["MOCK"]),
        CrowdSensor(mock=cfg["MOCK"]),
        CommodityPriceSensor(mock=cfg["MOCK"]),
    ]

    stream = MarketDataStream(
        market_id=cfg["MARKET_ID"],
        http_client=http_client,
        mqtt_client=mqtt_client,
        sensors=sensors,
        interval=cfg["INTERVAL"],
    )

    # Graceful shutdown handling
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def _signal_handler(*_) -> None:
        LOGGER.info("Received shutdown signal")
        stop_event.set()

    for s in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(s, _signal_handler)
        except NotImplementedError:
            # Windows Proactor loop may raise; fallback to default
            pass

    # Run the stream until stop_event is set
    task = asyncio.create_task(stream.start())
    await stop_event.wait()
    await stream.stop()
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        LOGGER.info("Stream task cancelled, shutting down.")

    # Close clients if present
    if http_client:
        await http_client.close()
    if mqtt_client:
        await mqtt_client.close()


if __name__ == "__main__":
    # Run top-level asyncio main
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        sys.exit(0)