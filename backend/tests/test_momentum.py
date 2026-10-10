"""TC-001-04: stars/day and stars gained from snapshots."""

from datetime import UTC, datetime, timedelta

import pytest

from app.momentum import Snapshot, stars_gained, stars_per_day

T0 = datetime(2026, 10, 10, 0, 0, tzinfo=UTC)


def snaps(*points: tuple[float, int]) -> list[Snapshot]:
    """(hours after T0, stars) pairs, deliberately unsorted-safe."""
    return [Snapshot(T0 + timedelta(hours=h), stars) for h, stars in points]


def test_regular_six_hourly_snapshots():
    # +60 stars every 6 h -> 240/day
    s = snaps((0, 1000), (6, 1060), (12, 1120), (18, 1180), (24, 1240))
    assert stars_per_day(s) == pytest.approx(240)


def test_uses_snapshot_closest_to_24h_before_latest():
    s = snaps((0, 0), (20, 500), (44, 1100))  # 24 h before latest = h20
    assert stars_per_day(s) == pytest.approx(600)


def test_gap_from_sleeping_laptop_uses_real_time():
    # only two snapshots 30 h apart: rate is normalized to a day
    s = snaps((0, 100), (30, 400))
    assert stars_per_day(s) == pytest.approx(240)


def test_too_short_history_returns_none():
    assert stars_per_day(snaps((0, 100), (3, 130))) is None
    assert stars_per_day(snaps((0, 100))) is None
    assert stars_per_day([]) is None


def test_star_loss_is_negative():
    assert stars_per_day(snaps((0, 500), (24, 476))) == pytest.approx(-24)


def test_order_does_not_matter():
    assert stars_per_day(snaps((24, 1240), (0, 1000))) == pytest.approx(240)


def test_stars_gained_since_cutoff():
    s = snaps((0, 100), (24, 150), (48, 260), (168, 900))
    assert stars_gained(s, since=T0 + timedelta(hours=24)) == 750


def test_stars_gained_repo_discovered_after_cutoff():
    s = snaps((48, 260), (168, 900))
    assert stars_gained(s, since=T0) == 640


def test_stars_gained_needs_two_snapshots():
    assert stars_gained(snaps((0, 100)), since=T0) is None
