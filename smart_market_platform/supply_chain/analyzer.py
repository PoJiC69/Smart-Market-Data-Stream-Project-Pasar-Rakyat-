"""
Route condition analyzer and logistic delay estimator.
Simple heuristics combining weather/traffic/disaster simulation.
"""
from __future__ import annotations

from dataclasses import dataclass
import random

@dataclass
class RouteCondition:
    route_id: str
    distance_km: float
    weather_score: float  # 0..1 (1 bad)
    traffic_score: float
    disaster_score: float
    estimated_delay_minutes: int

def analyze_route(route_id: str, distance_km: float) -> RouteCondition:
    # Mock weather/traffic/disaster scores
    weather = random.random() * 0.6  # 0..0.6
    traffic = random.random() * 0.6
    disaster = random.random() * 0.3
    # Estimate delay: base per km + additive effects
    base = int(distance_km * 2)  # 2 minutes per km
    penalty = int((weather + traffic + disaster) * 100)
    delay = base + penalty
    return RouteCondition(route_id=route_id, distance_km=distance_km, weather_score=round(weather,2), traffic_score=round(traffic,2), disaster_score=round(disaster,2), estimated_delay_minutes=delay)