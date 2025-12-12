"""
Configuration and shared utilities for Smart Market Platform.
Loads environment variables and provides async DB engine/session.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()  # load .env if present

@dataclass
class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Smart Market Platform")
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("1", "true", "yes")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./sm_platform.db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "changeme")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    MQTT_TLS_CERT: Optional[str] = os.getenv("MQTT_TLS_CERT")
    MQTT_TLS_KEY: Optional[str] = os.getenv("MQTT_TLS_KEY")
    ALERT_THRESHOLD: float = float(os.getenv("ALERT_THRESHOLD", "0.6"))  # impact score threshold 0..1
    TELEGRAM_TOKEN: Optional[str] = os.getenv("TELEGRAM_TOKEN")
    WHATSAPP_TOKEN: Optional[str] = os.getenv("WHATSAPP_TOKEN")

settings = Settings()