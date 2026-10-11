"""Weekly leaderboard (spec 006): top repos by raw stars gained over 7 days (Q-026).

Stored as a `briefs` row of type `weekly`, dated the Monday of its week; built Mondays at
`leaderboard.run_at` (07:35, after the daily brief), once per week.
"""

import logging
from collections import defaultdict
from collections.abc import Mapping, Sequence
from datetime import UTC, date, datetime, time, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.brief import local_now
from app.config import get_config
from app.db import SessionLocal
from app.models import Brief, RepoSnapshot
from app.momentum import Snapshot, stars_gained
from app.repo_stats import RepoRow, load_repo_rows

log = logging.getLogger(__name__)

WINDOW = timedelta(days=7)


def week_start(now_local: datetime) -> date:
    """Monday of the local week."""
    return now_local.date() - timedelta(days=now_local.weekday())


def leaderboard_due(now_local: datetime, run_at: str) -> bool:
    """True from Monday `run_at` until the end of the week."""
    hour, minute = (int(x) for x in run_at.split(":"))
    return now_local.weekday() > 0 or now_local.time() >= time(hour, minute)


def rank_weekly(
    rows: Sequence[RepoRow],
    snapshots: Mapping[int, Sequence[Snapshot]],
    now: datetime,
    size: int,
) -> list[dict[str, Any]]:
    """Top `size` repos by stars gained over the last 7 days. Repos tracked for less than
    7 days count from their first snapshot and carry `since` (its date)."""
    window_start = now - WINDOW
    entries = []
    for r in rows:
        snaps = sorted(snapshots.get(r.id, []), key=lambda s: s.taken_at)
        gained = stars_gained(snaps, since=window_start)
        if gained is None:
            continue
        in_window_from_start = any(s.taken_at <= window_start for s in snaps)
        entries.append(
            {
                "item_type": "repo",
                "item_id": r.id,
                "title": r.full_name,
                "url": r.url,
                "description": r.description,
                "language": r.language,
                "stars": snaps[-1].stars,
                "stars_gained": gained,
                "since": None if in_window_from_start else snaps[0].taken_at.date().isoformat(),
                "matched_topics": list(r.matched_topics),
            }
        )
    entries.sort(key=lambda e: (-e["stars_gained"], -e["stars"]))
    top = entries[:size]
    for rank, entry in enumerate(top, 1):
        entry["rank"] = rank
        entry["section"] = "leaderboard"
    return top


async def snapshots_since(
    session: AsyncSession, repo_ids: Sequence[int], since: datetime
) -> dict[int, list[Snapshot]]:
    out: dict[int, list[Snapshot]] = defaultdict(list)
    if repo_ids:
        result = await session.execute(
            select(RepoSnapshot.repo_id, RepoSnapshot.taken_at, RepoSnapshot.stars).where(
                RepoSnapshot.repo_id.in_(repo_ids), RepoSnapshot.taken_at >= since
            )
        )
        for repo_id, taken_at, stars in result:
            out[repo_id].append(Snapshot(taken_at, stars))
    return out


async def build_weekly_leaderboard(force: bool = False) -> int:
    """Build this week's leaderboard once. Returns entries in a newly built one (0 if skipped)."""
    cfg = get_config()
    now_local = local_now(cfg)
    if not force and not leaderboard_due(now_local, cfg.leaderboard.run_at):
        log.info("Leaderboard not due yet this week; skipping")
        return 0
    week = week_start(now_local)
    async with SessionLocal() as session:
        exists = await session.scalar(
            select(Brief.id).where(Brief.type == "weekly", Brief.date == week)
        )
        if exists:
            log.info("Leaderboard for week of %s already exists", week)
            return 0
        now = datetime.now(UTC)
        rows = await load_repo_rows(session, cfg.sources.github_api.track_days)
        # one extra day so a snapshot just before the window start can be the base
        snaps = await snapshots_since(
            session, [r.id for r in rows], now - WINDOW - timedelta(days=1)
        )
        entries = rank_weekly(rows, snaps, now, cfg.brief.leaderboard_size)
        session.add(Brief(type="weekly", date=week, items=entries))
        await session.commit()
    log.info("Leaderboard for week of %s built with %d entries", week, len(entries))
    return len(entries)


async def latest_leaderboard(session: AsyncSession) -> Brief | None:
    return await session.scalar(
        select(Brief).where(Brief.type == "weekly").order_by(Brief.date.desc()).limit(1)
    )
