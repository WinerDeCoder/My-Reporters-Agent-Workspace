"""Run collectors once and inspect momentum without waiting for the scheduler.

uv run python -m app.cli collect trending
uv run python -m app.cli collect github
uv run python -m app.cli collect hn
uv run python -m app.cli prune
uv run python -m app.cli momentum --top 20
uv run python -m app.cli top
uv run python -m app.cli cards      # write today's cards now (LLM calls; cached by source)
uv run python -m app.cli usage      # LLM tokens used this month vs the cap
"""

import argparse
import asyncio
import logging
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any

from app.cards import usage_summary
from app.config import get_config
from app.db import SessionLocal, engine
from app.news_feed import NewsRow, load_news_rows
from app.repo_stats import RepoRow, load_repo_rows, rank_by_score
from app.scheduler import JOBS, run_job
from app.scoring import boost

# CLI name -> scheduler job name (CLI runs are recorded under the same job name)
COLLECTORS = {"trending": "github_trending", "github": "github_api", "hn": "hacker_news"}


async def _run(fn: Callable[[], Awaitable[Any]]) -> Any:
    try:
        return await fn()
    finally:
        await engine.dispose()


async def print_usage() -> None:
    async def load() -> dict[str, Any]:
        async with SessionLocal() as session:
            return await usage_summary(session, get_config(), datetime.now(UTC))

    u = await _run(load)
    pct = u["tokens"] / u["cap"] * 100 if u["cap"] else 100.0
    print(
        f"LLM usage since {u['month_start']:%Y-%m-%d}: {u['calls']} calls, "
        f"{u['input_tokens']:,} in + {u['output_tokens']:,} out = {u['tokens']:,} tokens "
        f"({pct:.1f}% of the {u['cap']:,} cap)"
    )
    if u["estimated_usd"] is not None:
        print(f"Estimated cost: ${u['estimated_usd']:.2f}")


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


async def print_top(n_repos: int, n_news: int) -> None:
    """Today's top repos and stories by score, with the parts of each score (spec 003)."""

    async def load() -> tuple[list[RepoRow], list[NewsRow]]:
        async with SessionLocal() as session:
            repos = await load_repo_rows(session, get_config().sources.github_api.track_days)
            news = await load_news_rows(session)
        return rank_by_score(repos), news

    repos, news = await _run(load)
    cfg = get_config().interests

    def boost_of(topics: list[str]) -> float:
        return boost(len(topics), cfg.topic_boost, cfg.max_boost)

    scored = [r for r in repos if r.score is not None][:n_repos]
    print(f"\nTOP REPOS  (score = stars/day x topic boost x penalties)  [{len(repos)} tracked]")
    if not scored:
        matched = [r for r in repos if r.matched_topics]
        print("  No repo scores yet: stars/day needs two snapshots 6+ h apart.")
        print(f"  {len(matched)} repos already match your topics, e.g.:")
        for r in matched[:5]:
            print(f"    {r.full_name:<42} topics: {', '.join(r.matched_topics)}")
    for i, r in enumerate(scored, 1):
        print(
            f"{i:>3}. {r.full_name:<42} {r.score:>8.1f} = {r.stars_per_day:>7.1f}/day"
            f" x {boost_of(r.matched_topics):.2f}  {', '.join(r.matched_topics) or '-'}"
        )

    eligible = [n for n in news if n.score is not None]
    counts = f"[{len(eligible)}/{len(news)} AI/dev]"
    print(f"\nTOP NEWS  (score = points/hour x topic boost x penalties)  {counts}")
    for i, n in enumerate(eligible[:n_news], 1):
        print(
            f"{i:>3}. {n.title[:58]:<58} {n.score:>6.1f} = {n.points_per_hour:>5.1f}/h"
            f" x {boost_of(n.matched_topics):.2f}  {', '.join(n.matched_topics) or '-'}"
        )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="python -m app.cli", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    collect = sub.add_parser(
        "collect", help="run one collector once (recorded like a scheduled run)"
    )
    collect.add_argument("source", choices=sorted(COLLECTORS))
    sub.add_parser("prune", help="delete old HN stories and untracked repos' snapshots now")
    mom = sub.add_parser("momentum", help="print top repos by stars/day")
    mom.add_argument("--top", type=int, default=20)
    top = sub.add_parser("top", help="print today's top repos and stories by score")
    top.add_argument("--repos", type=int, default=10)
    top.add_argument("--news", type=int, default=10)
    sub.add_parser("cards", help="write today's cards now (recorded like the 07:25 job)")
    sub.add_parser("usage", help="LLM tokens used this month vs the cap")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)-7s %(name)s: %(message)s"
    )
    if args.command == "collect":
        job = COLLECTORS[args.source]
        result = asyncio.run(_run(lambda: run_job(job, JOBS[job])))
        print(f"{args.source}: {result}")
    elif args.command == "prune":
        result = asyncio.run(_run(lambda: run_job("prune", JOBS["prune"])))
        print(f"prune: {result} rows deleted")
    elif args.command == "top":
        asyncio.run(print_top(args.repos, args.news))
    elif args.command == "cards":
        result = asyncio.run(_run(lambda: run_job("cards", JOBS["cards"])))
        print(f"cards: {result} written")
    elif args.command == "usage":
        asyncio.run(print_usage())
    else:
        asyncio.run(print_momentum(args.top))


if __name__ == "__main__":
    main()
