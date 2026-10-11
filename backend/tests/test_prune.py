"""TC-002-06: prune cutoffs from config."""

from datetime import UTC, datetime, timedelta

from app.collectors.prune import prune_cutoffs
from app.config import AppConfig, GithubApiConfig, HackerNewsConfig, SourcesConfig

NOW = datetime(2026, 10, 11, 12, 0, tzinfo=UTC)


def test_prune_cutoffs():
    cfg = AppConfig(
        sources=SourcesConfig(
            hacker_news=HackerNewsConfig(retention_days=30),
            github_api=GithubApiConfig(track_days=14),
        )
    )
    cut = prune_cutoffs(cfg, NOW)
    assert cut.news_before == NOW - timedelta(days=30)
    assert cut.untracked_before == NOW - timedelta(days=14)
