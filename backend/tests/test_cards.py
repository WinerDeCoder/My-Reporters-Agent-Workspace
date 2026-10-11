"""TC-004-01..04: truncation, hashing, article extraction, cache decision, token cap."""

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from app.cards import (
    Source,
    build_input,
    extract_article,
    month_start,
    needs_new_card,
    source_hash,
    truncate,
    within_cap,
)

ARTICLE = (
    "<html><head><title>Agents decompile a game</title></head><body>"
    "<nav>Home | About | Login</nav>"
    "<article><h1>500B tokens later</h1>"
    + "".join(
        f"<p>Paragraph {i}: we let AI agents decompile a first-person shooter, "
        "tracking every function they recovered and every dead end they hit.</p>"
        for i in range(8)
    )
    + "</article><footer>Cookie settings · Privacy</footer></body></html>"
)


def test_truncate_and_hash():
    assert truncate("short text", 100) == "short text"
    long = "word " * 100
    cut = truncate(long, 50)
    assert cut.endswith("…[truncated]") and len(cut) <= 50 + len("\n…[truncated]")
    a = Source("readme", "same text", False)
    assert source_hash(a) == source_hash(Source("readme", "same text", False))
    assert source_hash(a) != source_hash(Source("readme", "other text", False))
    assert source_hash(a) != source_hash(Source("article", "same text", False))


def test_extract_article_from_html():
    text = extract_article(ARTICLE)
    assert text is not None
    assert "decompile a first-person shooter" in text
    assert "Cookie settings" not in text and "Login" not in text


def test_extract_article_returns_none_for_non_articles():
    assert extract_article("<html><body><nav>Home</nav><p>Sign in</p></body></html>") is None
    assert extract_article("") is None


def test_needs_new_card():
    assert needs_new_card(None, "h1")  # no card yet
    assert not needs_new_card("h1", "h1")  # unchanged source -> reuse, no LLM call
    assert needs_new_card("h1", "h2")  # source changed
    assert needs_new_card("h1", "h1", force=True)


def test_within_cap():
    assert within_cap(0, 3_000_000)
    assert within_cap(2_999_999, 3_000_000)
    assert not within_cap(3_000_000, 3_000_000)
    assert not within_cap(0, 0)  # cap 0 disables all calls


def test_month_start_uses_local_timezone():
    tz = ZoneInfo("Asia/Ho_Chi_Minh")  # UTC+7
    # 2026-10-31 20:00 UTC is already 2026-11-01 03:00 local -> November
    start = month_start(datetime(2026, 10, 31, 20, 0, tzinfo=UTC), tz)
    assert (start.year, start.month, start.day, start.hour) == (2026, 11, 1, 0)
    assert start.utcoffset().total_seconds() == 7 * 3600


def test_build_input_marks_limited_sources():
    text = build_input(
        "news", "Some headline", "https://x.com/a", Source("title", "Some headline", True)
    )
    assert "LIMITED" in text and "Title: Some headline" in text and "News story" in text
    full = build_input("repo", "a/b", None, Source("readme", "# Readme", False))
    assert "LIMITED" not in full and "--- README ---" in full
