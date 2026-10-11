"""Daily brief (spec 005): choose items, build once a day, read it back, record ratings.

Layout (Q-025): top story = #1 repo by score; rising repos = #2..#top_repos; news = top
`top_news` AI/dev stories. Built at `brief_time` (07:30, Q-006), after collection and cards.
"""

import logging
from collections.abc import Sequence
from datetime import UTC, date, datetime, time
from typing import Any, Literal
from zoneinfo import ZoneInfo

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cards import CapReached, get_or_write_card, latest_card
from app.collectors import make_client
from app.config import AppConfig, get_config
from app.db import SessionLocal
from app.models import Brief, Feedback
from app.news_feed import NewsRow, load_news_rows
from app.repo_stats import RepoRow, load_repo_rows, rank_by_score

log = logging.getLogger(__name__)

Section = Literal["top", "repos", "news"]


# ----------------------------------------------------------------- pure helpers


def _repo_item(r: RepoRow, section: Section) -> dict[str, Any]:
    return {
        "section": section,
        "item_type": "repo",
        "item_id": r.id,
        "title": r.full_name,
        "url": r.url,
        "description": r.description,
        "language": r.language,
        "stars": r.stars,
        "stars_per_day": r.stars_per_day,
        "matched_topics": list(r.matched_topics),
        "score": r.score,
    }


def _news_item(n: NewsRow) -> dict[str, Any]:
    return {
        "section": "news",
        "item_type": "news",
        "item_id": n.id,
        "title": n.title,
        "url": n.url,
        "hn_url": n.hn_url,
        "domain": n.domain,
        "points": n.points,
        "comments": n.comments,
        "points_per_hour": n.points_per_hour,
        "linked_repo": n.linked_repo,
        "matched_topics": list(n.matched_topics),
        "score": n.score,
    }


def select_brief_items(
    repos_by_score: Sequence[RepoRow],
    news_by_score: Sequence[NewsRow],
    top_repos: int,
    top_news: int,
) -> list[dict[str, Any]]:
    """Inputs already in "For you" order. Unscored items are never included."""
    repos = [r for r in repos_by_score if r.score is not None][:top_repos]
    news = [n for n in news_by_score if n.score is not None][:top_news]
    items = [_repo_item(r, "top" if i == 0 else "repos") for i, r in enumerate(repos)]
    return items + [_news_item(n) for n in news]


def brief_due(now_local: datetime, brief_time: str) -> bool:
    hour, minute = (int(x) for x in brief_time.split(":"))
    return now_local.time() >= time(hour, minute)


def local_now(cfg: AppConfig) -> datetime:
    return datetime.now(ZoneInfo(cfg.timezone))


# ----------------------------------------------------------------- building


async def brief_for(session: AsyncSession, day: date) -> Brief | None:
    return await session.scalar(select(Brief).where(Brief.type == "daily", Brief.date == day))


async def build_daily_brief(force: bool = False, write_cards: bool = True) -> int:
    """Build today's brief once. Scheduled runs (force=False) do nothing before brief_time.
    Returns the number of items in a newly built brief (0 if skipped or already built)."""
    cfg = get_config()
    now = local_now(cfg)
    if not force and not brief_due(now, cfg.brief_time):
        log.info("Brief not due yet (%s < %s); skipping", now.strftime("%H:%M"), cfg.brief_time)
        return 0
    async with SessionLocal() as session:
        if await brief_for(session, now.date()):
            log.info("Brief for %s already exists", now.date())
            return 0
        repos = rank_by_score(await load_repo_rows(session, cfg.sources.github_api.track_days))
        news = await load_news_rows(session)
        items = select_brief_items(repos, news, cfg.brief.top_repos, cfg.brief.top_news)
        session.add(Brief(type="daily", date=now.date(), items=items))
        await session.commit()
    log.info("Brief for %s built with %d items", now.date(), len(items))

    if write_cards and items:  # usually all cached by the 07:25 cards job
        async with make_client(github_api=True) as gh, make_client() as web, SessionLocal() as s:
            for it in items:
                try:
                    await get_or_write_card(s, it["item_type"], it["item_id"], gh, web)
                except CapReached:
                    log.warning("Token cap reached; remaining brief items keep their description")
                    break
                except Exception:
                    log.exception(
                        "Card for brief item %s %s failed", it["item_type"], it["item_id"]
                    )
                    await s.rollback()
    return len(items)


# ----------------------------------------------------------------- reading and rating


async def latest_daily_brief(session: AsyncSession) -> Brief | None:
    return await session.scalar(
        select(Brief).where(Brief.type == "daily").order_by(Brief.date.desc()).limit(1)
    )


async def mark_opened(session: AsyncSession, brief: Brief) -> None:
    """First view of a brief (REQ-BRF-004); later views keep the first time."""
    if brief.opened_at is None:
        brief.opened_at = datetime.now(UTC)
        await session.commit()


async def enrich_items(session: AsyncSession, brief: Brief) -> list[dict[str, Any]]:
    """Brief items + live card summary + current rating."""
    ratings = {
        (f.item_type, f.item_id): f.rating
        for f in await session.scalars(select(Feedback).where(Feedback.brief_id == brief.id))
    }
    out = []
    for it in brief.items or []:
        card = await latest_card(session, it["item_type"], it["item_id"])
        out.append(
            {
                **it,
                "what_it_is": card.content.get("what_it_is") if card else None,
                "has_card": card is not None,
                "rating": ratings.get((it["item_type"], it["item_id"])),
            }
        )
    return out


class NotInBrief(Exception):
    pass


async def set_rating(
    session: AsyncSession, brief_id: int, item_type: str, item_id: int, rating: int
) -> int | None:
    """Save 👍 (1) / 👎 (-1), or clear (0). The latest rating replaces any earlier one."""
    if rating not in (-1, 0, 1):
        raise ValueError("rating must be -1, 0 or 1")
    brief = await session.get(Brief, brief_id)
    if brief is None or not any(
        it["item_type"] == item_type and it["item_id"] == item_id for it in brief.items or []
    ):
        raise NotInBrief(f"{item_type} {item_id} is not in brief {brief_id}")
    await session.execute(
        delete(Feedback).where(
            Feedback.brief_id == brief_id,
            Feedback.item_type == item_type,
            Feedback.item_id == item_id,
        )
    )
    if rating:
        session.add(
            Feedback(item_type=item_type, item_id=item_id, rating=rating, brief_id=brief_id)
        )
    await session.commit()
    return rating or None
