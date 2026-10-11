"""Background jobs. Each job is isolated: one failing never stops another (REQ-COL-005)."""

import logging
import time
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.collectors.github_api import collect_github
from app.collectors.github_trending import collect_trending
from app.collectors.hacker_news import collect_hacker_news
from app.collectors.prune import prune_old_data
from app.config import AppConfig, get_config
from app.runs import Recorder, record_run

log = logging.getLogger(__name__)

JOBS = {
    "github_trending": collect_trending,
    "github_api": collect_github,
    "hacker_news": collect_hacker_news,
    "prune": prune_old_data,
}

# First runs shortly after startup (Q-003): Trending, then the API job once candidates exist,
# then HN; prune last, after the morning's collection.
FIRST_RUN = {
    "github_trending": timedelta(seconds=60),
    "github_api": timedelta(seconds=120),
    "hacker_news": timedelta(seconds=90),
    "prune": timedelta(minutes=5),
}


def job_intervals(cfg: AppConfig) -> dict[str, timedelta]:
    return {
        "github_trending": timedelta(hours=cfg.sources.github_trending.every_hours),
        "github_api": timedelta(hours=cfg.sources.github_api.every_hours),
        "hacker_news": timedelta(hours=cfg.sources.hacker_news.every_hours),
        "prune": timedelta(days=7),
    }


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


def create_scheduler(now: datetime | None = None) -> AsyncIOScheduler:
    cfg = get_config()
    tz = ZoneInfo(cfg.timezone)
    now = now or datetime.now(tz)
    scheduler = AsyncIOScheduler(timezone=tz)
    common: dict[str, Any] = {"max_instances": 1, "coalesce": True, "misfire_grace_time": 3600}

    for name, interval in job_intervals(cfg).items():
        scheduler.add_job(
            run_job,
            "interval",
            seconds=interval.total_seconds(),
            args=[name, JOBS[name]],
            id=name,
            next_run_time=now + FIRST_RUN[name],
            **common,
        )
    # Later specs add: daily brief at brief_time (+ catch-up), weekly leaderboard.
    return scheduler
