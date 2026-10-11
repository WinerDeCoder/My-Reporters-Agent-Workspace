"""Collector run log (REQ-COL-007): record each job run; never let recording break a job."""

import logging
from collections.abc import Awaitable, Callable
from datetime import datetime

from sqlalchemy import func, select

from app.db import SessionLocal
from app.models import CollectorRun

log = logging.getLogger(__name__)

Recorder = Callable[[str, datetime, datetime, bool, int | None, str | None], Awaitable[None]]


async def record_run(
    job: str,
    started_at: datetime,
    finished_at: datetime,
    ok: bool,
    result: int | None,
    error: str | None,
) -> None:
    try:
        async with SessionLocal() as session:
            session.add(
                CollectorRun(
                    job=job,
                    started_at=started_at,
                    finished_at=finished_at,
                    ok=ok,
                    result=result,
                    error=error[:2000] if error else None,
                )
            )
            await session.commit()
    except Exception:
        log.exception("Could not record run of job %s", job)


async def last_runs() -> dict[str, CollectorRun]:
    """Latest run per job."""
    async with SessionLocal() as session:
        latest = (
            select(CollectorRun.job, func.max(CollectorRun.started_at).label("started_at"))
            .group_by(CollectorRun.job)
            .subquery()
        )
        rows = await session.scalars(
            select(CollectorRun).join(
                latest,
                (CollectorRun.job == latest.c.job)
                & (CollectorRun.started_at == latest.c.started_at),
            )
        )
        return {run.job: run for run in rows}
