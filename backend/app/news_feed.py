"""Recent HN stories with points/hour, topics and score. Used by the API and the CLI."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from urllib.parse import urlparse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_config
from app.models import NewsItem, Repo
from app.news_stats import points_per_hour
from app.scoring import ai_dev_matcher, load_signals, news_text, score_item, topic_matcher


@dataclass
class NewsRow:
    id: int
    hn_id: int
    title: str
    url: str | None
    domain: str | None
    hn_url: str
    points: int
    comments: int
    posted_at: datetime
    points_per_hour: float
    linked_repo: str | None
    matched_topics: list[str]
    ai_dev: bool
    score: float | None


def domain_of(url: str | None) -> str | None:
    host = urlparse(url).hostname if url else None
    return host.removeprefix("www.") if host else None


async def load_news_rows(session: AsyncSession, days: int = 7) -> list[NewsRow]:
    """Stories posted in the last `days` days, "For you" order: score first, then points/hour."""
    cfg = get_config()
    now = datetime.now(UTC)
    topics_of, ai_dev_of = topic_matcher(cfg), ai_dev_matcher(cfg)
    signals = await load_signals(session, cfg, now)
    result = await session.execute(
        select(NewsItem, Repo.full_name)
        .outerjoin(Repo, Repo.id == NewsItem.linked_repo_id)
        .where(NewsItem.posted_at >= now - timedelta(days=days))
    )
    rows = []
    for item, repo_name in result:
        domain = domain_of(item.url)
        text = news_text(item.title, domain)
        topics = topics_of.match(text)
        ai_dev = bool(topics) or bool(ai_dev_of.match(text))  # Q-016
        pph = points_per_hour(item.points, item.posted_at, now)
        scored = score_item(pph, topics, ("news", item.id), signals, cfg, eligible=ai_dev)
        rows.append(
            NewsRow(
                id=item.id,
                hn_id=item.hn_id,
                title=item.title,
                url=item.url,
                domain=domain,
                hn_url=f"https://news.ycombinator.com/item?id={item.hn_id}",
                points=item.points,
                comments=item.comments,
                posted_at=item.posted_at,
                points_per_hour=pph,
                linked_repo=repo_name,
                matched_topics=sorted(topics),
                ai_dev=ai_dev,
                score=scored.score if scored else None,
            )
        )
    return sorted(rows, key=lambda r: (r.score is None, -(r.score or 0), -r.points_per_hour))
