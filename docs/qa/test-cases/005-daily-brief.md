# Test cases — 005 Daily brief

Spec: [005](../../../specs/005-daily-brief/spec.md) · Plan: [plan.md](../../../specs/005-daily-brief/plan.md)

| TC | Title | Covers | Module | Type | Automated test / Steps | Last result |
| --- | --- | --- | --- | --- | --- | --- |
| TC-005-01 | Selection: top story #1 repo, repos #2–#5, top 3 AI/dev stories, unscored skipped, short lists OK | AC-1, REQ-BRF-001 | app/brief.py | unit | `backend/tests/test_brief.py::test_select_*` | pass 2026-10-11 |
| TC-005-02 | `brief_due`: before 07:30 → no, at/after → yes (local time) | AC-3, REQ-BRF-002 | app/brief.py | unit | `backend/tests/test_brief.py::test_brief_due` | pass 2026-10-11 |
| TC-005-03 | `brief` job at 07:30; catch-up after cards, before prune | AC-2, AC-3, REQ-BRF-001, REQ-BRF-002 | app/scheduler.py | unit | `backend/tests/test_scheduler.py` | pass 2026-10-11 |
| TC-005-04 | Live build: one brief with 8 items; second build same day = no-op | AC-1, AC-2, REQ-BRF-001 | app/brief.py, app/cli.py | integration | `cd backend; uv run python -m app.cli brief` twice; one `briefs` row for today | pass 2026-10-11 (brief 2026-10-11 built with 8 items in 5.7 s, all cards cached; second build: already exists) |
| TC-005-05 | `GET /api/briefs/today` returns items + card summaries + ratings; `opened_at` set once | AC-4, REQ-BRF-003, REQ-BRF-004 | app/api/briefs.py | integration | GET twice; `opened_at` equal both times | pass 2026-10-11 (8 items in order top/4 repos/3 news, 8/8 with card summary; opened_at identical on two GETs; reset to NULL afterwards so the user's first view counts) |
| TC-005-06 | Feedback save / switch / clear; penalties now active in scoring | AC-5, AC-6, REQ-FBK-001, REQ-SCO-003 | app/api/briefs.py, app/scoring.py | integration | POST 1, −1, 0 for one item; check rows; `top` shows repeat penalty ×0.3 on briefed repos | pass 2026-10-11 (👍 → 👎 → clear via API and page; item not in brief 404; rating 5 → 422; briefed repos now score stars/day × boost × 0.3; test ratings cleared, 0 feedback rows left) |
| TC-005-07 | Prune keeps briefed stories and briefed repos' snapshots | AC-7, REQ-COL-006 | app/collectors/prune.py | integration | Fake old story + untracked repo referenced by a fake brief survive prune; unreferenced ones go | pass 2026-10-11 (fake briefed old story + untracked repo kept, unbriefed ones deleted; all fixtures removed) |
| TC-005-08 | Today page: brief sections, card lines, 👍/👎 persist after reload, empty state; no console errors | AC-8, REQ-BRF-003, REQ-FBK-001 | frontend/src/pages/Today.tsx, frontend/src/components/Rating.tsx | manual | Open /, rate items, reload | pass 2026-10-11 (Playwright: Top story / Rising repos / News, 8 rating pairs, 👍 persisted after reload and cleared on second click, 0 console messages) |
| TC-005-09 | Frontend typecheck and production build pass | AC-8, REQ-BRF-003 | frontend/src | unit | `cd frontend; npm run typecheck; npm run build` | pass 2026-10-11 |
