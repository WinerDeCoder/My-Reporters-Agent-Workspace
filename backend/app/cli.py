"""Run collectors once and inspect momentum without waiting for the scheduler.

uv run python -m app.cli collect trending
uv run python -m app.cli collect github
uv run python -m app.cli momentum --top 20
"""

import argparse
import asyncio
import logging
from collections import defaultdict
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select

from app.collectors.github_api import collect_github
from app.collectors.github_trending import collect_trending
from app.db import SessionLocal, engine
from app.models import Repo, RepoSnapshot
from app.momentum import Snapshot, stars_per_day

COLLECTORS: dict[str, Callable[[], Awaitable[Any]]] = {
    "trending": collect_trending,
    "github": collect_github,
}


async def _run(fn: Callable[[], Awaitable[Any]]) -> Any:
    try:
        return await fn()
    finally:
        await engine.dispose()


async def momentum(top: int) -> list[tuple[str, float, int]]:
    """Top repos by stars/day over the last 48 h of snapshots: (name, stars/day, stars)."""
    since = datetime.now(UTC) - timedelta(hours=48)
    async with SessionLocal() as session:
        rows = await session.execute(
            select(Repo.full_name, RepoSnapshot.taken_at, RepoSnapshot.stars)
            .join(RepoSnapshot, RepoSnapshot.repo_id == Repo.id)
            .where(RepoSnapshot.taken_at >= since)
        )
        by_repo: dict[str, list[Snapshot]] = defaultdict(list)
        for name, taken_at, stars in rows:
            by_repo[name].append(Snapshot(taken_at, stars))

    ranked = []
    for name, snaps in by_repo.items():
        rate = stars_per_day(snaps)
        if rate is not None:
            ranked.append((name, rate, max(snaps, key=lambda s: s.taken_at).stars))
    ranked.sort(key=lambda r: r[1], reverse=True)
    return ranked[:top]


async def print_momentum(top: int) -> None:
    ranked = await _run(lambda: momentum(top))
    if not ranked:
        print("No momentum yet: needs at least two snapshots 6+ hours apart.")
        return
    print(f"{'#':>3}  {'repo':<45} {'stars/day':>10} {'stars':>9}")
    for i, (name, rate, stars) in enumerate(ranked, 1):
        print(f"{i:>3}  {name:<45} {rate:>10.1f} {stars:>9,}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="python -m app.cli", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    collect = sub.add_parser("collect", help="run one collector once")
    collect.add_argument("source", choices=sorted(COLLECTORS))
    mom = sub.add_parser("momentum", help="print top repos by stars/day")
    mom.add_argument("--top", type=int, default=20)
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)-7s %(name)s: %(message)s"
    )
    if args.command == "collect":
        result = asyncio.run(_run(COLLECTORS[args.source]))
        print(f"{args.source}: {result}")
    else:
        asyncio.run(print_momentum(args.top))


if __name__ == "__main__":
    main()
