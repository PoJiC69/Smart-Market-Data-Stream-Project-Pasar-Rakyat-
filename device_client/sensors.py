"""
Mock sensor implementations for device client.
Each sensor exposes an async read() method returning the value.
"""
from __future__ import annotations

import random
from typing import Dict
from datetime import datetime

class TemperatureSensor:
    def __init__(self, mock: bool = True) -> None:
        self.mock = mock

    async def read(self) -> float:
        if self.mock:
            return round(random.uniform(24.0, 32.0), 2)
        raise NotImplementedError("Real temperature sensor not implemented")

class HumiditySensor:
    def __init__(self, mock: bool = True) -> None:
        self.mock = mock

    async def read(self) -> float:
        if self.mock:
            return round(random.uniform(40.0, 85.0), 2)
        raise NotImplementedError("Real humidity sensor not implemented")

class CrowdSensor:
    def __init__(self, mock: bool = True) -> None:
        self.mock = mock

    async def read(self) -> int:
        if self.mock:
            return random.randint(0, 120)
        raise NotImplementedError("Real crowd sensor not implemented")

class CommodityPriceSensor:
    def __init__(self, mock: bool = True) -> None:
        self.mock = mock
        # basic list of commodities
        self.commodities = ["cabai", "bawang", "beras"]

    async def read(self) -> Dict[str, float]:
        if self.mock:
            return {c: float(round(random.uniform(8000, 25000), 0)) for c in self.commodities}
        raise NotImplementedError("Real commodity price sensor not implemented")