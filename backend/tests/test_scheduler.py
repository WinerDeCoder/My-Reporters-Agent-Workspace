"""TC-001-08..09 (isolation, registration) and TC-008-04..05 (run recording)."""

import logging
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from app.config import get_config
from app.scheduler import create_scheduler, jobs_to_catch_up, run_job, schedule_catch_up


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


TZ = ZoneInfo(get_config().timezone)


def test_jobs_registered_daily_at_run_at():
    """Q-014: HN 07:00, Trending 07:10, snapshots 07:20, cards 07:25 daily; prune Mon 07:40."""
    cfg = get_config()
    src = cfg.sources
    assert (src.hacker_news.run_at, src.github_trending.run_at, src.github_api.run_at) == (
        "07:00",
        "07:10",
        "07:20",
    )
    assert cfg.cards.run_at == "07:25"
    jobs = {job.id: job for job in create_scheduler().get_jobs()}
    assert set(jobs) == {"hacker_news", "github_trending", "github_api", "cards", "prune"}

    sunday_6am = datetime(2026, 10, 11, 6, 0, tzinfo=TZ)
    expected = {
        "hacker_news": datetime(2026, 10, 11, 7, 0, tzinfo=TZ),
        "github_trending": datetime(2026, 10, 11, 7, 10, tzinfo=TZ),
        "github_api": datetime(2026, 10, 11, 7, 20, tzinfo=TZ),
        "cards": datetime(2026, 10, 11, 7, 25, tzinfo=TZ),
        "prune": datetime(2026, 10, 12, 7, 40, tzinfo=TZ),  # next Monday
    }
    for name, first in expected.items():
        trigger = jobs[name].trigger
        assert trigger.get_next_fire_time(None, sunday_6am) == first, name
        # and again a day (or a week) later, at the same time
        step = timedelta(days=7 if name == "prune" else 1)
        assert trigger.get_next_fire_time(first, first + timedelta(minutes=1)) == first + step
        assert jobs[name].max_instances == 1 and jobs[name].coalesce, name
        assert jobs[name].misfire_grace_time >= 12 * 3600, name  # laptop asleep at 07:00


def test_jobs_to_catch_up():
    now = datetime(2026, 10, 11, 9, 0, tzinfo=UTC)
    max_age = {
        "daily": timedelta(hours=20),
        "weekly": timedelta(days=7),
        "never": timedelta(hours=20),
    }
    last = {
        "daily": now - timedelta(hours=21),  # stale -> catch up
        "weekly": now - timedelta(days=3),  # fresh -> skip
    }
    assert jobs_to_catch_up(max_age, last, now) == ["daily", "never"]
    assert jobs_to_catch_up(max_age, {**last, "daily": now - timedelta(hours=2)}, now) == ["never"]


async def test_schedule_catch_up_adds_ordered_one_off_runs():
    now = datetime(2026, 10, 11, 9, 0, tzinfo=TZ)
    scheduler = create_scheduler()

    async def last_success():
        return {
            "hacker_news": now - timedelta(hours=26),  # stale
            "github_trending": now - timedelta(hours=1),  # fresh
            "cards": now - timedelta(hours=2),  # fresh
            # github_api never ran, prune never ran
        }

    due = await schedule_catch_up(scheduler, now=now, load_last_success=last_success)
    assert due == ["hacker_news", "github_api", "prune"]
    runs = {
        job.id: job.trigger.run_date for job in scheduler.get_jobs() if job.id.endswith(":catch_up")
    }
    assert runs == {
        "hacker_news:catch_up": now + timedelta(seconds=60),
        "github_api:catch_up": now + timedelta(seconds=150),
        "prune:catch_up": now + timedelta(minutes=5),
    }


async def test_cards_catch_up_runs_after_collectors():
    now = datetime(2026, 10, 11, 9, 0, tzinfo=TZ)
    scheduler = create_scheduler()

    async def nothing_ran():
        return {}

    await schedule_catch_up(scheduler, now=now, load_last_success=nothing_ran)
    runs = {j.id: j.trigger.run_date for j in scheduler.get_jobs() if j.id.endswith(":catch_up")}
    assert runs["cards:catch_up"] > runs["github_api:catch_up"] > runs["github_trending:catch_up"]


async def test_schedule_catch_up_skips_when_db_unreadable():
    async def broken():
        raise RuntimeError("db down")

    scheduler = create_scheduler()
    assert await schedule_catch_up(scheduler, load_last_success=broken) == []
    assert not [j for j in scheduler.get_jobs() if j.id.endswith(":catch_up")]
