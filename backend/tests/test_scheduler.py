"""TC-001-08..09 (isolation, registration) and TC-008-04..05 (run recording)."""

import logging
from datetime import UTC, datetime, timedelta

from app.config import get_config
from app.scheduler import create_scheduler, run_job


class FakeRecorder:
    """Stands in for app.runs.record_run so tests never touch the database."""

    def __init__(self, fail: bool = False):
        self.calls: list[tuple] = []
        self.fail = fail

    async def __call__(self, job, started_at, finished_at, ok, result, error):
        if self.fail:
            raise RuntimeError("database is down")
        self.calls.append((job, started_at, finished_at, ok, result, error))


async def test_run_job_isolates_failures(caplog):
    async def boom():
        raise RuntimeError("source is down")

    async def ok():
        return 42

    with caplog.at_level(logging.INFO, logger="app.scheduler"):
        assert await run_job("broken", boom, recorder=FakeRecorder()) is None
        assert await run_job("healthy", ok, recorder=FakeRecorder()) == 42
    assert "Job broken failed" in caplog.text
    assert "source is down" in caplog.text
    assert "Job healthy finished" in caplog.text


async def test_run_job_records_success():
    recorder = FakeRecorder()

    async def ok():
        return 62

    await run_job("github_trending", ok, recorder=recorder)
    [(job, started, finished, ok_, result, error)] = recorder.calls
    assert (job, ok_, result, error) == ("github_trending", True, 62, None)
    assert started <= finished


async def test_run_job_records_failure():
    recorder = FakeRecorder()

    async def boom():
        raise ValueError("bad page")

    await run_job("github_api", boom, recorder=recorder)
    [(job, _, _, ok_, result, error)] = recorder.calls
    assert (job, ok_, result) == ("github_api", False, None)
    assert error == "ValueError: bad page"


async def test_recorder_failure_does_not_break_job(caplog):
    async def ok():
        return 7

    with caplog.at_level(logging.ERROR, logger="app.scheduler"):
        assert await run_job("github_api", ok, recorder=FakeRecorder(fail=True)) == 7
    assert "Recording run of job github_api failed" in caplog.text


def test_jobs_registered():
    cfg = get_config().sources
    now = datetime(2026, 10, 10, 8, 0, tzinfo=UTC)
    jobs = {job.id: job for job in create_scheduler(now=now).get_jobs()}

    assert set(jobs) == {"github_trending", "github_api", "hacker_news", "prune"}
    expected = {
        "github_trending": (timedelta(hours=cfg.github_trending.every_hours), 60),
        "github_api": (timedelta(hours=cfg.github_api.every_hours), 120),
        "hacker_news": (timedelta(hours=cfg.hacker_news.every_hours), 90),
        "prune": (timedelta(days=7), 300),
    }
    for name, (interval, first_run_s) in expected.items():
        assert jobs[name].trigger.interval == interval, name
        assert jobs[name].next_run_time == now + timedelta(seconds=first_run_s), name
        assert jobs[name].max_instances == 1 and jobs[name].coalesce, name
