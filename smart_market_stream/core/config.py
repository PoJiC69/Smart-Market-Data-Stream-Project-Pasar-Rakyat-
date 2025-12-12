"""
Configuration loader and logger setup for Smart Market Stream
"""
from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env if exists
_env_path = BASE_DIR / ".env"
if _env_path.exists():
    load_dotenv(_env_path)
else:
    # Try default .env in CWD if present
    load_dotenv()

def get_env(key: str, default: Any = None) -> Any:
    return os.getenv(key, default)

def create_logger(name: str = "smart_market_stream") -> logging.Logger:
    """Create a module-wide logger with rotation."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # already configured

    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # Rotating file handler (optional, controlled by env)
    log_file = get_env("LOG_FILE", str(BASE_DIR / "logs" / "app.log"))
    try:
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        fh = RotatingFileHandler(log_file, maxBytes=int(get_env("LOG_MAX_BYTES", 5_242_880)), backupCount=int(get_env("LOG_BACKUP_COUNT", 5)))
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    except Exception:
        # Fallback to console-only if file cannot be created
        logger.exception("Could not create log file handler; continuing with console handler only.")

    return logger

# Default configuration accessible to rest of the app
LOGGER = create_logger()

def load_config() -> Dict[str, Any]:
    """Return a dict of runtime configuration pulled from environment variables."""
    cfg = {
        "MARKET_ID": get_env("MARKET_ID", "PASAR-001"),
        "PUSH_MODE": get_env("PUSH_MODE", "mqtt"),  # or http
        "HTTP_ENDPOINT": get_env("HTTP_ENDPOINT", "http://localhost:8000/ingest"),
        "MQTT_BROKER": get_env("MQTT_BROKER", "localhost"),
        "MQTT_PORT": int(get_env("MQTT_PORT", 1883)),
        "MQTT_TOPIC": get_env("MQTT_TOPIC", "pasar/data"),
        "INTERVAL": float(get_env("INTERVAL", 2.0)),
        "MOCK": get_env("MOCK", "true").lower() in ("1", "true", "yes"),
    }
    return cfg