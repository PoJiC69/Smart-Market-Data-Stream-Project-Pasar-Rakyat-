"""
Map dashboard routes - serves static UI and WebSocket for heatmap updates.
"""
from __future__ import annotations

from fastapi import APIRouter, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

router = APIRouter()
# Mount static folder for this module (fastapi app already mounts /static elsewhere)
static_dir = Path(__file__).parent / "static"
router.mount("/static", StaticFiles(directory=str(static_dir)), name="map_static")

@router.get("/", response_class=HTMLResponse)
async def map_index():
    html_path = static_dir / "index.html"
    return HTMLResponse(html_path.read_text())