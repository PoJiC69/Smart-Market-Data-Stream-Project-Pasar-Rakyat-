"""
Local persistence for queued payloads using SQLite.
Provides simple enqueue/dequeue semantics for reliability when network is down.
"""
from __future__ import annotations

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any

from .config import settings

DB_PATH = Path(settings.QUEUE_DB)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT,
                payload TEXT
            )
            """
        )
        conn.commit()
    finally:
        conn.close()

def enqueue(payload: Dict[str, Any]) -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO queue (created_at, payload) VALUES (datetime('now'), ?)", (json.dumps(payload, ensure_ascii=False),))
        conn.commit()
    finally:
        conn.close()

def get_all() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, payload FROM queue ORDER BY id ASC")
        rows = cur.fetchall()
        out: List[Dict[str, Any]] = []
        for row in rows:
            out.append({"id": row[0], "payload": json.loads(row[1])})
        return out
    finally:
        conn.close()

def delete(id_: int) -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM queue WHERE id=?", (id_,))
        conn.commit()
    finally:
        conn.close()