"""
Validation & Anti-Manipulation System.

- Outlier detection (Z-score, IQR)
- Simple AI anomaly detector stub (LSTM/Prophet optional)
- Multi-source verification (mocked)
- Quarantine suspicious entries flagging
"""
from __future__ import annotations

import math
from collections import deque
from typing import Dict, List, Tuple, Optional
import numpy as np
import statistics
import logging

logger = logging.getLogger("validation_engine")

# In-memory store per (market, commodity) for quick stats. For production, use DB/time-series store.
STATS_WINDOW = 500
_store: Dict[Tuple[str, str, Optional[str]], deque] = {}

def _get_window(market_id: str, commodity: str, region: Optional[str]):
    key = (market_id, commodity, region)
    if key not in _store:
        _store[key] = deque(maxlen=STATS_WINDOW)
    return _store[key]

def zscore_outlier(window: List[float], value: float, threshold: float = 3.0) -> bool:
    if len(window) < 2:
        return False
    mean = statistics.mean(window)
    stdev = statistics.pstdev(window)
    if stdev == 0:
        return False
    z = (value - mean) / stdev
    logger.debug("Z-Score check value=%s mean=%s stdev=%s z=%s", value, mean, stdev, z)
    return abs(z) > threshold

def iqr_outlier(window: List[float], value: float, multiplier: float = 1.5) -> bool:
    if len(window) < 4:
        return False
    arr = sorted(window)
    q1 = np.percentile(arr, 25)
    q3 = np.percentile(arr, 75)
    iqr = q3 - q1
    lower = q1 - multiplier * iqr
    upper = q3 + multiplier * iqr
    logger.debug("IQR check value=%s lower=%s upper=%s", value, lower, upper)
    return value < lower or value > upper

def ai_anomaly_detector(window: List[float], value: float) -> bool:
    """
    Placeholder AI anomaly detector.
    In production replace with LSTM/Prophet model inference.
    For now, we use a lightweight rule: large deviation relative to rolling median.
    """
    if len(window) < 10:
        return False
    median = statistics.median(window)
    if median == 0:
        return False
    rel = abs(value - median) / (median + 1e-9)
    logger.debug("AI anomaly detector rel=%s", rel)
    return rel > 0.5  # arbitrary

def multi_source_verify(market_id: str, commodity: str, value: float) -> Tuple[bool, List[Dict]]:
    """
    Verify price against other sources. For demo we simulate sources.
    Returns (all_sources_agree, sources)
    """
    # Mock other sources with slight variations
    sources = [
        {"source": "central_db", "price": value * (1 + np.random.normal(0, 0.01))},
        {"source": "news_scrape", "price": value * (1 + np.random.normal(0, 0.02))},
        {"source": "partner_feed", "price": value * (1 + np.random.normal(0, 0.03))},
    ]
    # determine if majority within 10%
    agree = sum(1 for s in sources if abs(s["price"] - value) / (value + 1e-9) < 0.1) >= 2
    return agree, sources

def validate_price(market_id: str, commodity: str, value: float, region: Optional[str] = None) -> Dict:
    """
    Runs validation checks and returns a JSON summary including quarantine flag.
    """
    window = list(_get_window(market_id, commodity, region))
    z = zscore_outlier(window, value)
    iq = iqr_outlier(window, value)
    ai = ai_anomaly_detector(window, value)
    multi_ok, sources = multi_source_verify(market_id, commodity, value)

    # decide quarantine: if at least two detectors flag or multi-source disagrees
    flags = {"zscore": z, "iqr": iq, "ai": ai, "multi_source_ok": multi_ok}
    suspect_count = sum(1 for k, v in flags.items() if (k == "multi_source_ok" and not v) or (k != "multi_source_ok" and v))
    quarantined = suspect_count >= 2

    # update window if not quarantined (or optionally add even quarantined to maintain history)
    if not quarantined:
        _get_window(market_id, commodity, region).append(value)
    else:
        logger.warning("Quarantined price for %s/%s value=%s flags=%s", market_id, commodity, value, flags)

    return {
        "market_id": market_id,
        "commodity": commodity,
        "value": value,
        "region": region,
        "flags": flags,
        "quarantined": quarantined,
        "sources": sources,
    }