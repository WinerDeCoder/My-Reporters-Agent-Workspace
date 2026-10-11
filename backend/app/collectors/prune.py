"""Weekly prune (REQ-COL-006, narrowed by Q-013 until briefs exist in spec 005):
HN stories older than `retention_days`, and snapshots of repos no longer tracked."""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.config import AppConfig, get_config
from app.db import SessionLocal
from app.models import NewsItem, Repo, RepoSnapshot

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class PruneCutoffs:
    news_before: datetime  # stories posted before this are deleted
    untracked_before: datetime  # repos last seen before this lose their snapshots


def prune_cutoffs(cfg: AppConfig, now: datetime) -> PruneCutoffs:
    return PruneCutoffs(
        news_before=now - timedelta(days=cfg.sources.hacker_news.retention_days),
        untracked_before=now - timedelta(days=cfg.sources.github_api.track_days),
    )


async def prune_old_data(session_factory: async_sessionmaker = SessionLocal) -> int:
    """Delete old stories and untracked repos' snapshots. Returns rows deleted."""
    cutoffs = prune_cutoffs(get_config(), datetime.now(UTC))
    async with session_factory() as session:
        news = await session.execute(
            delete(NewsItem).where(NewsItem.posted_at < cutoffs.news_before)
        )
        untracked = select(Repo.id).where(Repo.last_seen < cutoffs.untracked_before)
        snaps = await session.execute(
            delete(RepoSnapshot).where(RepoSnapshot.repo_id.in_(untracked))
        )
        await session.commit()
    log.info("Prune: %d old stories, %d untracked snapshots", news.rowcount, snaps.rowcount)
    return news.rowcount + snaps.rowcount
