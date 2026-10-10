"""GitHub API collector: metadata + one star snapshot per tracked repo. REQ-COL-002, REQ-NFR-004."""

import asyncio
import hashlib
import logging
import time
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.collectors import make_client, transient_retry
from app.config import get_config, get_secrets
from app.db import SessionLocal
from app.models import Repo, RepoSnapshot

log = logging.getLogger(__name__)

MAX_RATE_LIMIT_WAIT = 900.0  # seconds; never sleep longer than 15 min in one go
CONCURRENCY = 5

Sleep = Callable[[float], Awaitable[None]]


@dataclass
class RepoInfo:
    full_name: str
    description: str | None
    topics: list[str] = field(default_factory=list)
    language: str | None = None
    license: str | None = None
    stars: int = 0
    forks: int = 0
    readme_hash: str | None = None


def parse_repo_payload(data: Mapping[str, Any]) -> RepoInfo:
    """Map a `GET /repos/{owner}/{repo}` response to the fields we store."""
    license_ = data.get("license") or {}
    return RepoInfo(
        full_name=str(data["full_name"]).lower(),
        description=data.get("description"),
        topics=list(data.get("topics") or []),
        language=data.get("language"),
        license=license_.get("spdx_id"),
        stars=int(data.get("stargazers_count") or 0),
        forks=int(data.get("forks_count") or 0),
    )


def rate_limit_wait(status: int, headers: Mapping[str, str], now: float) -> float | None:
    """Seconds to wait if this response is a rate limit, else None. `now` is a Unix time."""
    if status not in (403, 429):
        return None
    if "retry-after" in headers:
        return min(float(headers["retry-after"]), MAX_RATE_LIMIT_WAIT)
    if headers.get("x-ratelimit-remaining") == "0" and "x-ratelimit-reset" in headers:
        return min(max(float(headers["x-ratelimit-reset"]) - now, 1.0), MAX_RATE_LIMIT_WAIT)
    if status == 429:
        return 60.0
    return None  # a 403 that isn't a rate limit (e.g. access blocked)


@transient_retry
async def _get(
    client: httpx.AsyncClient, url: str, headers: dict[str, str] | None
) -> httpx.Response:
    resp = await client.get(url, headers=headers)
    if resp.status_code >= 500:
        resp.raise_for_status()
    return resp


async def get_respecting_rate_limit(
    client: httpx.AsyncClient,
    url: str,
    headers: dict[str, str] | None = None,
    sleep: Sleep = asyncio.sleep,
) -> httpx.Response:
    """GET once; on a rate-limit response wait as told and retry once."""
    resp = await _get(client, url, headers)
    wait = rate_limit_wait(resp.status_code, resp.headers, time.time())
    if wait is None:
        return resp
    log.warning("GitHub rate limit on %s; waiting %.0fs", url, wait)
    await sleep(wait)
    return await _get(client, url, headers)


async def fetch_repo(
    client: httpx.AsyncClient, full_name: str, sleep: Sleep = asyncio.sleep
) -> RepoInfo | None:
    """Repo metadata + README hash. None if the repo no longer exists (404)."""
    resp = await get_respecting_rate_limit(client, f"/repos/{full_name}", sleep=sleep)
    if resp.status_code == 404:
        log.warning("Repo %s not found (deleted or renamed?); skipping", full_name)
        return None
    resp.raise_for_status()
    info = parse_repo_payload(resp.json())

    readme = await get_respecting_rate_limit(
        client,
        f"/repos/{full_name}/readme",
        headers={"Accept": "application/vnd.github.raw"},
        sleep=sleep,
    )
    if readme.status_code == 200:
        info.readme_hash = hashlib.sha256(readme.content).hexdigest()
    elif readme.status_code != 404:
        log.warning("README for %s: HTTP %d", full_name, readme.status_code)
    return info


async def tracked_repos(session: AsyncSession, track_days: int, now: datetime) -> list[Repo]:
    """Candidates whose last_seen is within track_days (window counted from last seen, Q-001)."""
    since = now - timedelta(days=track_days)
    result = await session.scalars(select(Repo).where(Repo.last_seen >= since).order_by(Repo.id))
    return list(result)


async def collect_github(session_factory: async_sessionmaker = SessionLocal) -> int:
    """Snapshot every tracked repo. Returns the number of snapshots stored."""
    cfg = get_config().sources.github_api
    async with session_factory() as session:
        targets = [
            (r.id, r.full_name)
            for r in await tracked_repos(session, cfg.track_days, datetime.now(UTC))
        ]
    if not get_secrets().github_token:
        log.warning("GITHUB_TOKEN is not set: GitHub allows only 60 requests/hour without it")

    requests = 0

    async def count_request(_request: httpx.Request) -> None:
        nonlocal requests
        requests += 1

    semaphore = asyncio.Semaphore(CONCURRENCY)

    async def one(name: str) -> RepoInfo | None:
        async with semaphore:
            try:
                return await fetch_repo(client, name)
            except httpx.HTTPError as exc:
                log.warning("GitHub API failed for %s: %s", name, exc)
                return None

    async with make_client(github_api=True, event_hooks={"request": [count_request]}) as client:
        infos = await asyncio.gather(*(one(name) for _, name in targets))

    stored = 0
    async with session_factory() as session:
        for (repo_id, name), info in zip(targets, infos, strict=True):
            repo = await session.get(Repo, repo_id)
            if info is None or repo is None:
                continue
            if info.full_name != repo.full_name:
                clash = await session.scalar(
                    select(Repo.id).where(Repo.full_name == info.full_name)
                )
                if clash is None:
                    log.info("Repo renamed: %s -> %s", name, info.full_name)
                    repo.full_name = info.full_name
            repo.description = info.description
            repo.topics = info.topics
            repo.language = info.language
            repo.license = info.license
            repo.readme_hash = info.readme_hash
            session.add(RepoSnapshot(repo_id=repo_id, stars=info.stars, forks=info.forks))
            stored += 1
        await session.commit()

    log.info(
        "GitHub API: %d/%d repos snapshotted using %d requests", stored, len(targets), requests
    )
    return stored
