"""TC-006-01..02: weekly ranking, week start, due check."""

from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from app.leaderboard import leaderboard_due, rank_weekly, week_start
from app.momentum import Snapshot
from app.repo_stats import RepoRow

NOW = datetime(2026, 10, 19, 1, 0, tzinfo=UTC)  # a Monday morning in UTC+7


def row(i: int, topics: list[str] | None = None) -> RepoRow:
    return RepoRow(
        id=i, full_name=f"o/r{i}", url=f"https://github.com/o/r{i}", description=f"repo {i}",
        language=None, topics=[], license=None, stars=None, stars_per_day=None, snapshots=0,
        first_seen=NOW, last_seen=NOW, matched_topics=topics or [],
    )  # fmt: skip


def snaps(*points: tuple[float, int]) -> list[Snapshot]:
    """(days before NOW, stars)"""
    return [Snapshot(NOW - timedelta(days=d), stars) for d, stars in points]


def test_rank_by_stars_gained_over_7_days():
    rows = [row(1), row(2, ["agents"]), row(3)]
    data = {
        1: snaps((7.5, 1000), (3, 1500), (0, 1900)),  # base = 7.5 d ago -> +900
        2: snaps((8, 50), (0, 2050)),  # +2000
        3: snaps((7.2, 10), (0, 110)),  # +100
    }
    top = rank_weekly(rows, data, NOW, size=10)
    assert [(e["rank"], e["item_id"], e["stars_gained"]) for e in top] == [
        (1, 2, 2000),
        (2, 1, 900),
        (3, 3, 100),
    ]
    assert top[0]["matched_topics"] == ["agents"] and top[0]["stars"] == 2050
    assert all(e["since"] is None for e in top)


def test_rank_newer_repo_counts_from_first_snapshot():
    rows = [row(1)]
    data = {1: snaps((3, 400), (0, 1000))}  # first seen 3 days ago
    [entry] = rank_weekly(rows, data, NOW, size=10)
    assert entry["stars_gained"] == 600
    assert entry["since"] == (NOW - timedelta(days=3)).date().isoformat()


def test_rank_skips_single_snapshot_and_limits_size():
    rows = [row(i) for i in range(1, 15)] + [row(99)]
    data = {i: snaps((8, 0), (0, i * 10)) for i in range(1, 15)}
    data[99] = snaps((0, 5000))  # only one snapshot -> skipped
    top = rank_weekly(rows, data, NOW, size=10)
    assert len(top) == 10 and 99 not in [e["item_id"] for e in top]
    assert top[0]["item_id"] == 14 and top[-1]["item_id"] == 5


def test_week_start_and_due():
    tz = ZoneInfo("Asia/Ho_Chi_Minh")
    monday_early = datetime(2026, 10, 19, 7, 0, tzinfo=tz)
    monday_late = datetime(2026, 10, 19, 7, 35, tzinfo=tz)
    wednesday = datetime(2026, 10, 21, 3, 0, tzinfo=tz)
    sunday = datetime(2026, 10, 25, 23, 0, tzinfo=tz)
    assert (
        week_start(monday_early)
        == week_start(wednesday)
        == week_start(sunday)
        == monday_early.date()
    )
    assert not leaderboard_due(monday_early, "07:35")
    assert leaderboard_due(monday_late, "07:35")
    assert leaderboard_due(wednesday, "07:35") and leaderboard_due(sunday, "07:35")
