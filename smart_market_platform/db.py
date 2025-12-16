from __future__ import annotations

import os
from typing import AsyncGenerator

from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Load DATABASE_URL from environment (fallback to sqlite async file DB)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./sm_platform.db")

# Create async engine and session factory
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db() -> None:
    """
    Initialise database schema (create tables).
    Call this at startup (e.g. in FastAPI startup event).
    """
    async with engine.begin() as conn:
        # Run the SQLModel metadata.create_all() in the sync context of the async engine
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async generator dependency for FastAPI routes.
    Usage:
        async def endpoint(session: AsyncSession = Depends(get_session)):
            ...
    """
    async with async_session_factory() as session:
        yield session