"""
Device and user models for authentication and registration.
Uses SQLModel for easy async persistence.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Column, String, DateTime

class Device(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    market_id: str = Field(index=True)
    device_id: str = Field(index=True, sa_column=Column(String, unique=True))
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    role: str = Field(default="operator")  # operator, admin, central
    metadata: Optional[str] = None