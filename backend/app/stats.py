"""Stats for the 2-week trial (spec 007): did I open the brief, and were items useful?

Thresholds (Q-028) and the trial window (Q-029) come from `config.yaml` → `trial`.
"""

from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from typing import Any, Literal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import TrialConfig
from app.models import Brief, Feedback

CheckState = Literal["pass", "fail", "not yet", "on track", "below", "no data"]


@dataclass
class DayRow:
    day: date
    built: bool
    opened_at: datetime | None
    items: int
    rated: int
    up: int
    down: int


async def day_rows(session: AsyncSession, start: date, days: int) -> list[DayRow]:
    """One row per date in [start, start + days); daily briefs only."""
    end = start + timedelta(days=days - 1)
    briefs = list(
        await session.scalars(
            select(Brief).where(Brief.type == "daily", Brief.date >= start, Brief.date <= end)
        )
    )
    votes: dict[int, tuple[int, int]] = {}
    if briefs:
        result = await session.execute(
            select(
                Feedback.brief_id,
                func.count().filter(Feedback.rating == 1),
                func.count().filter(Feedback.rating == -1),
            )
            .where(Feedback.brief_id.in_([b.id for b in briefs]))
            .group_by(Feedback.brief_id)
        )
        votes = {brief_id: (int(up), int(down)) for brief_id, up, down in result}
    by_day = {b.date: b for b in briefs}
    rows = []
    for i in range(days):
        d = start + timedelta(days=i)
        b = by_day.get(d)
        up, down = votes.get(b.id, (0, 0)) if b else (0, 0)
        rows.append(
            DayRow(d, b is not None, b.opened_at if b else None, len(b.items or []) if b else 0,
                   up + down, up, down)
        )  # fmt: skip
    return rows


def _share_state(share: float | None, threshold: float, finished: bool) -> CheckState:
    if share is None:
        return "fail" if finished else "no data"
    if finished:
        return "pass" if share >= threshold else "fail"
    return "on track" if share >= threshold else "below"


def summarize(
    rows: Sequence[DayRow], today: date, trial: TrialConfig, finished_matters: bool = True
) -> dict[str, Any]:
    """Totals, shares, check states and (after the last day) the verdict. Pure."""
    if not rows:
        raise ValueError("no days")
    start, end = rows[0].day, rows[-1].day
    elapsed = [r for r in rows if r.day <= today]
    finished = finished_matters and today > end
    opened_days = sum(1 for r in rows if r.opened_at is not None)
    items = sum(r.items for r in rows)
    rated = sum(r.rated for r in rows)
    up = sum(r.up for r in rows)
    down = sum(r.down for r in rows)
    up_share = up / rated if rated else None
    rated_share = rated / items if items else None

    # opened days: fail only once the minimum can't be reached in the remaining days
    still_possible = opened_days + sum(1 for r in rows if r.day >= today and r.opened_at is None)
    if opened_days >= trial.min_opened_days:
        opened_state: CheckState = "pass"
    elif finished or still_possible < trial.min_opened_days:
        opened_state = "fail"
    else:
        opened_state = "not yet"

    checks = {
        "opened_days": {
            "label": f"Brief opened on ≥ {trial.min_opened_days} of {len(rows)} days",
            "value": opened_days,
            "target": trial.min_opened_days,
            "state": opened_state,
        },
        "thumbs_up_share": {
            "label": f"≥ {trial.min_thumbs_up_share:.0%} of rated items 👍",
            "value": up_share,
            "target": trial.min_thumbs_up_share,
            "state": _share_state(up_share, trial.min_thumbs_up_share, finished),
        },
        "rated_share": {
            "label": f"≥ {trial.min_rated_share:.0%} of brief items rated",
            "value": rated_share,
            "target": trial.min_rated_share,
            "state": _share_state(rated_share, trial.min_rated_share, finished),
        },
    }
    verdict = None
    if finished:
        verdict = (
            "continue"  # all criteria met: the v1 requirements become the roadmap
            if all(c["state"] == "pass" for c in checks.values())
            else "fix scoring and cards first"
        )
    return {
        "start": start,
        "end": end,
        "today": today,
        "days": len(rows),
        "day_number": min(max((today - start).days + 1, 0), len(rows)),
        "not_started": today < start,
        "finished": finished,
        "briefs_built": sum(1 for r in elapsed if r.built),
        "opened_days": opened_days,
        "items": items,
        "rated": rated,
        "up": up,
        "down": down,
        "up_share": up_share,
        "rated_share": rated_share,
        "checks": checks,
        "verdict": verdict,
        "rows": [asdict(r) for r in rows],
    }
