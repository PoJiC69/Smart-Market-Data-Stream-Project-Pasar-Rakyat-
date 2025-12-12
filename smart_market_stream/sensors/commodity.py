"""
Commodity price sensor module.

Simulates reading daily commodity prices from a local JSON or API.
"""
from __future__ import annotations

import json
import random
from typing import Dict

from ..core.config import LOGGER


class CommodityPriceSensor:
    """
    Simulates commodity price readings. Returns dict with cabai, bawang, beras.
    """

    def __init__(self, mock: bool = True) -> None:
        self.mock = mock
        self.name = "CommodityPriceSensor"

    async def read(self) -> Dict[str, float]:
        """
        Return a dict of commodity prices in Indonesian Rupiah (IDR).

        Returns:
            Dict[str, float]: e.g. {"cabai": 12000.0, "bawang": 8000.0, "beras": 13000.0}
        """
        try:
            if self.mock:
                # Provide realistic-ish prices
                prices = {
                    "cabai": round(random.uniform(10000, 25000), 0),
                    "bawang": round(random.uniform(6000, 14000), 0),
                    "beras": round(random.uniform(9000, 16000), 0),
                }
            else:
                # Placeholder to read from file or API
                # Example: read JSON file path from env or call external API
                raise NotImplementedError("Commodity price real API not implemented.")
            LOGGER.debug("%s read: %s", self.name, prices)
            return prices
        except Exception as exc:
            LOGGER.warning("CommodityPriceSensor read error: %s", exc)
            # Return sentinel invalid values
            return {"cabai": -1.0, "bawang": -1.0, "beras": -1.0}