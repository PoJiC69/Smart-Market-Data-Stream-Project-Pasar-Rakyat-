from fastapi import APIRouter

router = APIRouter()
from . import commodity, devices, impact, alerts  # noqa: F401