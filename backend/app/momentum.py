"""Star momentum from snapshots. Pure functions: no DB, no clock."""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Snapshot:
    taken_at: datetime
    stars: int


def _hours(a: datetime, b: datetime) -> float:
    return (b - a).total_seconds() / 3600


def stars_per_day(
    snapshots: Iterable[Snapshot], target_hours: float = 24.0, min_span_hours: float = 6.0
) -> float | None:
    """Stars gained per day between the latest snapshot and the one closest to
    `target_hours` before it. Uses real time gaps, so missed runs (laptop asleep)
    don't distort the rate. None if there's less than `min_span_hours` of history."""
    snaps = sorted(snapshots, key=lambda s: s.taken_at)
    if len(snaps) < 2:
        return None
    latest = snaps[-1]
    candidates = [s for s in snaps[:-1] if _hours(s.taken_at, latest.taken_at) >= min_span_hours]
    if not candidates:
        return None
    base = min(candidates, key=lambda s: abs(_hours(s.taken_at, latest.taken_at) - target_hours))
    return (latest.stars - base.stars) / _hours(base.taken_at, latest.taken_at) * 24


def stars_gained(snapshots: Iterable[Snapshot], since: datetime) -> int | None:
    """Stars gained from `since` to the latest snapshot. If the repo was first
    snapshotted after `since`, counts from its first snapshot. None with < 2 snapshots."""
    snaps = sorted(snapshots, key=lambda s: s.taken_at)
    if len(snaps) < 2:
        return None
    before = [s for s in snaps if s.taken_at <= since]
    base = before[-1] if before else snaps[0]
    return snaps[-1].stars - base.stars
