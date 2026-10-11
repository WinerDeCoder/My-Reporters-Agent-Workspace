"""Weekly leaderboard endpoints (spec 006)."""

from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.cards import latest_card
from app.config import get_config
from app.db import get_session
from app.leaderboard import build_weekly_leaderboard, latest_leaderboard

router = APIRouter(tags=["leaderboard"])


class LeaderboardEntry(BaseModel):
    rank: int
    item_type: str = "repo"
    item_id: int
    title: str
    url: str | None = None
    description: str | None = None
    language: str | None = None
    stars: int
    stars_gained: int
    since: date | None = None  # set when tracked for less than the 7-day window
    matched_topics: list[str] = []
    what_it_is: str | None = None  # from the repo's latest card
    has_card: bool = False


class LeaderboardOut(BaseModel):
    week_of: date  # Monday
    created_at: datetime
    entries: list[LeaderboardEntry]


class LatestOut(BaseModel):
    leaderboard: LeaderboardOut | None
    run_at: str  # Mondays at this time


async def _latest(session: AsyncSession) -> LatestOut:
    run_at = get_config().leaderboard.run_at
    lb = await latest_leaderboard(session)
    if lb is None:
        return LatestOut(leaderboard=None, run_at=run_at)
    entries = []
    for e in lb.items or []:
        card = await latest_card(session, "repo", e["item_id"])
        entries.append(
            LeaderboardEntry(
                **{k: v for k, v in e.items() if k in LeaderboardEntry.model_fields},
                what_it_is=card.content.get("what_it_is") if card else None,
                has_card=card is not None,
            )
        )
    return LatestOut(
        leaderboard=LeaderboardOut(week_of=lb.date, created_at=lb.created_at, entries=entries),
        run_at=run_at,
    )


@router.get("/leaderboard/latest")
async def latest(session: Annotated[AsyncSession, Depends(get_session)]) -> LatestOut:
    return await _latest(session)


@router.post("/leaderboard/build")
async def build(session: Annotated[AsyncSession, Depends(get_session)]) -> LatestOut:
    """Build this week's leaderboard now (no-op if it exists)."""
    await build_weekly_leaderboard(force=True)
    return await _latest(session)
