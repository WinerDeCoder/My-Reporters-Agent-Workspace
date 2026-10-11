# 003 — Plan

Spec: [spec.md](spec.md) · Plan version 1.0 · Test cases: [docs/qa/test-cases/003-scoring.md](../../docs/qa/test-cases/003-scoring.md)

## Approach

All scoring is pure functions in `app/scoring.py` (no DB, no clock), fed by the existing row builders: `repo_stats.load_repo_rows` and the news endpoint. A small async loader collects the penalty signals (recently briefed items, disliked topics) and returns empty sets until briefs and feedback exist. The API adds `score` / `matched_topics` / `ai_dev`; the frontend only changes its default sort and adds badges and a toggle.

## Changes

| Area | File / module | Change |
| --- | --- | --- |
| Config | `config.yaml`, `app/config.py` | `interests.topics` (topic → terms, `~` = weak), `interests.ai_dev_terms`, `interests.topic_boost` 1.5, `interests.max_boost` 3.0, `scoring.repeat_penalty` 0.3, `scoring.dislike_penalty` 0.7, `scoring.dislike_floor` 0.2, `scoring.dislike_days` 30; replaces `interests.keywords` |
| Backend | `app/scoring.py` | `normalize()`, `TopicMatcher`, `boost()`, `Score`, `score_item()`, `repo_text()`, `news_text()`, `Signals` + `load_signals()` |
| Backend | `app/repo_stats.py` | `RepoRow` gains `score`, `matched_topics`; rows scored after building |
| Backend | `app/api/repos.py`, `app/api/news.py` | New response fields |
| Backend | `app/cli.py` | `top [--repos N] [--news N]` |
| DB | — | None. Convention for spec 005: each `briefs.items` entry has `item_type` and `item_id` |
| Frontend | `src/api/client.ts`, `src/pages/Repos.tsx`, `src/pages/News.tsx`, `src/components/TopicBadges.tsx` | Types, "For you" sort (default), topic badges, AI/dev toggle |

## Details

- **Normalize:** lowercase; every char not in `[a-z0-9+#.]` → space; collapse spaces; match `" term "` inside `" text "` (so `gpt` matches "GPT-5", `multi agent` matches "multi-agent").
- **Repo text:** full name (with `/`,`-`,`_` → spaces) + description + GitHub topics. **News text:** title + domain.
- **Boost:** `min(topic_boost ** n_topics, max_boost)`; n = 0 → 1.0.
- **Score:** `max(base, 0) × boost × repeat × dislike`; base None (no stars/day yet) → score None. News: not AI/dev → score None.
- **Signals:** recent brief items = `item_id`s by type from `briefs.items` where `date >= today - repeat_cooldown_days`; disliked topics = topics of items with a −1 rating in the last 30 days (counted). Both empty today.

## Testing

Unit: matcher cases (whole word, multi-word, hyphen, weak), boost cap, score with each penalty, dislike floor, news eligibility, fixture check on `hn_front_page.json`. Integration: `top` on the local DB; API fields. Manual: both pages in a browser.

## Risks

- Term lists are guesses: easy to tune in `config.yaml`, and the "For you" view makes misses visible.
- Plain `model`/`models` in the AI/dev list matched "license model", "decision model" in the live check, so it was replaced by specific phrases ("language model", "ai model").

## Docs to update when done

- [x] `docs/architecture/overview.md`: scoring module and flow
- [x] `docs/architecture/api.md`: new fields
- [x] `docs/architecture/data-model.md`: `briefs.items` convention
- [x] `README.md`: `top` command, tuning interests
- [x] `docs/qa/test-cases/003-scoring.md`: results
