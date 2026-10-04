"""Background jobs. Collectors and the daily brief get registered here as they are built."""

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import get_config

log = logging.getLogger(__name__)


def create_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=get_config().timezone)
    # Jobs added in later build steps:
    #   github_trending / github_api every N hours, hacker_news hourly,
    #   daily brief at brief_time (+ catch-up on startup), weekly leaderboard.
    return scheduler
