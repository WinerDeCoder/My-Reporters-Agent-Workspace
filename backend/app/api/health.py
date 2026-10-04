import logging

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text

from app.db import engine

log = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


class Health(BaseModel):
    status: str
    db: bool


@router.get("/health")
async def health() -> Health:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception as exc:  # noqa: BLE001 - report any DB failure as "down"
        log.warning("DB health check failed: %s", exc)
        db_ok = False
    return Health(status="ok", db=db_ok)
