"""
Authentication routes: device registration, token issuance, QR onboarding.
"""
from __future__ import annotations

import io
import qrcode
import base64
from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.responses import JSONResponse

from .models import Device
from .jwt import create_token
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..config import settings
from ..db import get_session, init_db  # db helper will be added below

router = APIRouter()

@router.on_event("startup")
async def startup():
    await init_db()

@router.post("/device/register")
async def register_device(market_id: str = Body(...), device_id: str = Body(...), role: str = Body("operator")):
    """
    Register a device and issue JWT token. Returns QR code (data URL) for onboarding.
    """
    async with get_session() as session:  # type: AsyncSession
        # check if device exists
        q = select(Device).where(Device.device_id == device_id)
        res = await session.exec(q)
        existing = res.first()
        if existing:
            raise HTTPException(status_code=400, detail="Device already registered")
        d = Device(market_id=market_id, device_id=device_id, role=role)
        session.add(d)
        await session.commit()
        token = create_token(subject=device_id, role=role)
        # Create a QR with onboarding payload
        payload = {"device_id": device_id, "market_id": market_id, "token": token}
        img = qrcode.make(str(payload))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        data = base64.b64encode(buf.getvalue()).decode()
        data_url = f"data:image/png;base64,{data}"
        return JSONResponse({"device_id": device_id, "token": token, "qr": data_url})

@router.post("/token")
async def token(device_id: str = Body(...)):
    # simple token issuance for existing device
    async with get_session() as session:
        q = select(Device).where(Device.device_id == device_id)
        res = await session.exec(q)
        dev = res.first()
        if not dev:
            raise HTTPException(status_code=404, detail="Device not found")
        token = create_token(subject=device_id, role=dev.role)
        return {"token": token}