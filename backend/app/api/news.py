from datetime import UTC, datetime, timedelta
from typing import Annotated
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import NewsItem, Repo
from app.news_stats import points_per_hour

router = APIRouter(tags=["news"])


class NewsOut(BaseModel):
    id: int
    hn_id: int
    title: str
    url: str | None  # null for Ask HN / text posts
    domain: str | None
    hn_url: str
    points: int
    comments: int
    posted_at: datetime
    points_per_hour: float
    linked_repo: str | None  # owner/repo when the story links a GitHub repo


def domain_of(url: str | None) -> str | None:
    host = urlparse(url).hostname if url else None
    return host.removeprefix("www.") if host else None


@router.get("/news")
async def list_news(
    session: Annotated[AsyncSession, Depends(get_session)],
    days: Annotated[int, Query(ge=1, le=30)] = 7,
) -> list[NewsOut]:
    """HN stories posted in the last `days` days, highest points/hour first."""
    now = datetime.now(UTC)
    rows = await session.execute(
        select(NewsItem, Repo.full_name)
        .outerjoin(Repo, Repo.id == NewsItem.linked_repo_id)
        .where(NewsItem.posted_at >= now - timedelta(days=days))
    )
    items = [
        NewsOut(
            id=item.id,
            hn_id=item.hn_id,
            title=item.title,
            url=item.url,
            domain=domain_of(item.url),
            hn_url=f"https://news.ycombinator.com/item?id={item.hn_id}",
            points=item.points,
            comments=item.comments,
            posted_at=item.posted_at,
            points_per_hour=points_per_hour(item.points, item.posted_at, now),
            linked_repo=repo_name,
        )
        for item, repo_name in rows
    ]
    return sorted(items, key=lambda n: n.points_per_hour, reverse=True)
