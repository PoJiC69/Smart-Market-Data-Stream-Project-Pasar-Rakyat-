"""
Simple sentiment analyzer using rule-based and lightweight heuristics.
Provides correlation with price movement (mock).
"""
from __future__ import annotations

from typing import Tuple, List
import re

def simple_sentiment(text: str) -> Tuple[str, float]:
    """
    Returns label and score (-1..1)
    """
    txt = text.lower()
    # naive rule-based
    positive_words = ["baik", "murah", "bagus", "stabil", "lebih murah"]
    negative_words = ["mahal", "langka", "rusak", "buruk", "naik", "penyakit"]
    score = 0
    for w in positive_words:
        if w in txt:
            score += 1
    for w in negative_words:
        if w in txt:
            score -= 1
    label = "neutral"
    if score > 0:
        label = "positive"
    elif score < 0:
        label = "negative"
    # normalize
    norm = max(-1, min(1, score / 3))
    return label, norm

def collect_mock_social(commodity: str, region: str, count: int = 20) -> List[dict]:
    samples = []
    for i in range(count):
        txt = "harga {} di {} {}".format(commodity, region, "naik" if i%3==0 else "stabil")
        label, score = simple_sentiment(txt)
        samples.append({"text": txt, "label": label, "score": score})
    return samples