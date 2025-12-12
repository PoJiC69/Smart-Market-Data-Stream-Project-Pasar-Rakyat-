"""
Routes for alerts including websocket push for dashboards.
"""
from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
from .manager import AlertsManager

router = APIRouter()
alerts_mgr = AlertsManager.get_instance()

@router.post("/trigger")
async def trigger_alert(payload: dict):
    await alerts_mgr.push_alert(payload)
    return {"status": "ok"}

@router.websocket("/ws/alerts")
async def alerts_ws(websocket: WebSocket):
    await websocket.accept()
    await alerts_mgr.register_ws(websocket)
    try:
        while True:
            try:
                await websocket.receive_text()  # keep alive or receive commands
            except WebSocketDisconnect:
                break
    finally:
        await alerts_mgr.unregister_ws(websocket)