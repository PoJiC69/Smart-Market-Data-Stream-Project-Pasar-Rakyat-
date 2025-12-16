# helper snippet to mount static frontend for dashboard (drop into main.py)
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Option A: serve static files from backend package static/ directory
STATIC_DASHBOARD_DIR = HERE / "static" / "dashboard"  # smart_market_platform/static/dashboard

# Option B: alternatively point to a frontend build directory:
# STATIC_DASHBOARD_DIR = Path(__file__).resolve().parent.parent / "frontend" / "build"

# Mount static files (serves /dashboard/* as files if they exist)
if STATIC_DASHBOARD_DIR.exists():
    app.mount("/dashboard/static", StaticFiles(directory=str(STATIC_DASHBOARD_DIR)), name="dashboard_static")

    # Serve index.html for /dashboard and any sub-paths (SPA fallback)
    @app.get("/dashboard", include_in_schema=False)
    async def dashboard_index():
        index = STATIC_DASHBOARD_DIR / "index.html"
        return FileResponse(index)

    @app.get("/dashboard/{full_path:path}", include_in_schema=False)
    async def dashboard_spa(full_path: str):
        # if an asset exists, serve it; otherwise return index.html so SPA router can handle route
        candidate = STATIC_DASHBOARD_DIR / full_path
        if candidate.exists() and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(STATIC_DASHBOARD_DIR / "index.html")
else:
    logger.debug("Static dashboard directory %s not found — /dashboard will return 404", STATIC_DASHBOARD_DIR)