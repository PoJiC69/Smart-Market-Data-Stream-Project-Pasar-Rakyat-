from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Column, String, DateTime
from sqlalchemy import Index


class Device(SQLModel, table=True):
    """
    Device registry model.

    Field previously named 'metadata' is renamed to 'metadata_json' to avoid
    conflict with SQLAlchemy Declarative 'metadata' attribute.
    """
    __tablename__ = "device"
    __table_args__ = (
        Index("ix_device_device_id", "device_id", unique=True),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: str = Field(sa_column=Column(String, nullable=False, unique=True))
    market_id: Optional[str] = Field(default=None)
    role: Optional[str] = Field(default="operator")
    registered_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, nullable=False))
    metadata_json: Optional[str] = Field(default=None, sa_column=Column(String, nullable=True))