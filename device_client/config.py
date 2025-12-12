"""
Configuration loader for the device client.
Loads settings from environment or .env file.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
_env = BASE_DIR / ".env"
if _env.exists():
    load_dotenv(_env)
else:
    load_dotenv()  # fallback to env

@dataclass
class Settings:
    PLATFORM_HTTP_BASE: str = os.getenv("PLATFORM_HTTP_BASE", "http://localhost:8000")
    REGISTER_PATH: str = os.getenv("REGISTER_PATH", "/api/auth/device/register")
    INGEST_PATH: str = os.getenv("INGEST_PATH", "/ingest")
    VALIDATION_PATH: str = os.getenv("VALIDATION_PATH", "/api/validation/price/check")
    MODE: str = os.getenv("MODE", "http")  # 'http' or 'mqtt'
    INTERVAL: float = float(os.getenv("INTERVAL", "2.0"))
    DEVICE_ID: str = os.getenv("DEVICE_ID", "DEV-001")
    MARKET_ID: str = os.getenv("MARKET_ID", "PASAR-001")
    MOCK: bool = os.getenv("MOCK", "true").lower() in ("1", "true", "yes")
    TOKEN_FILE: str = os.getenv("TOKEN_FILE", str(Path.home() / ".smart_market_client" / "token.json"))
    QUEUE_DB: str = os.getenv("QUEUE_DB", str(Path.home() / ".smart_market_client" / "queue.db"))
    MQTT_BROKER: str = os.getenv("MQTT_BROKER", "localhost")
    MQTT_PORT: int = int(os.getenv("MQTT_PORT", "1883"))
    MQTT_TOPIC: str = os.getenv("MQTT_TOPIC", "pasar/data")
    MQTT_USE_TLS: bool = os.getenv("MQTT_USE_TLS", "false").lower() in ("1", "true", "yes")
    MQTT_TLS_CA: Optional[str] = os.getenv("MQTT_TLS_CA")
    MQTT_TLS_CERT: Optional[str] = os.getenv("MQTT_TLS_CERT")
    MQTT_TLS_KEY: Optional[str] = os.getenv("MQTT_TLS_KEY")
    RETRY_INTERVAL: float = float(os.getenv("RETRY_INTERVAL", "5.0"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()