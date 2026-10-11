"""Daily brief and feedback endpoints (spec 005)."""

from datetime import date, datetime
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.brief import (
    NotInBrief,
    build_daily_brief,
    enrich_items,
    latest_daily_brief,
    mark_opened,
    set_rating,
)
from app.config import get_config
from app.db import get_session

router = APIRouter(tags=["brief"])


class BriefItemOut(BaseModel):
    section: Literal["top", "repos", "news"]
    item_type: Literal["repo", "news"]
    item_id: int
    title: str
    url: str | None = None
    hn_url: str | None = None
    domain: str | None = None
    description: str | None = None
    language: str | None = None
    stars: int | None = None
    stars_per_day: float | None = None
    points: int | None = None
    comments: int | None = None
    points_per_hour: float | None = None
    linked_repo: str | None = None
    matched_topics: list[str] = []
    score: float | None = None
    what_it_is: str | None = None  # from the item's latest card, read live
    has_card: bool = False
    rating: int | None = None  # 1 / -1 / null for this brief


class BriefOut(BaseModel):
    id: int
    date: date
    created_at: datetime
    opened_at: datetime | None
    items: list[BriefItemOut]


class TodayOut(BaseModel):
    brief: BriefOut | None  # latest daily brief, null if none was ever built
    brief_time: str  # when the scheduled brief is built (config)


class FeedbackIn(BaseModel):
    brief_id: int
    item_type: Literal["repo", "news"]
    item_id: int
    rating: int = Field(ge=-1, le=1, description="1 = 👍, -1 = 👎, 0 = clear")


class FeedbackOut(BaseModel):
    rating: int | None


async def _today(session: AsyncSession) -> TodayOut:
    brief = await latest_daily_brief(session)
    if brief is None:
        return TodayOut(brief=None, brief_time=get_config().brief_time)
    await mark_opened(session, brief)
    items: list[dict[str, Any]] = await enrich_items(session, brief)
    return TodayOut(
        brief=BriefOut(
            id=brief.id,
            date=brief.date,
            created_at=brief.created_at,
            opened_at=brief.opened_at,
            items=[BriefItemOut(**it) for it in items],
        ),
        brief_time=get_config().brief_time,
    )


@router.get("/briefs/today")
async def today(session: Annotated[AsyncSession, Depends(get_session)]) -> TodayOut:
    """The latest daily brief; the first view sets `opened_at` (REQ-BRF-004)."""
    return await _today(session)


@router.post("/briefs/today/build")
async def build_today(session: Annotated[AsyncSession, Depends(get_session)]) -> TodayOut:
    """Build today's brief now, even before brief_time (no-op if it already exists)."""
    await build_daily_brief(force=True)
    return await _today(session)


@router.post("/feedback")
async def feedback(
    body: FeedbackIn, session: Annotated[AsyncSession, Depends(get_session)]
) -> FeedbackOut:
    """Save, switch or clear a 👍/👎 on a brief item (REQ-FBK-001)."""
    try:
        rating = await set_rating(session, body.brief_id, body.item_type, body.item_id, body.rating)
    except NotInBrief as exc:
        raise HTTPException(404, str(exc)) from exc
    return FeedbackOut(rating=rating)
