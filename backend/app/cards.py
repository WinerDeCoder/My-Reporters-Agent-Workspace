"""LLM cards (spec 004): sources, cache, monthly token cap, writing cards.

A card answers four questions about a repo or story, written by the model from its README or
article text (Q-021), in English (Q-022). Cards are reused while the source text is unchanged
(REQ-CRD-003); no call is made once the month's tokens reach `llm.monthly_token_cap` (Q-023).
"""

import hashlib
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal
from zoneinfo import ZoneInfo

import httpx
import trafilatura
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import llm
from app.collectors import make_client
from app.config import AppConfig, get_config
from app.db import SessionLocal
from app.models import Card, LlmUsage, NewsItem, Repo
from app.news_feed import load_news_rows
from app.repo_stats import load_repo_rows, rank_by_score

log = logging.getLogger(__name__)

ItemType = Literal["repo", "news"]
MAX_ARTICLE_BYTES = 2_000_000
MIN_ARTICLE_CHARS = 200  # less than this is navigation/cookie text, not an article


class CardContent(BaseModel):
    """What the model writes. Signals (stars, points…) come from live data, not the model."""

    what_it_is: str = Field(description="One sentence, no jargon.")
    problem_it_solves: str = Field(description="Who has this pain and how they cope today.")
    whats_special: str = Field(description="The one idea that sets it apart.")
    worth_trying: str = Field(description="Effort to try it, maturity, license if known.")


@dataclass(frozen=True)
class Source:
    kind: Literal["readme", "article", "title"]
    text: str
    limited: bool  # True when only the title/description was available
    url: str | None = None


class CapReached(Exception):
    """The monthly token cap is used up; no LLM call was made."""


class ItemNotFound(Exception):
    pass


# ----------------------------------------------------------------- pure helpers


def truncate(text: str, max_chars: int) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars]
    space = cut.rfind(" ")
    return (cut[:space] if space > max_chars * 0.8 else cut).rstrip() + "\n…[truncated]"


def source_hash(source: Source) -> str:
    return hashlib.sha256(f"{source.kind}\n{source.text}".encode()).hexdigest()


def needs_new_card(existing_hash: str | None, new_hash: str, force: bool = False) -> bool:
    return force or existing_hash != new_hash


def month_start(now: datetime, tz: ZoneInfo) -> datetime:
    local = now.astimezone(tz)
    return local.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def within_cap(used_tokens: int, cap: int) -> bool:
    return cap > 0 and used_tokens < cap


def extract_article(html: str) -> str | None:
    """Main text of an article page, or None if nothing article-like was found."""
    text = trafilatura.extract(html, include_comments=False, include_tables=False) or ""
    text = text.strip()
    return text if len(text) >= MIN_ARTICLE_CHARS else None


def build_input(item_type: ItemType, title: str, url: str | None, source: Source) -> str:
    kind = {"readme": "README", "article": "Article text", "title": "Only this summary"}[
        source.kind
    ]
    header = [
        f"Item type: {'GitHub repository' if item_type == 'repo' else 'News story'}",
        f"Title: {title}",
    ]
    if url:
        header.append(f"URL: {url}")
    if source.limited:
        header.append("Source is LIMITED: only the title/description is available.")
    return "\n".join(header) + f"\n\n--- {kind} ---\n{source.text}"


# ----------------------------------------------------------------- fetching sources


async def fetch_readme(client: httpx.AsyncClient, full_name: str) -> str | None:
    resp = await client.get(
        f"/repos/{full_name}/readme", headers={"Accept": "application/vnd.github.raw"}
    )
    if resp.status_code != 200:
        return None
    return resp.content.decode("utf-8", errors="replace")


async def fetch_article(client: httpx.AsyncClient, url: str) -> str | None:
    try:
        resp = await client.get(url, timeout=15)
    except httpx.HTTPError as exc:
        log.info("Article fetch failed for %s: %s", url, exc)
        return None
    ctype = resp.headers.get("content-type", "")
    if resp.status_code != 200 or "html" not in ctype or len(resp.content) > MAX_ARTICLE_BYTES:
        log.info("Article not usable: %s (HTTP %d, %s)", url, resp.status_code, ctype)
        return None
    return extract_article(resp.text)


async def repo_source(gh: httpx.AsyncClient, repo: Repo, max_chars: int) -> Source:
    readme = await fetch_readme(gh, repo.full_name)
    if readme and readme.strip():
        return Source(
            "readme", truncate(readme, max_chars), False, f"https://github.com/{repo.full_name}"
        )
    summary = f"{repo.full_name}: {repo.description or 'no description'}"
    return Source("title", summary, True, f"https://github.com/{repo.full_name}")


async def news_source(
    gh: httpx.AsyncClient,
    web: httpx.AsyncClient,
    item: NewsItem,
    linked_repo: str | None,
    max_chars: int,
) -> Source:
    if linked_repo:  # GitHub-linked story: the README explains it best (Q-021)
        readme = await fetch_readme(gh, linked_repo)
        if readme and readme.strip():
            return Source("readme", truncate(readme, max_chars), False, item.url)
    if item.url:
        article = await fetch_article(web, item.url)
        if article:
            return Source("article", truncate(article, max_chars), False, item.url)
    return Source("title", item.title, True, item.url)


# ----------------------------------------------------------------- usage and cap


async def tokens_this_month(session: AsyncSession, cfg: AppConfig, now: datetime) -> int:
    since = month_start(now, ZoneInfo(cfg.timezone))
    total = await session.scalar(
        select(func.coalesce(func.sum(LlmUsage.input_tokens + LlmUsage.output_tokens), 0)).where(
            LlmUsage.at >= since
        )
    )
    return int(total or 0)


async def usage_summary(session: AsyncSession, cfg: AppConfig, now: datetime) -> dict[str, Any]:
    since = month_start(now, ZoneInfo(cfg.timezone))
    row = (
        await session.execute(
            select(
                func.count(LlmUsage.id),
                func.coalesce(func.sum(LlmUsage.input_tokens), 0),
                func.coalesce(func.sum(LlmUsage.output_tokens), 0),
            ).where(LlmUsage.at >= since)
        )
    ).one()
    calls, tokens_in, tokens_out = int(row[0]), int(row[1]), int(row[2])
    prices = cfg.llm.price_per_million
    usd = (
        tokens_in / 1e6 * prices.input + tokens_out / 1e6 * prices.output
        if prices.input is not None and prices.output is not None
        else None
    )
    return {
        "month_start": since,
        "calls": calls,
        "input_tokens": tokens_in,
        "output_tokens": tokens_out,
        "tokens": tokens_in + tokens_out,
        "cap": cfg.llm.monthly_token_cap,
        "estimated_usd": usd,
    }


def _usage_row(model: str, item_type: str, item_id: int, tin: int, tout: int, error: str | None):
    return LlmUsage(
        model=model,
        purpose="card",
        item_type=item_type,
        item_id=item_id,
        input_tokens=tin,
        output_tokens=tout,
        ok=error is None,
        error=error[:2000] if error else None,
    )


# ----------------------------------------------------------------- writing cards

Generate = Callable[[str, str, type[CardContent]], Awaitable[llm.LlmResult[CardContent]]]


async def latest_card(session: AsyncSession, item_type: str, item_id: int) -> Card | None:
    return await session.scalar(
        select(Card)
        .where(Card.item_type == item_type, Card.item_id == item_id)
        .order_by(Card.created_at.desc())
        .limit(1)
    )


async def get_or_write_card(
    session: AsyncSession,
    item_type: ItemType,
    item_id: int,
    gh: httpx.AsyncClient,
    web: httpx.AsyncClient,
    *,
    force: bool = False,
    generate: Generate = llm.generate,
) -> tuple[Card, bool]:
    """Return (card, written_now). Raises ItemNotFound, CapReached, or the LLM error."""
    cfg = get_config()
    max_chars = cfg.cards.max_source_chars
    if item_type == "repo":
        repo = await session.get(Repo, item_id)
        if repo is None:
            raise ItemNotFound(f"repo {item_id}")
        title, url = repo.full_name, f"https://github.com/{repo.full_name}"
        source = await repo_source(gh, repo, max_chars)
    else:
        item = await session.get(NewsItem, item_id)
        if item is None:
            raise ItemNotFound(f"news {item_id}")
        linked = await session.get(Repo, item.linked_repo_id) if item.linked_repo_id else None
        title, url = item.title, item.url
        source = await news_source(gh, web, item, linked.full_name if linked else None, max_chars)

    new_hash = source_hash(source)
    existing = await latest_card(session, item_type, item_id)
    if existing and not needs_new_card(existing.source_hash, new_hash, force):
        return existing, False

    used = await tokens_this_month(session, cfg, datetime.now(UTC))
    if not within_cap(used, cfg.llm.monthly_token_cap):
        raise CapReached(f"{used:,} of {cfg.llm.monthly_token_cap:,} tokens used this month")

    try:
        result = await generate(
            llm.load_prompt(), build_input(item_type, title, url, source), CardContent
        )
    except llm.LlmOutputError as exc:
        session.add(
            _usage_row(exc.model, item_type, item_id, exc.input_tokens, exc.output_tokens, str(exc))
        )
        await session.commit()
        raise
    except Exception as exc:
        session.add(
            _usage_row(cfg.llm.model, item_type, item_id, 0, 0, f"{type(exc).__name__}: {exc}")
        )
        await session.commit()
        raise

    session.add(
        _usage_row(
            result.model, item_type, item_id, result.input_tokens, result.output_tokens, None
        )
    )
    card = Card(
        item_type=item_type,
        item_id=item_id,
        content={
            **result.parsed.model_dump(),
            "source_kind": source.kind,
            "source_url": source.url,
            "limited": source.limited,
        },
        model=result.model,
        source_hash=new_hash,
    )
    session.add(card)
    await session.commit()
    await session.refresh(card)
    log.info(
        "Card written: %s %d (%s, %d+%d tokens)",
        item_type,
        item_id,
        source.kind,
        result.input_tokens,
        result.output_tokens,
    )
    return card, True


async def write_daily_cards(generate: Generate = llm.generate) -> int:
    """Cards for the brief's top repos and AI/dev stories (Q-020). Returns cards written now."""
    cfg = get_config()
    async with SessionLocal() as session:
        repos = rank_by_score(await load_repo_rows(session, cfg.sources.github_api.track_days))
        news = await load_news_rows(session)
    targets: list[tuple[ItemType, int, str]] = [
        ("repo", r.id, r.full_name) for r in repos if r.score is not None
    ][: cfg.brief.top_repos] + [("news", n.id, n.title) for n in news if n.score is not None][
        : cfg.brief.top_news
    ]

    written = 0
    async with make_client(github_api=True) as gh, make_client() as web, SessionLocal() as session:
        for item_type, item_id, label in targets:
            try:
                _, new = await get_or_write_card(
                    session, item_type, item_id, gh, web, generate=generate
                )
                written += new
            except CapReached as exc:
                log.warning("Monthly token cap reached (%s); stopping card generation", exc)
                break
            except Exception:
                log.exception("Card failed for %s %d (%s)", item_type, item_id, label)
                await session.rollback()
    log.info("Daily cards: %d written, %d targets", written, len(targets))
    return written
