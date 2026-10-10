"""TC-001-08..09: job isolation and registration."""

import logging
from datetime import UTC, datetime, timedelta

from app.config import get_config
from app.scheduler import create_scheduler, run_job


async def test_run_job_isolates_failures(caplog):
    async def boom():
        raise RuntimeError("source is down")

    async def ok():
        return 42

    with caplog.at_level(logging.INFO, logger="app.scheduler"):
        assert await run_job("broken", boom) is None
        assert await run_job("healthy", ok) == 42
    assert "Job broken failed" in caplog.text
    assert "source is down" in caplog.text
    assert "Job healthy finished" in caplog.text


def test_jobs_registered():
    cfg = get_config().sources
    now = datetime(2026, 10, 10, 8, 0, tzinfo=UTC)
    jobs = {job.id: job for job in create_scheduler(now=now).get_jobs()}

    assert set(jobs) == {"github_trending", "github_api"}
    trending, api = jobs["github_trending"], jobs["github_api"]
    assert trending.trigger.interval == timedelta(hours=cfg.github_trending.every_hours)
    assert api.trigger.interval == timedelta(hours=cfg.github_api.every_hours)
    assert trending.next_run_time == now + timedelta(seconds=60)
    assert api.next_run_time == now + timedelta(seconds=120)
    assert trending.max_instances == 1 and trending.coalesce
