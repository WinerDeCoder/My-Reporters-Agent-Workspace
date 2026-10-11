# 008 — Plan

Spec: [spec.md](spec.md) · Plan version 1.0 · Test cases: [docs/qa/test-cases/008-rising-repos-page.md](../../docs/qa/test-cases/008-rising-repos-page.md)

## Approach

Backend: a `collector_runs` table written by the existing `run_job()` wrapper; a small `repo_stats` module that turns repos + recent snapshots into rows (shared by the API and the CLI's `momentum` command); two read-only endpoints. Frontend: a new page and a reusable status panel, both fed by TanStack Query with a 60 s refetch. Filtering and sorting happen in the browser (a few hundred rows at most).

## Changes

| Area | File / module | Change |
| --- | --- | --- |
| DB | `app/models.py`, `alembic/versions/0002_collector_runs.py` | New `CollectorRun` (id, job, started_at, finished_at, ok, result, error); index on `(job, started_at)` |
| Backend | `app/runs.py` | `record_run(...)`: insert one row; swallow and log DB errors |
| Backend | `app/scheduler.py` | `run_job(name, fn, recorder=record_run)` records every run; `create_scheduler` unchanged otherwise |
| Backend | `app/main.py` | Keep the scheduler on `app.state.scheduler` (for next run times) |
| Backend | `app/repo_stats.py` | Pure `build_repo_rows(repos, snapshots)` → rows with latest stars and stars/day; `load_repo_rows(session, track_days)` query |
| Backend | `app/api/repos.py` | `GET /api/repos` → `list[RepoRow]` |
| Backend | `app/api/collectors.py` | `GET /api/collectors/status` → `list[CollectorStatus]` (last run + next run per job) |
| Backend | `app/cli.py` | `collect` goes through `run_job` (so CLI runs are recorded); `momentum` uses `repo_stats` |
| Frontend | `src/api/client.ts` | `RepoRow`, `CollectorStatus` types |
| Frontend | `src/components/CollectorStatus.tsx` | Compact panel (per job: last run, ok/failed, count, next run) |
| Frontend | `src/pages/Repos.tsx` | Search, language filter, sort, list; "collecting…" for null stars/day |
| Frontend | `src/App.tsx`, `src/pages/Today.tsx`, `index.html`, `public/favicon.svg` | Nav link + route; status panel on Today; favicon |

## Details

- **Tracked set** is the same as the API collector's (`last_seen` within `track_days`), so the page shows exactly what is being snapshotted.
- **Snapshots loaded:** last 48 h per tracked repo (enough for the 24 h stars/day window) plus the latest one for total stars.
- **Status "next run":** from `app.state.scheduler.get_job(id).next_run_time`; `null` when the scheduler isn't running (e.g. tests).
- **Times** are returned as ISO 8601 with offset; the UI shows relative time ("12 min ago") with the full time on hover.
- **Recording failures:** `record_run` catches all exceptions and logs them, so a DB outage can't turn a successful collection into a failure.

## Testing

See test cases. Unit: `build_repo_rows`, `run_job` recording (fake recorder: ok, failure, recorder raising). Integration: endpoints against the running DB. Manual (Playwright): the page, search/filter/sort, status panel, console clean.

## Risks

- The user's running backend must be restarted (or be in `fastapi dev` reload mode) and `alembic upgrade head` run to get the new table.

## Docs to update when done

- [x] `docs/architecture/data-model.md`: `collector_runs`
- [x] `docs/architecture/api.md`: two endpoints
- [x] `docs/architecture/overview.md`: modules, pages
- [x] `docs/qa/test-cases/008-rising-repos-page.md`: results
