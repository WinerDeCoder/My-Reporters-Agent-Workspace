"""Scoring (spec 003): interest-topic matching and item scores. REQ-SCO-001..003.

repo score = stars/day     x topic boost x repeat penalty x dislike penalty
news score = points/hour   x topic boost x repeat penalty x dislike penalty  (AI/dev stories only)

Everything here except `load_signals` is pure: no DB, no clock.
"""

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import AppConfig
from app.models import Brief, Feedback, NewsItem, Repo

# "." only survives between letters/digits (skill.md, node.js, gpt-4.1), not at word edges
_EDGE_DOTS = re.compile(r"(?<![a-z0-9])\.|\.(?![a-z0-9])")
_NON_WORD = re.compile(r"[^a-z0-9+#.]+")


def normalize(text: str) -> str:
    """Lowercase; everything except letters, digits, + # and inner dots becomes a space."""
    return _NON_WORD.sub(" ", _EDGE_DOTS.sub(" ", text.lower())).strip()


class TopicMatcher:
    """Whole-word, case-insensitive topic matching. Terms starting with "~" are weak: they only
    count when a different topic matched through a normal term (Q-015)."""

    def __init__(self, topics: Mapping[str, Iterable[str]]):
        self._strong: dict[str, list[str]] = {}
        self._weak: dict[str, list[str]] = {}
        for topic, terms in topics.items():
            for term in terms:
                weak = term.startswith("~")
                norm = normalize(term[1:] if weak else term)
                if norm:
                    (self._weak if weak else self._strong).setdefault(topic, []).append(norm)

    def match(self, text: str) -> set[str]:
        hay = f" {normalize(text)} "
        strong = {
            topic
            for topic, terms in self._strong.items()
            if any(f" {term} " in hay for term in terms)
        }
        weak = {
            topic
            for topic, terms in self._weak.items()
            if topic not in strong
            and strong - {topic}
            and any(f" {term} " in hay for term in terms)
        }
        return strong | weak


def topic_matcher(cfg: AppConfig) -> TopicMatcher:
    return TopicMatcher(cfg.interests.topics)


def ai_dev_matcher(cfg: AppConfig) -> TopicMatcher:
    return TopicMatcher({"ai_dev": cfg.interests.ai_dev_terms})


def repo_text(full_name: str, description: str | None, topics: Iterable[str]) -> str:
    return " ".join([full_name, description or "", *topics])


def news_text(title: str, domain: str | None) -> str:
    return f"{title} {(domain or '').replace('.', ' ')}"


def boost(n_topics: int, topic_boost: float, max_boost: float) -> float:
    return min(topic_boost**n_topics, max_boost) if n_topics else 1.0


@dataclass(frozen=True)
class Signals:
    """Penalty inputs: items briefed recently, and topics of items given 👎 recently."""

    briefed: frozenset[tuple[str, int]] = frozenset()  # (item_type, item_id)
    disliked_topics: frozenset[str] = frozenset()


@dataclass(frozen=True)
class Score:
    score: float
    base: float
    topics: tuple[str, ...] = field(default_factory=tuple)
    boost: float = 1.0
    repeat: float = 1.0  # 1.0 = no penalty
    dislike: float = 1.0


def score_item(
    base: float | None,
    topics: set[str],
    item: tuple[str, int],
    signals: Signals,
    cfg: AppConfig,
    eligible: bool = True,
) -> Score | None:
    """None when there is nothing to rank on yet (no stars/day) or the item isn't eligible."""
    if base is None or not eligible:
        return None
    b = boost(len(topics), cfg.interests.topic_boost, cfg.interests.max_boost)
    repeat = cfg.scoring.repeat_penalty if item in signals.briefed else 1.0
    shared = len(topics & signals.disliked_topics)
    dislike = max(cfg.scoring.dislike_penalty**shared, cfg.scoring.dislike_floor) if shared else 1.0
    base = max(base, 0.0)
    return Score(base * b * repeat * dislike, base, tuple(sorted(topics)), b, repeat, dislike)


async def load_signals(session: AsyncSession, cfg: AppConfig, now: datetime) -> Signals:
    """Recently briefed items and disliked topics. Empty until briefs/feedback exist (spec 005).
    Convention: each `briefs.items` entry has `item_type` and `item_id`."""
    since_day: date = now.date() - timedelta(days=cfg.brief.repeat_cooldown_days)
    briefed: set[tuple[str, int]] = set()
    for items in await session.scalars(select(Brief.items).where(Brief.date >= since_day)):
        for it in items or []:
            if isinstance(it, dict) and "item_type" in it and "item_id" in it:
                briefed.add((str(it["item_type"]), int(it["item_id"])))

    disliked = await session.execute(
        select(Feedback.item_type, Feedback.item_id).where(
            Feedback.rating == -1,
            Feedback.rated_at >= now - timedelta(days=cfg.scoring.dislike_days),
        )
    )
    repo_ids, news_ids = set(), set()
    for item_type, item_id in disliked:
        (repo_ids if item_type == "repo" else news_ids).add(item_id)

    matcher = topic_matcher(cfg)
    topics: set[str] = set()
    if repo_ids:
        for r in await session.scalars(select(Repo).where(Repo.id.in_(repo_ids))):
            topics |= matcher.match(repo_text(r.full_name, r.description, r.topics or []))
    if news_ids:
        for n in await session.scalars(select(NewsItem).where(NewsItem.id.in_(news_ids))):
            topics |= matcher.match(news_text(n.title, None))
    return Signals(frozenset(briefed), frozenset(topics))
