"""Stats endpoint for the 2-week trial (spec 007)."""

from datetime import timedelta
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.brief import local_now
from app.config import get_config
from app.db import get_session
from app.stats import day_rows, summarize

router = APIRouter(tags=["stats"])


@router.get("/stats")
async def stats(
    session: Annotated[AsyncSession, Depends(get_session)],
    view: Annotated[Literal["trial", "rolling"], Query()] = "trial",
) -> dict[str, Any]:
    """`trial`: the fixed trial window from config (Q-029), with checks and verdict.
    `rolling`: the last 14 days, same numbers, no verdict."""
    cfg = get_config()
    today = local_now(cfg).date()
    if view == "trial":
        rows = await day_rows(session, cfg.trial.start_date, cfg.trial.days)
        out = summarize(rows, today, cfg.trial)
    else:
        rows = await day_rows(session, today - timedelta(days=13), 14)
        out = summarize(rows, today, cfg.trial, finished_matters=False)
    return {"view": view, **out}
