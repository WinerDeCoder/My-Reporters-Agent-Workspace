---
id: 001
title: GitHub collectors
status: in-progress
version: 2.0
requirements: [REQ-COL-001, REQ-COL-002, REQ-COL-005, REQ-NFR-004]
target_release: 0.2.0
created: 2026-10-10
updated: 2026-10-11
---

# 001 — GitHub collectors

## Why

Momentum (stars gained per day) is the core signal for rising repos, and it only exists if we snapshot star counts over time. This feature fills `repos` and `repo_snapshots` so scoring (spec 003) and the leaderboard (spec 006) have data.

## What (behavior)

1. **Trending collector:** daily at `sources.github_trending.run_at` (07:10), reads the GitHub Trending page for each configured language (all, Python, TypeScript) and range (daily, weekly), and records every listed repo as a candidate (`repos`, updating `last_seen`).
2. **API snapshot collector:** daily at `sources.github_api.run_at` (07:20, after Trending and HN), for each candidate whose `last_seen` is within `track_days`, fetches its metadata and README from the GitHub REST API, updates the `repos` row, and inserts one `repo_snapshots` row (stars, forks).
3. Both run inside the backend's scheduler, independently, once a day at fixed times (Q-014). On startup a job runs only if its last successful run is older than `catch_up_after_hours` (20); a slot missed while the laptop slept still runs on wake (up to 12 h late). A failure in one never stops the other; transient errors are retried with backoff.
4. A CLI lets me run each collector once and print momentum, without waiting for the schedule:
   - `uv run python -m app.cli collect trending`
   - `uv run python -m app.cli collect github`
   - `uv run python -m app.cli momentum --top 20`

## Acceptance criteria

- [x] AC-1: Running `collect trending` with the default config stores between 25 and 150 unique repos and logs the count per page.
- [x] AC-2: Running `collect github` twice creates two snapshots per tracked repo, and fills description, topics, language, license and `readme_hash`.
- [x] AC-3: A repo that returns 404 (deleted or renamed) is logged and skipped; the run continues.
- [x] AC-4: On a 403/429 rate-limit response the collector waits until the reset time (or backs off) instead of failing; a full run uses under 500 API requests.
- [x] AC-5: If the Trending job raises, the API job still runs on schedule (and vice versa).
- [ ] AC-6: After about 24 hours of scheduled runs, `momentum --top 20` shows plausible stars/day for well-known trending repos (eyeball check against GitHub).
- [x] AC-7: Trending HTML parsing is covered by a unit test on a saved HTML fixture; stars/day calculation is covered by unit tests.
- [x] AC-8: Both jobs run daily at their `run_at` (07:10, 07:20); on startup a job is caught up only if its last success is older than 20 h (in order: Trending before snapshots).

## Out of scope

- Hacker News and HN-linked candidates (spec 002).
- Scoring, keyword boosts (spec 003).
- Storing README text (only its hash; cards fetch the text when needed, spec 004).
- Star history backfill from the stargazers API.

## Open questions

Logged in [docs/qa/questions.md](../../docs/qa/questions.md).

- [x] Q-001: Track window counted from last seen.
- [x] Q-002: Languages stay all + Python + TypeScript.
- [x] Q-003: First run shortly after startup. *(superseded by Q-014)*
- [x] Q-014: Daily at 07:10 / 07:20 with startup catch-up.

## QA

Test cases: [docs/qa/test-cases/001-github-collectors.md](../../docs/qa/test-cases/001-github-collectors.md)

## Change log

- 2.0 (2026-10-11): Daily schedule (Q-014, supersedes Q-003): Trending 07:10, snapshots 07:20, startup catch-up only when the last success is > 20 h old. AC-8 rewritten; TC-001-09 updated, TC-001-13 added. Stars/day now appears after the second daily snapshot, so the soak (AC-6) takes 1–2 days.
- 1.0 (2026-10-11): Live checks passed on the local DB (TC-001-10, 11): 60 repos, 2 snapshots each, 120 requests per run. Only the 24 h soak (AC-6) remains.
- 1.0 (2026-10-10): Approved. Q-001: track window counted from `last_seen`. Q-002: languages unchanged. Q-003: first run ~1 min after startup (new AC-8). Implementation started.
- 0.1 (2026-10-10): Draft.
