"""TC-002-01..04: HN parsing, GitHub URL matching, queries, merging (saved Algolia fixtures)."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.collectors.hacker_news import (
    Story,
    algolia_queries,
    github_repo_from_url,
    merge_stories,
    parse_hits,
)
from app.config import HackerNewsConfig

FIXTURES = Path(__file__).parent / "fixtures"


def load_hits(name: str) -> list[dict]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))["hits"]


def test_parse_saved_front_page():
    stories = parse_hits(load_hits("hn_front_page.json"))
    assert len(stories) == 29
    assert len({s.hn_id for s in stories}) == 29
    s = stories[0]
    assert isinstance(s.hn_id, int) and s.title and s.points >= 0 and s.comments >= 0
    assert s.posted_at.tzinfo is UTC
    linked = {github_repo_from_url(s.url) for s in stories} - {None}
    assert "rociiu/talorys" in linked
    assert len(linked) == 5


def test_parse_handles_missing_fields():
    hits = [
        {"objectID": "1", "title": "Ask HN: anything?", "url": None, "points": None,
         "num_comments": None, "created_at_i": 1_760_000_000},
        {"objectID": "2", "title": "", "url": "https://x.com", "created_at_i": 1_760_000_000},
        {"objectID": "3", "title": "No time", "url": "https://x.com"},
    ]  # fmt: skip
    [ask] = parse_hits(hits)
    assert (ask.hn_id, ask.url, ask.points, ask.comments) == (1, None, 0, 0)
    assert ask.posted_at == datetime.fromtimestamp(1_760_000_000, UTC)


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://github.com/rociiu/talorys", "rociiu/talorys"),
        ("https://www.github.com/Owner/Repo/tree/main/docs", "owner/repo"),
        ("https://github.com/owner/repo.git", "owner/repo"),
        ("https://github.com/owner/repo#readme", "owner/repo"),
        ("https://github.com/owner", None),
        ("https://github.com/orgs/acme/repositories", None),
        ("https://github.com/topics/agents", None),
        ("https://github.com/marketplace/actions/foo", None),
        ("https://gist.github.com/someone/abc123", None),
        ("https://example.com/github.com/a/b", None),
        (None, None),
    ],
)
def test_github_repo_from_url(url, expected):
    assert github_repo_from_url(url) == expected


def test_algolia_queries():
    cfg = HackerNewsConfig()  # defaults: > 100 points within 26 h (daily runs overlap, Q-014)
    now = datetime(2026, 10, 11, 12, 0, tzinfo=UTC)
    q = algolia_queries(cfg, now)
    assert q["front_page"]["tags"] == "front_page"
    since = int(now.timestamp()) - 26 * 3600
    assert q["popular"]["tags"] == "story"
    assert q["popular"]["numericFilters"] == f"points>100,created_at_i>{since}"


def test_merge_stories():
    t = datetime(2026, 10, 11, tzinfo=UTC)
    a = [Story(1, "One", None, 50, 10, t), Story(2, "Two", None, 5, 1, t)]
    b = [Story(1, "One", None, 120, 8, t), Story(3, "Three", None, 300, 40, t)]
    merged = {s.hn_id: s for s in merge_stories(a, b)}
    assert set(merged) == {1, 2, 3}
    assert (merged[1].points, merged[1].comments) == (120, 10)


def test_merge_saved_fixtures_dedupes():
    front = parse_hits(load_hits("hn_front_page.json"))
    popular = parse_hits(load_hits("hn_popular.json"))
    merged = merge_stories(front, popular)
    overlap = {s.hn_id for s in front} & {s.hn_id for s in popular}
    assert len(merged) == len(front) + len(popular) - len(overlap)
