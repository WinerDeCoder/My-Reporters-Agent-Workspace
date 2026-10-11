"""TC-003-01..05: topic matching, boost, scores, penalties, saved-fixture check."""

import json
from pathlib import Path

import pytest

from app.config import AppConfig, InterestsConfig, ScoringConfig, get_config
from app.news_feed import domain_of
from app.scoring import (
    Signals,
    TopicMatcher,
    ai_dev_matcher,
    boost,
    news_text,
    normalize,
    repo_text,
    score_item,
    topic_matcher,
)

FIXTURES = Path(__file__).parent / "fixtures"

CFG = AppConfig(
    interests=InterestsConfig(
        topic_boost=1.5,
        max_boost=3.0,
        topics={
            "agents": ["agent", "agents", "multi agent"],
            "mcp": ["mcp", "model context protocol"],
            "claude": ["claude"],
            "skills": ["agent skills", "~skills"],
        },
    ),
    scoring=ScoringConfig(repeat_penalty=0.3, dislike_penalty=0.7, dislike_floor=0.2),
)
M = TopicMatcher(CFG.interests.topics)


def test_normalize():
    assert normalize("GPT-5 / Multi_Agent") == "gpt 5 multi agent"
    assert normalize("from my .agents directory.") == "from my agents directory"
    assert normalize("SKILL.md and node.js") == "skill.md and node.js"


def test_matcher_whole_word_and_case():
    assert M.match("An MCP server for Claude") == {"mcp", "claude"}
    assert M.match("Agentic workflows") == set()  # "agentic" isn't a term here
    assert M.match("reagent chemistry") == set()  # no partial words


def test_matcher_multi_word_and_separators():
    assert M.match("A multi-agent framework") == {"agents"}
    assert M.match("Model Context Protocol explained") == {"mcp"}
    assert M.match("owner/claude_tools") == {"claude"}


def test_matcher_weak_terms_need_another_topic():
    assert M.match("Improve your coding skills") == set()
    assert M.match("Skills for your Claude setup") == {"skills", "claude"}
    assert M.match("agent skills collection") == {"skills", "agents"}  # strong term


def test_real_config_matches_user_examples():
    cfg = get_config()
    m = topic_matcher(cfg)
    skills = repo_text(
        "mattpocock/skills", "Skills for Real Engineers. Straight from my .agents directory.", []
    )
    assert m.match(skills) == {"skills", "agents"}
    assert "new llm models" in m.match("Qwen 3.5 open weights released")
    assert "new llm models" in m.match("GPT-5.1 is out")
    assert m.match("Improve your soft skills at work") == set()


def test_boost():
    assert boost(0, 1.5, 3.0) == 1.0
    assert boost(1, 1.5, 3.0) == 1.5
    assert boost(2, 1.5, 3.0) == 2.25
    assert boost(3, 1.5, 3.0) == 3.0  # 3.375 capped


def test_score_repo_formula():
    s = score_item(200.0, {"agents", "mcp"}, ("repo", 1), Signals(), CFG)
    assert s is not None
    assert s.score == pytest.approx(200 * 2.25)
    assert (s.base, s.topics, s.boost, s.repeat, s.dislike) == (
        200.0,
        ("agents", "mcp"),
        2.25,
        1.0,
        1.0,
    )


def test_score_unscored_cases():
    assert score_item(None, {"agents"}, ("repo", 1), Signals(), CFG) is None  # no stars/day yet
    assert (
        score_item(50.0, set(), ("news", 1), Signals(), CFG, eligible=False) is None
    )  # not AI/dev
    lost = score_item(-30.0, set(), ("repo", 1), Signals(), CFG)
    assert lost is not None and lost.score == 0.0  # losing stars never goes negative


def test_penalties():
    briefed = Signals(briefed=frozenset({("repo", 7)}))
    assert score_item(100.0, set(), ("repo", 7), briefed, CFG).score == pytest.approx(30)
    assert score_item(100.0, set(), ("news", 7), briefed, CFG).score == pytest.approx(100)

    disliked = Signals(disliked_topics=frozenset({"agents", "mcp", "claude", "skills"}))
    one = score_item(100.0, {"agents"}, ("repo", 1), disliked, CFG)
    assert one.dislike == pytest.approx(0.7) and one.score == pytest.approx(100 * 1.5 * 0.7)
    many = score_item(100.0, {"agents", "mcp", "claude", "skills"}, ("repo", 1), disliked, CFG)
    assert many.dislike == pytest.approx(0.7**4)  # 0.2401: still above the 0.2 floor

    floored_cfg = CFG.model_copy(
        update={"scoring": ScoringConfig(dislike_penalty=0.7, dislike_floor=0.3)}
    )
    floored = score_item(
        100.0, {"agents", "mcp", "claude", "skills"}, ("repo", 1), disliked, floored_cfg
    )
    assert floored.dislike == pytest.approx(0.3)  # 0.2401 floored at 0.3


def test_saved_front_page_ai_dev():
    cfg = get_config()
    tm, am = topic_matcher(cfg), ai_dev_matcher(cfg)
    hits = {
        h["objectID"]: h
        for h in json.loads((FIXTURES / "hn_front_page.json").read_text("utf-8"))["hits"]
    }

    def classify(hn_id: str) -> tuple[set[str], bool]:
        h = hits[hn_id]
        text = news_text(h["title"], domain_of(h.get("url")))
        topics = tm.match(text)
        return topics, bool(topics) or bool(am.match(text))

    assert classify("50039633") == ({"agents", "mcp"}, True)  # MCP server for AI agents
    assert classify("50031614") == ({"agents"}, True)  # self-hosted personal AI agent
    assert classify("50017247")[1]  # "Nix wrote half of my debugger"
    for off_topic in ("50039715", "50029830", "50036864"):  # vegetables, food, city game
        assert classify(off_topic) == (set(), False), hits[off_topic]["title"]
