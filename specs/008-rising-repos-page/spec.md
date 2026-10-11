---
id: 008
title: Rising repos page
status: in-progress
version: 1.0
requirements: [REQ-UI-001, REQ-UI-002, REQ-COL-007]
target_release: 0.2.0
created: 2026-10-11
updated: 2026-10-11
---

# 008 — Rising repos page

## Why

The collectors (spec 001) now fill the database, but no page shows the data: the roadmap's first content page (Today, spec 005) waits for scoring and cards. A Rising repos page makes the collected data visible now, lets me sanity-check momentum by eye during the soak, and becomes a page of the v1 dashboard later. A small collector-status panel shows the background jobs are actually running. Decided in Q-008 and Q-009.

## What (behavior)

1. **Rising repos page** (`/repos`, in the nav as "Rising repos"): one row per tracked repo with full name (link to GitHub), description, language, topics, total stars, stars/day, and when it was first seen.
   - Stars/day shows "collecting…" until the repo has 6 h of snapshot history.
   - Controls: text search (name, description, topics), language filter, sort by stars/day (default), total stars, or newest first-seen.
   - Data refreshes every minute.
2. **Collector run log:** every collector run (scheduled or from the CLI) is stored with job name, start, end, success, result count and error.
3. **Collector status panel:** per job, last run time, outcome (ok / failed + error), count, and next scheduled run. Shown on the Today page (replacing the bare status list, keeping API/DB status) and in the Rising repos header.
4. The missing favicon is added (removes the console 404).

## Acceptance criteria

- [x] AC-1: With the current data, `/repos` lists every tracked repo (matches `GET /api/repos` count) with name, link, description, language, topics, stars and stars/day or "collecting…".
- [x] AC-2: Search narrows the list by name, description or topic; the language filter shows only that language; each sort order orders the list correctly.
- [x] AC-3: `GET /api/repos` returns tracked repos with latest stars and stars/day computed by `app/momentum.py`; repos without enough history return `stars_per_day: null`.
- [x] AC-4: Each collector run, scheduled or CLI, writes one `collector_runs` row; a failing job records `ok = false` with the error; a failure to record never breaks the job.
- [x] AC-5: `GET /api/collectors/status` returns, per job, the last run (time, ok, count, error) and the next scheduled run; the panel on Today and Rising repos shows it.
- [x] AC-6: `npm run typecheck` and `npm run build` pass; no console errors on Today or Rising repos.

## Out of scope

- Star-history charts, follow/unfollow, repo detail page (v1 dashboard).
- Scoring, keyword boosts (spec 003); cards (spec 004).
- Pagination (under a few hundred tracked repos; client-side filtering is enough).

## Open questions

Logged in [docs/qa/questions.md](../../docs/qa/questions.md).

- [x] Q-008: Rising repos page now.
- [x] Q-009: Collector status panel, with a run log table.

## QA

Test cases: [docs/qa/test-cases/008-rising-repos-page.md](../../docs/qa/test-cases/008-rising-repos-page.md)

## Change log

- 1.0 (2026-10-11): Created and approved from the user's answers to Q-008 and Q-009; implementation started.
