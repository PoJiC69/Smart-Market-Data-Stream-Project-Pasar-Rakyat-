"""
Training utilities for forecast models (placeholder).
Implements simple save/load of model artifacts for Prophet/SARIMAX/LSTM when available.
"""
from __future__ import annotations

import os
import pandas as pd
import numpy as np

MODEL_DIR = "./models"
os.makedirs(MODEL_DIR, exist_ok=True)

def train_dummy_model(commodity: str):
    # Train a trivial model and save a small artifact
    series = pd.Series(10000 + np.cumsum(np.random.normal(0, 100, 365)))
    avg = float(series.mean())
    path = os.path.join(MODEL_DIR, f"{commodity}.meta")
    with open(path, "w") as fh:
        fh.write(str({"avg": avg}))
    return path