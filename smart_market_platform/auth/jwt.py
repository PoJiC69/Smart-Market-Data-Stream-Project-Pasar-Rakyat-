"""
JWT utilities for issuing and validating tokens for devices and users.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, Optional

import jwt

from ..config import settings

def create_token(subject: str, role: str = "operator", expires_minutes: int = 60*24) -> str:
    payload = {
        "sub": subject,
        "role": role,
        "exp": datetime.utcnow() + timedelta(minutes=expires_minutes),
        "iat": datetime.utcnow(),
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token

def decode_token(token: str) -> Optional[Dict]:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except Exception:
        return None