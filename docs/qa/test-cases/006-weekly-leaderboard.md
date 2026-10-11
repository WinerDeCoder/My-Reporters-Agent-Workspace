# Test cases — 006 Weekly leaderboard

Spec: [006](../../../specs/006-weekly-leaderboard/spec.md)

| TC | Title | Covers | Module | Type | Automated test / Steps | Last result |
| --- | --- | --- | --- | --- | --- | --- |
| TC-006-01 | Ranking by stars gained over 7 days; skip < 2 snapshots; `since` for newer repos; top N | AC-1, REQ-LDB-001 | app/leaderboard.py | unit | `backend/tests/test_leaderboard.py::test_rank_*` | pass 2026-10-11 |
| TC-006-02 | Week start (Monday, local) and due check (Monday 07:35 onward) | AC-2, REQ-LDB-001 | app/leaderboard.py | unit | `backend/tests/test_leaderboard.py::test_week_*` | pass 2026-10-11 |
| TC-006-03 | `leaderboard` job Mondays 07:35; always caught up | AC-2, REQ-LDB-001 | app/scheduler.py | unit | `backend/tests/test_scheduler.py` | pass 2026-10-11 |
| TC-006-04 | Live build: 10 entries; second build no-op | AC-1, AC-2, REQ-LDB-001 | app/leaderboard.py, app/cli.py | integration | `uv run python -m app.cli leaderboard` twice | pass 2026-10-11 (10 entries, week of 2026-10-05; 2nd run no-op) |
| TC-006-05 | API latest/build + page renders; no console errors | AC-3, AC-4, REQ-LDB-001 | app/api/leaderboard.py, frontend/src/pages/Leaderboard.tsx | manual | curl + browser | pass 2026-10-11 (ordered by stars gained; 0 console messages) |
| TC-006-06 | Frontend typecheck and build | AC-4, REQ-LDB-001 | frontend/src | unit | `npm run typecheck; npm run build` | pass 2026-10-11 |
