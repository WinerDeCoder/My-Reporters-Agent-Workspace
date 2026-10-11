"""Card endpoints (spec 004): read a card with its item's live signals, or write one on demand."""

from datetime import UTC, datetime
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.cards import CapReached, ItemNotFound, get_or_write_card, latest_card, usage_summary
from app.collectors import make_client
from app.config import get_config
from app.db import get_session
from app.news_feed import load_news_rows
from app.repo_stats import load_repo_rows

router = APIRouter(tags=["cards"])

ItemType = Literal["repo", "news"]


class CardItem(BaseModel):
    """The item a card is about, with live signals (not written by the model)."""

    item_type: ItemType
    item_id: int
    title: str
    url: str | None
    description: str | None = None
    language: str | None = None
    stars: int | None = None
    stars_per_day: float | None = None
    points: int | None = None
    comments: int | None = None
    points_per_hour: float | None = None
    hn_url: str | None = None
    linked_repo: str | None = None
    matched_topics: list[str] = []
    score: float | None = None


class CardOut(BaseModel):
    what_it_is: str
    problem_it_solves: str
    whats_special: str
    worth_trying: str
    source_kind: str  # readme | article | title
    source_url: str | None
    limited: bool
    model: str
    created_at: datetime


class CardView(BaseModel):
    item: CardItem
    card: CardOut | None  # null until written


class LlmUsageOut(BaseModel):
    month_start: datetime
    calls: int
    input_tokens: int
    output_tokens: int
    tokens: int
    cap: int
    estimated_usd: float | None


async def _item(session: AsyncSession, item_type: ItemType, item_id: int) -> CardItem:
    if item_type == "repo":
        rows = await load_repo_rows(session, get_config().sources.github_api.track_days)
        row = next((r for r in rows if r.id == item_id), None)
        if row:
            return CardItem(
                item_type="repo", item_id=row.id, title=row.full_name, url=row.url,
                description=row.description, language=row.language, stars=row.stars,
                stars_per_day=row.stars_per_day, matched_topics=row.matched_topics, score=row.score,
            )  # fmt: skip
    else:
        news = await load_news_rows(session, days=30)
        n = next((x for x in news if x.id == item_id), None)
        if n:
            return CardItem(
                item_type="news", item_id=n.id, title=n.title, url=n.url, points=n.points,
                comments=n.comments, points_per_hour=n.points_per_hour, hn_url=n.hn_url,
                linked_repo=n.linked_repo, matched_topics=n.matched_topics, score=n.score,
            )  # fmt: skip
    raise HTTPException(404, f"No tracked {item_type} with id {item_id}")


def _card_out(card: Any) -> CardOut:
    c = card.content
    return CardOut(
        what_it_is=c.get("what_it_is", ""),
        problem_it_solves=c.get("problem_it_solves", ""),
        whats_special=c.get("whats_special", ""),
        worth_trying=c.get("worth_trying", ""),
        source_kind=c.get("source_kind", "title"),
        source_url=c.get("source_url"),
        limited=bool(c.get("limited", False)),
        model=card.model,
        created_at=card.created_at,
    )


@router.get("/cards/{item_type}/{item_id}")
async def get_card(
    item_type: ItemType, item_id: int, session: Annotated[AsyncSession, Depends(get_session)]
) -> CardView:
    item = await _item(session, item_type, item_id)
    card = await latest_card(session, item_type, item_id)
    return CardView(item=item, card=_card_out(card) if card else None)


@router.post("/cards/{item_type}/{item_id}")
async def write_card(
    item_type: ItemType, item_id: int, session: Annotated[AsyncSession, Depends(get_session)]
) -> CardView:
    """Write the card now (REQ-UI-005); reuses the cached card if the source is unchanged."""
    item = await _item(session, item_type, item_id)
    try:
        async with make_client(github_api=True) as gh, make_client() as web:
            card, _ = await get_or_write_card(session, item_type, item_id, gh, web)
    except ItemNotFound as exc:
        raise HTTPException(404, str(exc)) from exc
    except CapReached as exc:
        raise HTTPException(429, f"Monthly LLM token cap reached: {exc}") from exc
    except Exception as exc:
        raise HTTPException(502, f"Card generation failed: {type(exc).__name__}: {exc}") from exc
    return CardView(item=item, card=_card_out(card))


@router.get("/llm/usage")
async def llm_usage(session: Annotated[AsyncSession, Depends(get_session)]) -> LlmUsageOut:
    """Tokens used this calendar month vs the cap (Q-023)."""
    return LlmUsageOut(**await usage_summary(session, get_config(), datetime.now(UTC)))
