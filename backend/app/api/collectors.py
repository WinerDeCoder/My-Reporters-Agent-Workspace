from datetime import datetime

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.runs import last_runs
from app.scheduler import JOBS

router = APIRouter(tags=["collectors"])


class LastRun(BaseModel):
    started_at: datetime
    finished_at: datetime
    ok: bool
    result: int | None
    error: str | None


class CollectorStatus(BaseModel):
    job: str
    last_run: LastRun | None
    next_run: datetime | None  # null when the scheduler isn't running


@router.get("/collectors/status")
async def collectors_status(request: Request) -> list[CollectorStatus]:
    runs = await last_runs()
    scheduler = getattr(request.app.state, "scheduler", None)
    out = []
    for job in JOBS:
        run = runs.get(job)
        # earliest of the daily slot and a pending startup catch-up run
        upcoming = [
            j.next_run_time
            for j in (
                (scheduler.get_job(job), scheduler.get_job(f"{job}:catch_up")) if scheduler else ()
            )
            if j is not None and j.next_run_time is not None
        ]
        out.append(
            CollectorStatus(
                job=job,
                last_run=LastRun.model_validate(run, from_attributes=True) if run else None,
                next_run=min(upcoming) if upcoming else None,
            )
        )
    return out
