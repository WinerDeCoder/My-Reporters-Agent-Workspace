"""Background jobs. Each job is isolated: one failing never stops another (REQ-COL-005).

Collectors run once a day at their `run_at` time (Q-014): Hacker News 07:00, GitHub Trending
07:10, star snapshots 07:20 (after the others, so new candidates get a snapshot). The prune
runs weekly. On startup, a job is caught up only if its last successful run is too old.
"""

import logging
import time
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.collectors.github_api import collect_github
from app.collectors.github_trending import collect_trending
from app.collectors.hacker_news import collect_hacker_news
from app.collectors.prune import prune_old_data
from app.config import AppConfig, get_config
from app.runs import Recorder, last_successes, record_run

log = logging.getLogger(__name__)

JOBS = {
    "hacker_news": collect_hacker_news,
    "github_trending": collect_trending,
    "github_api": collect_github,
    "prune": prune_old_data,
}

# Startup catch-up order: HN and Trending add candidates before the snapshot job runs.
CATCH_UP_DELAY = {
    "hacker_news": timedelta(seconds=60),
    "github_trending": timedelta(seconds=90),
    "github_api": timedelta(seconds=150),
    "prune": timedelta(minutes=5),
}

PRUNE_AT = {"day_of_week": "mon", "hour": 7, "minute": 40}  # after Monday's collection


@dataclass(frozen=True)
class JobSpec:
    trigger: CronTrigger
    max_age: timedelta  # catch up on startup if the last success is older than this
    misfire_grace: timedelta  # still run a missed slot this late (e.g. laptop was asleep)


def job_specs(cfg: AppConfig, tz: ZoneInfo) -> dict[str, JobSpec]:
    def daily(run_at: str) -> CronTrigger:
        hour, minute = run_at.split(":")
        return CronTrigger(hour=int(hour), minute=int(minute), timezone=tz)

    src = cfg.sources
    stale = timedelta(hours=src.catch_up_after_hours)
    grace = timedelta(hours=12)
    return {
        "hacker_news": JobSpec(daily(src.hacker_news.run_at), stale, grace),
        "github_trending": JobSpec(daily(src.github_trending.run_at), stale, grace),
        "github_api": JobSpec(daily(src.github_api.run_at), stale, grace),
        "prune": JobSpec(
            CronTrigger(**PRUNE_AT, timezone=tz), timedelta(days=7), timedelta(days=3)
        ),
    }


def jobs_to_catch_up(
    max_age: Mapping[str, timedelta], last_success: Mapping[str, datetime], now: datetime
) -> list[str]:
    """Jobs never run successfully, or whose last success is older than their max age."""
    return [
        name
        for name, age in max_age.items()
        if (last := last_success.get(name)) is None or now - last > age
    ]


async def run_job(
    name: str, fn: Callable[[], Awaitable[Any]], recorder: Recorder = record_run
) -> Any:
    """Run one job, log and record it (REQ-COL-007), and never let an exception escape."""
    started_at = datetime.now(UTC)
    start = time.monotonic()
    log.info("Job %s started", name)
    result: Any = None
    error: str | None = None
    try:
        result = await fn()
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        log.exception("Job %s failed after %.1fs", name, time.monotonic() - start)
    else:
        log.info("Job %s finished in %.1fs (result: %s)", name, time.monotonic() - start, result)

    count = result if isinstance(result, int) and not isinstance(result, bool) else None
    try:
        await recorder(name, started_at, datetime.now(UTC), error is None, count, error)
    except Exception:
        log.exception("Recording run of job %s failed", name)
    return result


def create_scheduler() -> AsyncIOScheduler:
    """Daily (and weekly) jobs at fixed times. Call `schedule_catch_up` after starting it."""
    cfg = get_config()
    tz = ZoneInfo(cfg.timezone)
    scheduler = AsyncIOScheduler(timezone=tz)
    for name, spec in job_specs(cfg, tz).items():
        scheduler.add_job(
            run_job,
            spec.trigger,
            args=[name, JOBS[name]],
            id=name,
            max_instances=1,
            coalesce=True,
            misfire_grace_time=int(spec.misfire_grace.total_seconds()),
        )
    # Later specs add: daily brief (+ catch-up), weekly leaderboard.
    return scheduler


async def schedule_catch_up(
    scheduler: AsyncIOScheduler,
    now: datetime | None = None,
    load_last_success: Callable[[], Awaitable[Mapping[str, datetime]]] = last_successes,
) -> list[str]:
    """One-off runs at startup for jobs whose last success is too old (Q-014)."""
    cfg = get_config()
    tz = ZoneInfo(cfg.timezone)
    now = now or datetime.now(tz)
    try:
        last = await load_last_success()
    except Exception:
        log.exception("Could not read last runs; skipping startup catch-up")
        return []
    max_age = {name: spec.max_age for name, spec in job_specs(cfg, tz).items()}
    due = jobs_to_catch_up(max_age, last, now)
    for name in due:
        scheduler.add_job(
            run_job,
            "date",
            run_date=now + CATCH_UP_DELAY[name],
            args=[name, JOBS[name]],
            id=f"{name}:catch_up",
            replace_existing=True,
        )
    log.info("Startup catch-up: %s", ", ".join(due) or "nothing due")
    return due
