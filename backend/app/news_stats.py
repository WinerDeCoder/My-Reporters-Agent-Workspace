"""News momentum. Pure functions: no DB, no clock."""

from datetime import datetime


def points_per_hour(points: int, posted_at: datetime, now: datetime) -> float:
    """HN points per hour since posting; age is floored at 1 h so brand-new posts don't spike."""
    hours = max((now - posted_at).total_seconds() / 3600, 1.0)
    return points / hours
