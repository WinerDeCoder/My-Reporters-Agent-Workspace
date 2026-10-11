"""Hacker News collector (Algolia API): stories + GitHub-linked repo candidates.

REQ-COL-003, REQ-COL-004. Every story is stored; topic filtering happens in scoring (Q-011).
"""

import logging
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import urlparse

import httpx
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.collectors import make_client, transient_retry
from app.collectors.github_trending import upsert_candidates
from app.config import HackerNewsConfig, get_config
from app.db import SessionLocal
from app.models import NewsItem, Repo

log = logging.getLogger(__name__)

ALGOLIA_SEARCH = "https://hn.algolia.com/api/v1/search"

# First path segments on github.com that are not user/org names.
GITHUB_RESERVED = {
    "about", "apps", "collections", "customer-stories", "enterprise", "explore", "features",
    "login", "marketplace", "orgs", "pricing", "readme", "search", "security", "settings",
    "site", "sponsors", "topics", "trending",
}  # fmt: skip


@dataclass(frozen=True)
class Story:
    hn_id: int
    title: str
    url: str | None
    points: int
    comments: int
    posted_at: datetime


def algolia_queries(cfg: HackerNewsConfig, now: datetime) -> dict[str, dict[str, Any]]:
    """Front page + popular recent stories (Q-010), as named Algolia query params."""
    since = int((now - timedelta(hours=cfg.popular_window_hours)).timestamp())
    return {
        "front_page": {"tags": "front_page", "hitsPerPage": 50},
        "popular": {
            "tags": "story",
            "numericFilters": f"points>{cfg.popular_min_points},created_at_i>{since}",
            "hitsPerPage": 100,
        },
    }


def parse_hits(hits: Iterable[Mapping[str, Any]]) -> list[Story]:
    stories = []
    for hit in hits:
        title = (hit.get("title") or "").strip()
        if not title or not hit.get("objectID") or hit.get("created_at_i") is None:
            continue
        stories.append(
            Story(
                hn_id=int(hit["objectID"]),
                title=title,
                url=hit.get("url") or None,
                points=int(hit.get("points") or 0),
                comments=int(hit.get("num_comments") or 0),
                posted_at=datetime.fromtimestamp(int(hit["created_at_i"]), UTC),
            )
        )
    return stories


def github_repo_from_url(url: str | None) -> str | None:
    """`owner/repo` (lowercased) if the URL points into a GitHub repository, else None."""
    if not url:
        return None
    parsed = urlparse(url)
    if parsed.hostname not in ("github.com", "www.github.com"):
        return None
    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) < 2 or parts[0].lower() in GITHUB_RESERVED:
        return None
    owner, repo = parts[0].lower(), parts[1].lower().removesuffix(".git")
    return f"{owner}/{repo}" if owner and repo else None


def merge_stories(*batches: Iterable[Story]) -> list[Story]:
    """Union by hn_id, keeping the higher points and comments seen."""
    merged: dict[int, Story] = {}
    for batch in batches:
        for story in batch:
            seen = merged.get(story.hn_id)
            merged[story.hn_id] = (
                story
                if seen is None
                else replace(
                    seen,
                    points=max(seen.points, story.points),
                    comments=max(seen.comments, story.comments),
                )
            )
    return list(merged.values())


@transient_retry
async def fetch_hits(client: httpx.AsyncClient, params: dict[str, Any]) -> list[dict[str, Any]]:
    resp = await client.get(ALGOLIA_SEARCH, params=params)
    resp.raise_for_status()
    return resp.json().get("hits", [])


async def collect_hacker_news(session_factory: async_sessionmaker = SessionLocal) -> int:
    """Fetch stories, upsert GitHub-linked repo candidates, upsert stories. Returns story count."""
    cfg = get_config().sources.hacker_news
    batches = []
    async with make_client() as client:
        for name, params in algolia_queries(cfg, datetime.now(UTC)).items():
            stories = parse_hits(await fetch_hits(client, params))
            log.info("HN %s: %d stories", name, len(stories))
            batches.append(stories)
    stories = merge_stories(*batches)

    repo_for_story = {s.hn_id: github_repo_from_url(s.url) for s in stories}
    repo_names = sorted({name for name in repo_for_story.values() if name})

    async with session_factory() as session:
        await upsert_candidates(session, repo_names)  # last_seen = now -> tracked
        repo_ids = {}
        if repo_names:
            rows = await session.execute(
                select(Repo.full_name, Repo.id).where(Repo.full_name.in_(repo_names))
            )
            repo_ids = dict(rows.all())

        if stories:
            stmt = pg_insert(NewsItem).values(
                [
                    {
                        "hn_id": s.hn_id,
                        "title": s.title,
                        "url": s.url,
                        "points": s.points,
                        "comments": s.comments,
                        "posted_at": s.posted_at,
                        "linked_repo_id": repo_ids.get(repo_for_story[s.hn_id] or ""),
                    }
                    for s in stories
                ]
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=[NewsItem.hn_id],
                set_={
                    "title": stmt.excluded.title,
                    "url": stmt.excluded.url,
                    "points": stmt.excluded.points,
                    "comments": stmt.excluded.comments,
                    "linked_repo_id": stmt.excluded.linked_repo_id,
                    "fetched_at": func.now(),
                },
            )
            await session.execute(stmt)
            await session.commit()

    log.info("HN: %d stories upserted, %d GitHub repos linked", len(stories), len(repo_names))
    return len(stories)
