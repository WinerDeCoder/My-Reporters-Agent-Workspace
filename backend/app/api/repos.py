from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_config
from app.db import get_session
from app.repo_stats import load_repo_rows

router = APIRouter(tags=["repos"])


class RepoOut(BaseModel):
    id: int
    full_name: str
    url: str
    description: str | None
    language: str | None
    topics: list[str]
    license: str | None
    stars: int | None
    stars_per_day: float | None  # null until 6 h of snapshot history
    snapshots: int
    first_seen: datetime
    last_seen: datetime


@router.get("/repos")
async def list_repos(session: Annotated[AsyncSession, Depends(get_session)]) -> list[RepoOut]:
    """Tracked repos (last seen within track_days), highest stars/day first."""
    rows = await load_repo_rows(session, get_config().sources.github_api.track_days)
    return [RepoOut.model_validate(row, from_attributes=True) for row in rows]
