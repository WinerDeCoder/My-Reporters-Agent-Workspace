"""Weekly prune (REQ-COL-006): HN stories older than `retention_days` unless a brief references
them, and snapshots of repos no longer tracked that never reached a brief (spec 005)."""

import logging
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.config import AppConfig, get_config
from app.db import SessionLocal
from app.models import Brief, NewsItem, Repo, RepoSnapshot

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class PruneCutoffs:
    news_before: datetime  # stories posted before this are deleted
    untracked_before: datetime  # repos last seen before this lose their snapshots


def briefed_ids(
    briefs_items: Iterable[Sequence[dict[str, Any]] | None],
) -> tuple[set[int], set[int]]:
    """(repo ids, news ids) referenced by any brief (spec 005 prune rules)."""
    repos: set[int] = set()
    news: set[int] = set()
    for items in briefs_items:
        for it in items or []:
            if isinstance(it, dict) and "item_id" in it:
                (repos if it.get("item_type") == "repo" else news).add(int(it["item_id"]))
    return repos, news


def prune_cutoffs(cfg: AppConfig, now: datetime) -> PruneCutoffs:
    return PruneCutoffs(
        news_before=now - timedelta(days=cfg.sources.hacker_news.retention_days),
        untracked_before=now - timedelta(days=cfg.sources.github_api.track_days),
    )


async def prune_old_data(session_factory: async_sessionmaker = SessionLocal) -> int:
    """Delete old stories and untracked repos' snapshots. Returns rows deleted."""
    cutoffs = prune_cutoffs(get_config(), datetime.now(UTC))
    async with session_factory() as session:
        briefed_repos, briefed_news = briefed_ids(await session.scalars(select(Brief.items)))
        news = await session.execute(
            delete(NewsItem).where(
                NewsItem.posted_at < cutoffs.news_before,
                NewsItem.id.not_in(briefed_news or {-1}),  # stories in a brief are kept
            )
        )
        untracked = select(Repo.id).where(
            Repo.last_seen < cutoffs.untracked_before,
            Repo.id.not_in(briefed_repos or {-1}),  # repos that reached a brief keep history
        )
        snaps = await session.execute(
            delete(RepoSnapshot).where(RepoSnapshot.repo_id.in_(untracked))
        )
        await session.commit()
    log.info("Prune: %d old stories, %d untracked snapshots", news.rowcount, snaps.rowcount)
    return news.rowcount + snaps.rowcount
