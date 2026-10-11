# Test cases — 007 Stats

Spec: [007](../../../specs/007-stats/spec.md)

| TC | Title | Covers | Module | Type | Automated test / Steps | Last result |
| --- | --- | --- | --- | --- | --- | --- |
| TC-007-01 | Totals and shares from per-day rows; empty window | AC-1, REQ-FBK-002 | app/stats.py | unit | `backend/tests/test_stats.py::test_summarize_*` | pass 2026-10-11 |
| TC-007-02 | Check states pass / not yet / fail (unreachable); verdict only after the last day | AC-2, AC-3, REQ-FBK-002 | app/stats.py | unit | `backend/tests/test_stats.py::test_checks_*` | pass 2026-10-11 |
| TC-007-03 | API numbers equal direct SQL counts (trial + rolling) | AC-1, AC-4, REQ-FBK-002 | app/api/stats.py | integration | curl vs SQL on the local DB | pass 2026-10-11 (rolling: built 1, items 8, opened 0, rated 0 = SQL) |
| TC-007-04 | Stats page renders both views; no console errors | AC-4, REQ-FBK-002 | frontend/src/pages/Stats.tsx | manual | browser | pass 2026-10-11 (trial not started; rolling 14 rows; 0 console messages) |
| TC-007-05 | Frontend typecheck and build | AC-4, REQ-FBK-002 | frontend/src | unit | `npm run typecheck; npm run build` | pass 2026-10-11 |
