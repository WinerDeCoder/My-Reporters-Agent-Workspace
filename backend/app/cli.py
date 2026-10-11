"""Run collectors once and inspect momentum without waiting for the scheduler.

uv run python -m app.cli collect trending
uv run python -m app.cli collect github
uv run python -m app.cli momentum --top 20
"""

import argparse
import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from app.config import get_config
from app.db import SessionLocal, engine
from app.repo_stats import RepoRow, load_repo_rows
from app.scheduler import JOBS, run_job

# CLI name -> scheduler job name (CLI runs are recorded under the same job name)
COLLECTORS = {"trending": "github_trending", "github": "github_api"}


async def _run(fn: Callable[[], Awaitable[Any]]) -> Any:
    try:
        return await fn()
    finally:
        await engine.dispose()


async def momentum(top: int) -> list[RepoRow]:
    """Top tracked repos by stars/day (repos still collecting history are skipped)."""
    async with SessionLocal() as session:
        rows = await load_repo_rows(session, get_config().sources.github_api.track_days)
    return [r for r in rows if r.stars_per_day is not None][:top]


async def print_momentum(top: int) -> None:
    ranked = await _run(lambda: momentum(top))
    if not ranked:
        print("No momentum yet: needs at least two snapshots 6+ hours apart.")
        return
    print(f"{'#':>3}  {'repo':<45} {'stars/day':>10} {'stars':>9}")
    for i, row in enumerate(ranked, 1):
        print(f"{i:>3}  {row.full_name:<45} {row.stars_per_day:>10.1f} {row.stars or 0:>9,}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="python -m app.cli", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    collect = sub.add_parser(
        "collect", help="run one collector once (recorded like a scheduled run)"
    )
    collect.add_argument("source", choices=sorted(COLLECTORS))
    mom = sub.add_parser("momentum", help="print top repos by stars/day")
    mom.add_argument("--top", type=int, default=20)
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)-7s %(name)s: %(message)s"
    )
    if args.command == "collect":
        job = COLLECTORS[args.source]
        result = asyncio.run(_run(lambda: run_job(job, JOBS[job])))
        print(f"{args.source}: {result}")
    else:
        asyncio.run(print_momentum(args.top))


if __name__ == "__main__":
    main()
