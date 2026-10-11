"""TC-002-05: points per hour."""

from datetime import UTC, datetime, timedelta

import pytest

from app.news_stats import points_per_hour

NOW = datetime(2026, 10, 11, 12, 0, tzinfo=UTC)


def test_normal_age():
    assert points_per_hour(300, NOW - timedelta(hours=3), NOW) == pytest.approx(100)


def test_brand_new_post_is_floored_at_one_hour():
    assert points_per_hour(40, NOW - timedelta(minutes=10), NOW) == pytest.approx(40)


def test_old_post():
    assert points_per_hour(480, NOW - timedelta(days=2), NOW) == pytest.approx(10)
