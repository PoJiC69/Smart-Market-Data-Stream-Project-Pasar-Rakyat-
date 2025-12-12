"""
Database initialization and session helpers using SQLModel.
"""
from __future__ import annotations

from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import AsyncEngine
import asyncio

from .config import settings

_async_engine: AsyncEngine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG, future=True)

async def init_db():
    # create tables
    async with _async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

def get_engine():
    return _async_engine

# Provide async session factory
from sqlalchemy.orm import sessionmaker
async_session = sessionmaker(_async_engine, class_=AsyncSession, expire_on_commit=False)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session