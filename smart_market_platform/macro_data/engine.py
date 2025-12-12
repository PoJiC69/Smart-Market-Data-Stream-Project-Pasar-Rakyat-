"""
Macro data simulation and coefficients.
Provides inflation_rate, currency_rate, fuel_coefficient, fertilizer_trend etc.
"""
from __future__ import annotations

from dataclasses import dataclass
import random
import datetime

@dataclass
class MacroData:
    inflation_rate: float  # e.g., 0.03 = 3%
    currency_rate: float   # IDR per USD (for context)
    fuel_coefficient: float  # 0..1 impact coefficient
    fertilizer_trend: float  # relative trend

    @staticmethod
    def get_current() -> "MacroData":
        # In production pull from external macro data sources (APIs). Here we simulate.
        return MacroData(
            inflation_rate=0.03 + random.uniform(-0.005, 0.01),
            currency_rate=15300 + random.uniform(-200, 500),
            fuel_coefficient=0.05 + random.uniform(0, 0.1),
            fertilizer_trend=0.02 + random.uniform(-0.01, 0.02),
        )