"""TC-005-01..02 and prune helper: brief item selection, timing, briefed ids."""

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from app.brief import brief_due, select_brief_items
from app.collectors.prune import briefed_ids
from app.news_feed import NewsRow
from app.repo_stats import RepoRow

T = datetime(2026, 10, 11, tzinfo=UTC)


def repo(i: int, score: float | None) -> RepoRow:
    return RepoRow(
        id=i, full_name=f"o/r{i}", url=f"https://github.com/o/r{i}", description=f"repo {i}",
        language="Python", topics=[], license=None, stars=100 * i, stars_per_day=score,
        snapshots=2, first_seen=T, last_seen=T, score=score, matched_topics=["agents"],
    )  # fmt: skip


def story(i: int, score: float | None) -> NewsRow:
    return NewsRow(
        id=i, hn_id=1000 + i, title=f"Story {i}", url=f"https://x.com/{i}", domain="x.com",
        hn_url=f"https://news.ycombinator.com/item?id={1000 + i}", points=50, comments=5,
        posted_at=T, points_per_hour=10.0, linked_repo=None, matched_topics=[],
        ai_dev=score is not None, score=score,
    )  # fmt: skip


def test_select_layout_top_story_is_first_repo():
    repos = [repo(i, 100.0 - i) for i in range(1, 9)]  # already in score order
    news = [story(i, 50.0 - i) for i in range(1, 6)]
    items = select_brief_items(repos, news, top_repos=5, top_news=3)
    assert [(it["section"], it["item_type"], it["item_id"]) for it in items] == [
        ("top", "repo", 1),
        ("repos", "repo", 2),
        ("repos", "repo", 3),
        ("repos", "repo", 4),
        ("repos", "repo", 5),
        ("news", "news", 1),
        ("news", "news", 2),
        ("news", "news", 3),
    ]
    top = items[0]
    assert (top["title"], top["stars"], top["matched_topics"]) == ("o/r1", 100, ["agents"])
    assert items[5]["hn_url"].endswith("1001") and items[5]["points"] == 50


def test_select_skips_unscored_items():
    repos = [repo(1, None), repo(2, 80.0), repo(3, None), repo(4, 60.0)]
    news = [story(1, None), story(2, 9.0)]  # story 1 is not AI/dev
    items = select_brief_items(repos, news, top_repos=5, top_news=3)
    assert [(it["section"], it["item_id"]) for it in items] == [
        ("top", 2),
        ("repos", 4),
        ("news", 2),
    ]


def test_select_with_nothing_scored():
    assert select_brief_items([repo(1, None)], [story(1, None)], 5, 3) == []


def test_brief_due():
    tz = ZoneInfo("Asia/Ho_Chi_Minh")
    assert not brief_due(datetime(2026, 10, 12, 7, 29, tzinfo=tz), "07:30")
    assert brief_due(datetime(2026, 10, 12, 7, 30, tzinfo=tz), "07:30")
    assert brief_due(datetime(2026, 10, 12, 21, 0, tzinfo=tz), "07:30")
    assert not brief_due(datetime(2026, 10, 12, 0, 5, tzinfo=tz), "07:30")


def test_briefed_ids():
    items = [
        [{"item_type": "repo", "item_id": 1}, {"item_type": "news", "item_id": 7}],
        None,
        [{"item_type": "repo", "item_id": "3"}, {"bad": "entry"}],
    ]
    assert briefed_ids(items) == ({1, 3}, {7})
