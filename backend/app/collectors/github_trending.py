"""GitHub Trending collector: every listed repo becomes (or stays) a candidate. REQ-COL-001."""

import logging

import httpx
from selectolax.lexbor import LexborHTMLParser
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.collectors import make_client, transient_retry
from app.config import TrendingConfig, get_config
from app.db import SessionLocal
from app.models import Repo

log = logging.getLogger(__name__)

TRENDING_BASE = "https://github.com/trending"


def trending_urls(cfg: TrendingConfig) -> list[str]:
    """One URL per configured language x range; language "" means all languages."""
    urls = []
    for language in cfg.languages:
        path = f"{TRENDING_BASE}/{language}" if language else TRENDING_BASE
        urls += [f"{path}?since={since}" for since in cfg.ranges]
    return urls


def parse_trending(html: str) -> list[str]:
    """Return lowercased `owner/repo` names in page order, without duplicates."""
    names = []
    for link in LexborHTMLParser(html).css("article.Box-row h2 a"):
        href = (link.attributes.get("href") or "").strip("/")
        if href.count("/") == 1:
            names.append(href.lower())
    return list(dict.fromkeys(names))


@transient_retry
async def fetch_page(client: httpx.AsyncClient, url: str) -> str:
    resp = await client.get(url)
    resp.raise_for_status()
    return resp.text


async def upsert_candidates(session: AsyncSession, names: list[str]) -> None:
    if not names:
        return
    stmt = pg_insert(Repo).values([{"full_name": name} for name in names])
    stmt = stmt.on_conflict_do_update(
        index_elements=[Repo.full_name], set_={"last_seen": func.now()}
    )
    await session.execute(stmt)
    await session.commit()


async def collect_trending(session_factory: async_sessionmaker = SessionLocal) -> int:
    """Scrape every configured Trending page and upsert the repos. Returns the unique count."""
    found: list[str] = []
    async with make_client() as client:
        for url in trending_urls(get_config().sources.github_trending):
            try:
                names = parse_trending(await fetch_page(client, url))
            except httpx.HTTPError as exc:
                log.warning("Trending page failed: %s (%s)", url, exc)
                continue
            if not names:
                log.warning("No repos parsed from %s; has the page layout changed?", url)
            log.info("Trending %s: %d repos", url, len(names))
            found += names

    unique = list(dict.fromkeys(found))
    async with session_factory() as session:
        await upsert_candidates(session, unique)
    log.info("Trending: %d unique repos upserted", len(unique))
    return len(unique)
