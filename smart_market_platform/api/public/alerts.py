"""
Expose the latest alerts to public consumers.
"""
from __future__ import annotations

from typing import List
from fastapi import APIRouter
from ...alerts.manager import AlertsManager

router = APIRouter()
alerts_mgr = AlertsManager.get_instance()

@router.get("/alerts/live")
async def alerts_live():
    return await alerts_mgr.get_recent_alerts()