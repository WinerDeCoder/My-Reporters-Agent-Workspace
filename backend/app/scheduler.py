"""Background jobs. Each job is isolated: one failing never stops another (REQ-COL-005)."""

import logging
import time
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.collectors.github_api import collect_github
from app.collectors.github_trending import collect_trending
from app.config import get_config

log = logging.getLogger(__name__)

# First runs shortly after startup (Q-003); the API job waits for Trending to add candidates.
TRENDING_FIRST_RUN = timedelta(seconds=60)
GITHUB_API_FIRST_RUN = timedelta(seconds=120)


async def run_job(name: str, fn: Callable[[], Awaitable[Any]]) -> Any:
    """Run one job, log its duration and result, and never let an exception escape."""
    start = time.monotonic()
    log.info("Job %s started", name)
    try:
        result = await fn()
    except Exception:
        log.exception("Job %s failed after %.1fs", name, time.monotonic() - start)
        return None
    log.info("Job %s finished in %.1fs (result: %s)", name, time.monotonic() - start, result)
    return result


def create_scheduler(now: datetime | None = None) -> AsyncIOScheduler:
    cfg = get_config()
    tz = ZoneInfo(cfg.timezone)
    now = now or datetime.now(tz)
    scheduler = AsyncIOScheduler(timezone=tz)
    common: dict[str, Any] = {"max_instances": 1, "coalesce": True, "misfire_grace_time": 3600}

    scheduler.add_job(
        run_job,
        "interval",
        hours=cfg.sources.github_trending.every_hours,
        args=["github_trending", collect_trending],
        id="github_trending",
        next_run_time=now + TRENDING_FIRST_RUN,
        **common,
    )
    scheduler.add_job(
        run_job,
        "interval",
        hours=cfg.sources.github_api.every_hours,
        args=["github_api", collect_github],
        id="github_api",
        next_run_time=now + GITHUB_API_FIRST_RUN,
        **common,
    )
    # Later specs add: hacker_news hourly, daily brief at brief_time (+ catch-up), leaderboard.
    return scheduler
