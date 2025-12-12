"""
Blockchain routes for adding entries and integrity checking.
"""
from __future__ import annotations

from fastapi import APIRouter
from .ledger import ledger

router = APIRouter()

@router.post("/append")
async def append_entry(payload: dict):
    block = ledger.add_entry(payload)
    return {"index": block.index, "hash": block.hash}

@router.get("/integrity/check")
async def integrity_check():
    return ledger.verify()