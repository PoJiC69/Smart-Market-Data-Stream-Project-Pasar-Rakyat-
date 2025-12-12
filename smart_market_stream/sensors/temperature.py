"""
Temperature sensor module.

Provides TemperatureSensor with optional mock mode.
"""
from __future__ import annotations

import random
import time
from typing import Union

from ..core.config import LOGGER


class TemperatureSensor:
    """
    Simulated Temperature Sensor.

    In mock mode returns a randomized temperature.
    In real mode this class should be extended to integrate with hardware drivers.
    """

    def __init__(self, mock: bool = True) -> None:
        self.mock = mock
        self.name = "TemperatureSensor"

    async def read(self) -> float:
        """
        Read current temperature in Celsius.

        Returns:
            float: temperature value in °C
        """
        try:
            if self.mock:
                # small jitter and occasional spikes
                base = random.uniform(24.0, 32.0)
                jitter = random.uniform(-0.5, 0.5)
                value = round(base + jitter, 2)
            else:
                # Placeholder for real sensor reading.
                # Insert hardware integration here.
                raise NotImplementedError("Hardware temperature read not implemented.")
            LOGGER.debug("%s read: %s °C", self.name, value)
            return value
        except Exception as exc:  # pragma: no cover - defensive
            LOGGER.warning("TemperatureSensor read error: %s", exc)
            # fallback/failure sentinel
            return float("nan")