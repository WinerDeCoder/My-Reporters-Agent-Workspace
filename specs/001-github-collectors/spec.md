---
id: 001
title: GitHub collectors
status: in-progress
version: 1.0
requirements: [REQ-COL-001, REQ-COL-002, REQ-COL-005, REQ-NFR-004]
target_release: 0.2.0
created: 2026-10-10
updated: 2026-10-10
---

# 001 — GitHub collectors

## Why

Momentum (stars gained per day) is the core signal for rising repos, and it only exists if we snapshot star counts over time. This feature fills `repos` and `repo_snapshots` so scoring (spec 003) and the leaderboard (spec 006) have data.

## What (behavior)

1. **Trending collector:** every `sources.github_trending.every_hours`, reads the GitHub Trending page for each configured language (all, Python, TypeScript) and range (daily, weekly), and records every listed repo as a candidate (`repos`, updating `last_seen`).
2. **API snapshot collector:** every `sources.github_api.every_hours`, for each candidate whose `last_seen` is within `track_days`, fetches its metadata and README from the GitHub REST API, updates the `repos` row, and inserts one `repo_snapshots` row (stars, forks).
3. Both run inside the backend's scheduler, independently, first about 1 minute after the app starts (Trending first, API one minute later) and then on their interval. A failure in one never stops the other; transient errors are retried with backoff.
4. A CLI lets me run each collector once and print momentum, without waiting for the schedule:
   - `uv run python -m app.cli collect trending`
   - `uv run python -m app.cli collect github`
   - `uv run python -m app.cli momentum --top 20`

## Acceptance criteria

- [ ] AC-1: Running `collect trending` with the default config stores between 25 and 150 unique repos and logs the count per page.
- [ ] AC-2: Running `collect github` twice creates two snapshots per tracked repo, and fills description, topics, language, license and `readme_hash`.
- [x] AC-3: A repo that returns 404 (deleted or renamed) is logged and skipped; the run continues.
- [ ] AC-4: On a 403/429 rate-limit response the collector waits until the reset time (or backs off) instead of failing; a full run uses under 500 API requests.
- [x] AC-5: If the Trending job raises, the API job still runs on schedule (and vice versa).
- [ ] AC-6: After about 24 hours of scheduled runs, `momentum --top 20` shows plausible stars/day for well-known trending repos (eyeball check against GitHub).
- [x] AC-7: Trending HTML parsing is covered by a unit test on a saved HTML fixture; stars/day calculation is covered by unit tests.
- [x] AC-8: Both jobs first run about 1 minute after startup (API job ~1 minute after Trending), then every `every_hours`.

## Out of scope

- Hacker News and HN-linked candidates (spec 002).
- Scoring, keyword boosts (spec 003).
- Storing README text (only its hash; cards fetch the text when needed, spec 004).
- Star history backfill from the stargazers API.

## Open questions

Logged in [docs/qa/questions.md](../../docs/qa/questions.md).

- [x] Q-001: Track window counted from last seen.
- [x] Q-002: Languages stay all + Python + TypeScript.
- [x] Q-003: First run shortly after startup.

## QA

Test cases: [docs/qa/test-cases/001-github-collectors.md](../../docs/qa/test-cases/001-github-collectors.md)

## Change log

- 1.0 (2026-10-10): Approved. Q-001: track window counted from `last_seen`. Q-002: languages unchanged. Q-003: first run ~1 min after startup (new AC-8). Implementation started.
- 0.1 (2026-10-10): Draft.
