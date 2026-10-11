# Test cases — 003 Scoring

Spec: [003](../../../specs/003-scoring/spec.md) · Plan: [plan.md](../../../specs/003-scoring/plan.md)

| TC | Title | Covers | Module | Type | Automated test / Steps | Last result |
| --- | --- | --- | --- | --- | --- | --- |
| TC-003-01 | Topic matching: whole word, case, multi-word, hyphen/slash, weak terms need another topic | AC-1, REQ-SCO-001, REQ-SCO-002 | app/scoring.py | unit | `backend/tests/test_scoring.py::test_matcher_*` | pass 2026-10-11 |
| TC-003-02 | Boost per topic, capped (formula; config 2.0 / 5.0 since Q-019) | AC-2, REQ-SCO-001 | app/scoring.py | unit | `backend/tests/test_scoring.py::test_boost` | pass 2026-10-11 |
| TC-003-03 | Repo and news scores: formula, unscored without stars/day, news only when AI/dev | AC-2, AC-3, REQ-SCO-001, REQ-SCO-002 | app/scoring.py | unit | `backend/tests/test_scoring.py::test_score_*` | pass 2026-10-11 |
| TC-003-04 | Repeat penalty ×0.3; 👎 penalty ×0.7 per shared topic, floor ×0.2 | AC-4, REQ-SCO-003 | app/scoring.py | unit | `backend/tests/test_scoring.py::test_penalties` | pass 2026-10-11 |
| TC-003-05 | Saved HN front page: AI/dev stories found, obvious off-topic stories excluded | AC-3, AC-7, REQ-SCO-002 | app/scoring.py | unit | `backend/tests/test_scoring.py::test_saved_front_page_ai_dev` | pass 2026-10-11 (agent/MCP stories matched; vegetables, food, city-game excluded; after removing plain "model" from the AI/dev list) |
| TC-003-06 | `top` prints ranked repos and stories with score parts | AC-5, REQ-SCO-001, REQ-SCO-002 | app/cli.py | integration | `cd backend; uv run python -m app.cli top` on the local DB | pass 2026-10-11 (60/66 repos scored; top: morluto/rea, mattpocock/skills, diagram-design with topic boosts; news 18/41 AI/dev, top 2 = agent stories) |
| TC-003-07 | `/api/repos` and `/api/news` return `score`, `matched_topics` (+ `ai_dev`) | AC-6, REQ-UI-004 | app/api/repos.py, app/api/news.py | integration | curl both endpoints; fields present; scored items ordered by score in "For you" | pass 2026-10-11 (repos: score + matched_topics on all 66; news: score set exactly for the 18 ai_dev stories, ordered by score) |
| TC-003-08 | Pages default to "For you" with topic badges; News AI/dev toggle; no console errors | AC-6, REQ-UI-004 | frontend/src/pages/Repos.tsx, frontend/src/pages/News.tsx | manual | Open /repos and /news; check default sort, badges, toggle on/off changes the count; console clean | pass 2026-10-11 (Playwright: both pages default "For you"; 33/66 repos and 5 stories with badges; AI/dev toggle 18 ↔ 41; 0 console messages) |
| TC-003-09 | Frontend typecheck and production build pass | AC-6, REQ-UI-004 | frontend/src | unit | `cd frontend; npm run typecheck; npm run build` | pass 2026-10-11 |
