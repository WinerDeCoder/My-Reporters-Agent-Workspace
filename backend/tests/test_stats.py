"""TC-007-01..02: trial totals, shares, check states, verdict."""

from datetime import UTC, date, datetime, timedelta

from app.config import TrialConfig
from app.stats import DayRow, summarize

TRIAL = TrialConfig(start_date=date(2026, 10, 12), days=14, min_opened_days=10,
                    min_thumbs_up_share=0.6, min_rated_share=0.5)  # fmt: skip
START = TRIAL.start_date
OPENED = datetime(2026, 10, 12, 1, 0, tzinfo=UTC)


def rows(days_opened: int, up: int = 5, down: int = 1, rated: int | None = None, total: int = 14):
    out = []
    for i in range(total):
        d = START + timedelta(days=i)
        opened = i < days_opened
        r = (up + down) if rated is None else rated
        out.append(DayRow(d, True, OPENED if opened else None, 8, r if opened else 0,
                          up if opened else 0, down if opened else 0))  # fmt: skip
    return out


def test_summarize_totals_and_shares():
    s = summarize(rows(10), today=START + timedelta(days=20), trial=TRIAL)
    assert (s["opened_days"], s["items"], s["rated"], s["up"], s["down"]) == (10, 112, 60, 50, 10)
    assert abs(s["up_share"] - 50 / 60) < 1e-9 and abs(s["rated_share"] - 60 / 112) < 1e-9
    assert s["day_number"] == 14 and s["finished"] and s["briefs_built"] == 14


def test_summarize_empty_window_mid_trial():
    empty = [DayRow(START + timedelta(days=i), False, None, 0, 0, 0, 0) for i in range(14)]
    s = summarize(empty, today=START + timedelta(days=2), trial=TRIAL)
    assert s["up_share"] is None and s["rated_share"] is None
    assert s["checks"]["thumbs_up_share"]["state"] == "no data"
    assert s["checks"]["opened_days"]["state"] == "not yet" and s["verdict"] is None


def test_checks_pass_and_verdict_continue():
    s = summarize(rows(11), today=START + timedelta(days=14), trial=TRIAL)
    assert {k: c["state"] for k, c in s["checks"].items()} == {
        "opened_days": "pass", "thumbs_up_share": "pass", "rated_share": "pass",
    }  # fmt: skip
    assert s["verdict"] == "continue"


def test_checks_fail_and_verdict_fix():
    s = summarize(rows(8, up=2, down=4), today=START + timedelta(days=15), trial=TRIAL)
    assert s["checks"]["opened_days"]["state"] == "fail"
    assert s["checks"]["thumbs_up_share"]["state"] == "fail"
    assert s["verdict"] == "fix scoring and cards first"


def test_checks_opened_days_unreachable_mid_trial():
    # day 10, only 3 opened so far: 3 + 5 remaining days (incl. today) < 10 -> already failed
    r = rows(3)
    s = summarize(r, today=START + timedelta(days=9), trial=TRIAL)
    assert s["checks"]["opened_days"]["state"] == "fail" and s["verdict"] is None


def test_checks_mid_trial_on_track_or_below():
    s = summarize(rows(4, up=5, down=1), today=START + timedelta(days=3), trial=TRIAL)
    assert s["checks"]["thumbs_up_share"]["state"] == "on track"
    assert s["checks"]["opened_days"]["state"] == "not yet"
    low = summarize(rows(4, up=1, down=5), today=START + timedelta(days=3), trial=TRIAL)
    assert low["checks"]["thumbs_up_share"]["state"] == "below"


def test_not_started():
    s = summarize(rows(0), today=START - timedelta(days=1), trial=TRIAL)
    assert s["not_started"] and s["day_number"] == 0
