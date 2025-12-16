"""
Entry point for the Smart Market Platform FastAPI application.

Changes:
- Uses a lifespan async context manager instead of @app.on_event for startup/shutdown.
- When executed as a script (python -m smart_market_platform.main) it calls
  uvicorn.run() with an import string ("smart_market_platform.main:app")
  so reload/workers work without warnings.
"""
from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
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

# ingest router (optional)
try:
    from .ingest.routes import router as ingest_router
except Exception:
    ingest_router = None

# configure root logger for the app
logging.basicConfig(level=logging.DEBUG if settings.DEBUG else logging.INFO)
logger = logging.getLogger("smart_market_platform")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan handler: start background tasks on startup and perform cleanup on shutdown.
    Use this instead of @app.on_event to avoid deprecation warnings.
    """
    logger.info("Starting Smart Market Platform (lifespan startup)")
    # Start optional background alert worker if available
    try:
        # import inside try so missing module won't break startup
        from .alerts.manager import start_alert_worker
    except Exception:
        start_alert_worker = None

    if start_alert_worker is not None:
        # start worker as background task (non-blocking)
        try:
            asyncio.create_task(start_alert_worker())
            logger.debug("Alert worker scheduled")
        except Exception as exc:
            logger.exception("Failed to schedule alert worker: %s", exc)
    else:
        logger.debug("No alert worker module available; skipping")

    yield  # application runs here

    # Shutdown / cleanup
    logger.info("Smart Market Platform shutting down (lifespan shutdown)")


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

# Allow CORS for development. Lock down in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (guard includes if module import failed)
app.include_router(public_router, prefix="/api/public", tags=["public"])
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(validation_router, prefix="/api/validation", tags=["validation"])
app.include_router(forecast_router, prefix="/api/forecast", tags=["forecast"])
app.include_router(supply_router, prefix="/api/supply", tags=["supply_chain"])
app.include_router(alerts_router, prefix="/api/alerts", tags=["alerts"])
app.include_router(blockchain_router, prefix="/api/blockchain", tags=["blockchain"])
app.include_router(map_router, prefix="/dashboard/map", tags=["dashboard.map"])

if ingest_router is not None:
    app.include_router(ingest_router)
else:
    logger.debug("ingest router not available; /ingest endpoint will not be mounted")


# Allow uvicorn reload/workers when invoked via python -m by passing an import string.
if __name__ == "__main__":
    import uvicorn

    import_str = "smart_market_platform.main:app"
    uvicorn.run(import_str, host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)