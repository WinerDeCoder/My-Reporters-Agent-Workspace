from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.news_feed import load_news_rows

router = APIRouter(tags=["news"])


class NewsOut(BaseModel):
    id: int
    hn_id: int
    title: str
    url: str | None  # null for Ask HN / text posts
    domain: str | None
    hn_url: str
    points: int
    comments: int
    posted_at: datetime
    points_per_hour: float
    linked_repo: str | None  # owner/repo when the story links a GitHub repo
    matched_topics: list[str]  # interest topics matched (spec 003)
    ai_dev: bool  # eligible for the brief's news section (Q-016)
    score: float | None  # points/hour x topic boost x penalties; null when not AI/dev
    has_card: bool  # spec 004


@router.get("/news")
async def list_news(
    session: Annotated[AsyncSession, Depends(get_session)],
    days: Annotated[int, Query(ge=1, le=30)] = 7,
) -> list[NewsOut]:
    """HN stories posted in the last `days` days, "For you" order (score, then points/hour)."""
    rows = await load_news_rows(session, days)
    return [NewsOut.model_validate(row, from_attributes=True) for row in rows]
