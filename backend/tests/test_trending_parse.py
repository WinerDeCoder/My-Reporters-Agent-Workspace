"""TC-001-01..03: GitHub Trending parsing and URL building."""

from pathlib import Path

from app.collectors.github_trending import parse_trending, trending_urls
from app.config import TrendingConfig

FIXTURE = Path(__file__).parent / "fixtures" / "trending.html"


def test_parse_saved_page():
    names = parse_trending(FIXTURE.read_text(encoding="utf-8"))
    assert len(names) == 11
    assert names[0] == "morluto/rea"
    assert "berriai/litellm" in names  # lowercased
    assert all(name.count("/") == 1 for name in names)
    assert len(set(names)) == len(names)


def test_parse_unknown_layout_returns_empty():
    html = "<html><body><div class='repo-list'><a href='/a/b'>a/b</a></div></body></html>"
    assert parse_trending(html) == []


def test_parse_dedupes_and_skips_non_repo_links():
    html = (
        "<article class='Box-row'><h2><a href='/Owner/Repo'>x</a></h2></article>"
        "<article class='Box-row'><h2><a href='/owner/repo'>x</a></h2></article>"
        "<article class='Box-row'><h2><a href='/sponsors/someone/extra'>x</a></h2></article>"
    )
    assert parse_trending(html) == ["owner/repo"]


def test_trending_urls():
    cfg = TrendingConfig(languages=["", "python"], ranges=["daily", "weekly"])
    assert trending_urls(cfg) == [
        "https://github.com/trending?since=daily",
        "https://github.com/trending?since=weekly",
        "https://github.com/trending/python?since=daily",
        "https://github.com/trending/python?since=weekly",
    ]
