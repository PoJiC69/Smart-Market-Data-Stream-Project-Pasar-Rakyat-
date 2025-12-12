"""
Entry point for the Smart Market Platform FastAPI application.
Includes routers for public API, auth, validation, forecasting, supply chain, alerts, blockchain, dashboard, and websocket endpoints.
"""
from __future__ import annotations

import asyncio
import logging

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .api.public import router as public_router
from .auth.routes import router as auth_router
from .validation_engine.routes import router as validation_router
from .forecast_engine.routes import router as forecast_router
from .supply_chain.routes import router as supply_router
from .alerts.routes import router as alerts_router
from .blockchain.routes import router as blockchain_router
from .dashboard.map.routes import router as map_router

# initialize logger
logging.basicConfig(level=logging.DEBUG if settings.DEBUG else logging.INFO)
logger = logging.getLogger("smart_market_platform")

app = FastAPI(title=settings.APP_NAME)

# Allow CORS for development. Lock down in production.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Include routers
app.include_router(public_router, prefix="/api/public", tags=["public"])
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(validation_router, prefix="/api/validation", tags=["validation"])
app.include_router(forecast_router, prefix="/api/forecast", tags=["forecast"])
app.include_router(supply_router, prefix="/api/supply", tags=["supply_chain"])
app.include_router(alerts_router, prefix="/api/alerts", tags=["alerts"])
app.include_router(blockchain_router, prefix="/api/blockchain", tags=["blockchain"])
app.include_router(map_router, prefix="/dashboard/map", tags=["dashboard.map"])

# Mount static assets served directly by dashboard routes (they serve their own static directory)
# Startup/shutdown events for background tasks (e.g., alert workers)
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Smart Market Platform")
    # start background tasks if necessary
    from .alerts.manager import start_alert_worker
    asyncio.create_task(start_alert_worker())

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Smart Market Platform")