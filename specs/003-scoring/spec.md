---
id: 003
title: Scoring
status: in-progress
version: 1.0
requirements: [REQ-SCO-001, REQ-SCO-002, REQ-SCO-003, REQ-UI-004]
target_release: 0.4.0
created: 2026-10-11
updated: 2026-10-11
---

# 003 — Scoring

## Why

The collectors gather ~70 repos and ~40 stories a day; the brief shows about 8. Scoring decides which ones, using momentum plus my interests, so the brief feels personal and the success check ("most items get a thumbs up") has a chance. It must be simple, explainable, and tunable from `config.yaml`.

## What (behavior)

1. **Interest topics** (Q-005, Q-015) in `config.yaml` → `interests.topics`: agents, mcp, claude, skills, new llm models, each with a list of match terms. Matching is case-insensitive and whole-word (hyphens, slashes and underscores count as spaces). A term starting with `~` is *weak*: it only counts when another topic also matched (so "skills" alone doesn't match "improve your coding skills", but `mattpocock/skills` "…from my .agents directory" matches skills + agents).
2. **Repo score** (REQ-SCO-001) = stars/day × topic boost × penalties. Topic boost = 1.5 per matched topic, capped at 3.0. Repos without stars/day yet have no score.
3. **News score** (REQ-SCO-002) = points/hour × topic boost × penalties, only for stories that are **AI/dev**: the title matches a term in `interests.ai_dev_terms` or any interest topic (Q-016). Other stories get no score.
4. **Penalties:** ×0.3 if the item was in a brief within `repeat_cooldown_days` (no-op until briefs exist, spec 005); ×0.7 for each topic shared with an item I gave 👎 in the last 30 days, floored at ×0.2 (REQ-SCO-003; no-op until feedback exists, spec 005).
5. **UI** (Q-017, REQ-UI-004): Rising repos and News default to a **"For you"** sort by score; matched topics show as badges; News has an **"AI/dev only"** toggle (on by default).
6. **CLI** `uv run python -m app.cli top` prints today's top repos and stories with the score parts, for an eyeball check.

## Acceptance criteria

- [x] AC-1: Topic matching is whole-word and case-insensitive, handles multi-word terms and `-`/`/`/`_`, and weak terms only count with another topic.
- [x] AC-2: Repo score follows the formula; boost caps at 3.0; repos without stars/day are unscored and sort last.
- [x] AC-3: Only AI/dev stories get a news score; score = points/hour × boost × penalties.
- [x] AC-4: Repeat and 👎 penalties apply as specified (unit-tested; live effect starts with spec 005).
- [x] AC-5: `top` prints the top repos and stories with stars/day or points/hour, matched topics, boost and penalties.
- [x] AC-6: `/api/repos` and `/api/news` return `score` and `matched_topics` (news also `ai_dev`); both pages default to "For you" with topic badges; News "AI/dev only" toggle works; no console errors; typecheck and build pass.
- [x] AC-7: Matching and scoring are pure functions with unit tests, including a check on the saved HN fixture.

## Out of scope

- Embeddings / learned relevance (v1).
- Recording 👍/👎 and building briefs (spec 005).
- Classifying categories (v1).

## Open questions

Logged in [docs/qa/questions.md](../../docs/qa/questions.md).

- [x] Q-005: Interests: agents, mcp, claude, skills, new llm models.
- [x] Q-015: Topics + term lists; weak terms need another topic.
- [x] Q-016: Broad AI/dev list for news eligibility.
- [x] Q-017: "For you" sort, topic badges, AI/dev toggle.

## QA

Test cases: [docs/qa/test-cases/003-scoring.md](../../docs/qa/test-cases/003-scoring.md)

## Change log

- 1.0 (2026-10-11): Eyeball check on live data: plain "model" removed from the AI/dev list (matched "license model", "decision model"); added specific AI phrases and a few dev terms. Implementation and tests done.
- 1.0 (2026-10-11): Created and approved from the user's answers to Q-005, Q-015…Q-017; implementation started.
