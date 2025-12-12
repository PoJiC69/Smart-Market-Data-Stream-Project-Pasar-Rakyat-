"""
Humidity sensor module.

Provides HumiditySensor with optional mock mode.
"""
from __future__ import annotations

import random
from typing import Union

from ..core.config import LOGGER


class HumiditySensor:
    """
    Simulated Humidity Sensor.

    Returns relative humidity percentage.
    """

    def __init__(self, mock: bool = True) -> None:
        self.mock = mock
        self.name = "HumiditySensor"

    async def read(self) -> float:
        """
        Read current humidity percentage.

        Returns:
            float: humidity in %
        """
        try:
            if self.mock:
                value = round(random.uniform(40.0, 85.0), 2)
            else:
                raise NotImplementedError("Hardware humidity read not implemented.")
            LOGGER.debug("%s read: %s %%", self.name, value)
            return value
        except Exception as exc:
            LOGGER.warning("HumiditySensor read error: %s", exc)
            return float("nan")