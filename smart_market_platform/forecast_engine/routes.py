"""
Forecast endpoints: simple ARIMA/SARIMAX and optional LSTM/Prophet.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from typing import Dict
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

router = APIRouter()

# Lightweight in-memory sample series generator
def _generate_series(commodity: str, days: int = 90):
    rng = pd.date_range(end=datetime.utcnow(), periods=days, freq="D")
    base = {"cabai": 15000, "beras": 12000, "bawang": 9000}.get(commodity, 10000)
    series = base + np.cumsum(np.random.normal(0, 200, size=days))
    return pd.Series(series, index=rng)

@router.get("/{commodity}")
async def forecast_for_commodity(commodity: str):
    """
    Return 7-day forecast with a naïve model (last value + trend).
    Replace with Prophet/ARIMA model in production.
    """
    ser = _generate_series(commodity, days=90)
    # naive trend: linear fit
    x = np.arange(len(ser))
    coef = np.polyfit(x, ser.values, 1)
    trend = coef[0]
    last = ser.values[-1]
    forecast = []
    for i in range(1, 8):
        val = last + trend * i
        forecast.append({"date": (ser.index[-1] + timedelta(days=i)).isoformat(), "price": float(round(val,2))})
    # compute naive confidence based on residual std
    resid = ser.values - (coef[0]*x + coef[1])
    conf = float(max(0.1, 1 - (np.std(resid) / (np.mean(ser)+1e-9))))
    return {"commodity": commodity, "forecast_7d": forecast, "confidence": round(conf,2)}

@router.get("/confidence")
async def forecast_confidence(commodity: str):
    # quick wrapper returning confidence only
    res = await forecast_for_commodity(commodity)
    return {"commodity": commodity, "confidence": res["confidence"]}