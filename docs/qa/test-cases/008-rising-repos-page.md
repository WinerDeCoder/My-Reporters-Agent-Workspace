# Test cases — 008 Rising repos page

Spec: [008](../../../specs/008-rising-repos-page/spec.md) · Plan: [plan.md](../../../specs/008-rising-repos-page/plan.md)

| TC | Title | Covers | Module | Type | Automated test / Steps | Last result |
| --- | --- | --- | --- | --- | --- | --- |
| TC-008-01 | Repo rows: latest stars, stars/day from momentum, null when history < 6 h, repos without snapshots included | AC-3, REQ-UI-001 | app/repo_stats.py | unit | `backend/tests/test_repo_stats.py::test_build_repo_rows` | pass 2026-10-11 |
| TC-008-02 | Rows sorted by stars/day with nulls last (CLI momentum order) | AC-3, REQ-UI-001 | app/repo_stats.py, app/cli.py | unit | `backend/tests/test_repo_stats.py::test_rank_by_momentum` | pass 2026-10-11 |
| TC-008-03 | `GET /api/repos` returns every tracked repo with the documented fields | AC-1, AC-3, REQ-UI-001 | app/api/repos.py | integration | Backend running on the local DB: `curl http://localhost:8000/api/repos` → count equals tracked repos in DB; fields present | pass 2026-10-11 (60 repos = DB count; all fields; stars_per_day null as history < 6 h) |
| TC-008-04 | Every run is recorded: success and failure (with error) | AC-4, REQ-COL-007 | app/scheduler.py, app/runs.py | unit | `backend/tests/test_scheduler.py::test_run_job_records_success`, `::test_run_job_records_failure` | pass 2026-10-11 |
| TC-008-05 | A recorder failure never breaks the job | AC-4, REQ-COL-007 | app/scheduler.py, app/runs.py | unit | `backend/tests/test_scheduler.py::test_recorder_failure_does_not_break_job` | pass 2026-10-11 |
| TC-008-06 | `GET /api/collectors/status` returns last run and next run per job | AC-5, REQ-UI-002, REQ-COL-007 | app/api/collectors.py | integration | After a run: `curl http://localhost:8000/api/collectors/status` shows each job with a recent `ok` run, its count and next run | pass 2026-10-11 (scheduled runs on a test instance: trending ok 60 in 10.4 s; github_api ok 60 in 12.9 s; next runs +6 h) |
| TC-008-07 | Rising repos page lists all repos with stars and stars/day or "collecting…" | AC-1, REQ-UI-001 | frontend/src/pages/Repos.tsx | manual | Open /repos; row count equals the API count; spot-check rows | pass 2026-10-11 (Playwright: 60 rows; all "collecting…" as expected) |
| TC-008-08 | Search, language filter and each sort order work | AC-2, REQ-UI-001 | frontend/src/pages/Repos.tsx | manual | Type "agent" → only matching rows; pick a language → only that language; switch sort → order changes accordingly | pass 2026-10-11 (Playwright: "agent" → 24, all match; Python → 23, all Python; stars sort strictly descending; newest keeps 60) |
| TC-008-09 | Status panel on Today and Rising repos; no console errors | AC-5, AC-6, REQ-UI-002 | frontend/src/components/CollectorStatus.tsx, frontend/src/pages/Today.tsx | manual | Open both pages; panel shows each job's last run, count and next run; browser console has no errors | pass 2026-10-11 (Playwright: both pages, 0 console messages; favicon 404 gone) |
| TC-008-10 | Frontend typecheck and production build pass | AC-6, REQ-UI-001 | frontend/src | unit | `cd frontend; npm run typecheck; npm run build` | pass 2026-10-11 |
