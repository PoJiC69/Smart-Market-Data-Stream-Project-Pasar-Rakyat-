````markdown
# Smart Market Platform - National-level Smart Market Intelligence

This repository assembles a national-level Smart Market Intelligence platform built with Python 3.11+, FastAPI, WebSocket and modular clean architecture.

It includes:
- Validation & Anti-Manipulation engine (outliers, AI stub, multi-source verification)
- Device Identity & Auth (JWT, device registration, QR onboarding)
- Supply Chain intelligence (route analyzer, stock monitoring)
- Forecast engine (naïve SARIMAX/Prophet/LSTM stubs)
- Early Warning System (alerts, mock Telegram/WhatsApp)
- Sentiment analysis (simple NLP)
- Macro-economic fusion (inflation/fuel coefficients integrated into impact engine)
- Blockchain ledger for integrity of price entries
- Dashboard map (Leaflet) and Charting modules
- Public API routers for developers

Quick start (development):
1. Create virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt