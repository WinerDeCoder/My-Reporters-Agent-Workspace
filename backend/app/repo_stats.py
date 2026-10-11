"""Tracked repos with their latest stars and momentum. Used by the API and the CLI."""

from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.collectors.github_api import tracked_repos
from app.models import Repo, RepoSnapshot
from app.momentum import Snapshot, stars_per_day

HISTORY = timedelta(hours=48)  # enough for the 24 h stars/day window


@dataclass
class RepoRow:
    id: int
    full_name: str
    url: str
    description: str | None
    language: str | None
    topics: list[str]
    license: str | None
    stars: int | None
    stars_per_day: float | None
    snapshots: int
    first_seen: datetime
    last_seen: datetime


def build_repo_rows(
    repos: Iterable[Repo], snapshots: Iterable[tuple[int, Snapshot]]
) -> list[RepoRow]:
    """Pure: join repos with their (repo_id, Snapshot) pairs. Repos without snapshots get
    `stars=None`; stars/day is None until there are 6 h of history (see momentum)."""
    by_repo: dict[int, list[Snapshot]] = defaultdict(list)
    for repo_id, snap in snapshots:
        by_repo[repo_id].append(snap)

    rows = []
    for repo in repos:
        snaps = by_repo.get(repo.id, [])
        latest = max(snaps, key=lambda s: s.taken_at) if snaps else None
        rows.append(
            RepoRow(
                id=repo.id,
                full_name=repo.full_name,
                url=f"https://github.com/{repo.full_name}",
                description=repo.description,
                language=repo.language,
                topics=list(repo.topics or []),
                license=repo.license,
                stars=latest.stars if latest else None,
                stars_per_day=stars_per_day(snaps),
                snapshots=len(snaps),
                first_seen=repo.first_seen,
                last_seen=repo.last_seen,
            )
        )
    return rows


def rank_by_momentum(rows: Sequence[RepoRow]) -> list[RepoRow]:
    """Highest stars/day first; repos still collecting history go last, by stars."""
    return sorted(
        rows,
        key=lambda r: (r.stars_per_day is None, -(r.stars_per_day or 0), -(r.stars or 0)),
    )


async def load_repo_rows(session: AsyncSession, track_days: int) -> list[RepoRow]:
    now = datetime.now(UTC)
    repos = await tracked_repos(session, track_days, now)
    ids = [r.id for r in repos]
    snaps: list[tuple[int, Snapshot]] = []
    if ids:
        result = await session.execute(
            select(RepoSnapshot.repo_id, RepoSnapshot.taken_at, RepoSnapshot.stars).where(
                RepoSnapshot.repo_id.in_(ids), RepoSnapshot.taken_at >= now - HISTORY
            )
        )
        snaps = [(repo_id, Snapshot(taken_at, stars)) for repo_id, taken_at, stars in result]
    return rank_by_momentum(build_repo_rows(repos, snaps))
