"""TC-008-01..02: repo rows for the Rising repos page."""

from datetime import UTC, datetime, timedelta

import pytest

from app.models import Repo
from app.momentum import Snapshot
from app.repo_stats import build_repo_rows, rank_by_momentum

T0 = datetime(2026, 10, 10, 0, 0, tzinfo=UTC)


def repo(id_: int, name: str, **kw) -> Repo:
    return Repo(
        id=id_, full_name=name, topics=kw.pop("topics", []), first_seen=T0, last_seen=T0, **kw
    )


def snap(hours: float, stars: int) -> Snapshot:
    return Snapshot(T0 + timedelta(hours=hours), stars)


def test_build_repo_rows():
    repos = [
        repo(1, "a/fast", description="Fast one", language="Python", topics=["agents"]),
        repo(2, "b/new"),
        repo(3, "c/never-snapshotted"),
    ]
    snaps = [(1, snap(0, 1000)), (1, snap(24, 1240)), (2, snap(0, 50)), (2, snap(2, 60))]
    rows = {r.full_name: r for r in build_repo_rows(repos, snaps)}

    fast = rows["a/fast"]
    assert fast.url == "https://github.com/a/fast"
    assert (fast.stars, fast.snapshots) == (1240, 2)
    assert fast.stars_per_day == pytest.approx(240)
    assert (fast.description, fast.language, fast.topics) == ("Fast one", "Python", ["agents"])

    assert rows["b/new"].stars == 60
    assert rows["b/new"].stars_per_day is None  # only 2 h of history

    never = rows["c/never-snapshotted"]
    assert (never.stars, never.stars_per_day, never.snapshots) == (None, None, 0)


def test_rank_by_momentum():
    repos = [
        repo(1, "slow"),
        repo(2, "fast"),
        repo(3, "collecting-big"),
        repo(4, "collecting-small"),
    ]
    snaps = [
        (1, snap(0, 100)), (1, snap(24, 110)),
        (2, snap(0, 100)), (2, snap(24, 400)),
        (3, snap(0, 9000)),
        (4, snap(0, 10)),
    ]  # fmt: skip
    ranked = [r.full_name for r in rank_by_momentum(build_repo_rows(repos, snaps))]
    assert ranked == ["fast", "slow", "collecting-big", "collecting-small"]
