"""
Crowd sensor module.

Provides CrowdSensor which simulates people counting or presence detection.
"""
from __future__ import annotations

import random
from typing import Any

from ..core.config import LOGGER


class CrowdSensor:
    """
    Simulate crowd estimation using PIR / ultrasonic / AI (mocked).

    Returns an integer representing number of people detected or an activity score.
    """

    def __init__(self, mock: bool = True) -> None:
        self.mock = mock
        self.name = "CrowdSensor"

    async def read(self) -> int:
        """
        Read the current crowd level.

        Returns:
            int: count of people or an index of crowd
        """
        try:
            if self.mock:
                # Simulate low to high crowd levels
                value = random.randint(0, 120)
            else:
                raise NotImplementedError("Hardware crowd read not implemented.")
            LOGGER.debug("%s read: %s people", self.name, value)
            return value
        except Exception as exc:
            LOGGER.warning("CrowdSensor read error: %s", exc)
            return -1