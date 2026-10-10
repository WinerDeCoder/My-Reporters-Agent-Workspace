# 001 — Plan

Spec: [spec.md](spec.md) · Plan version 1.0 (approved with spec 1.0) · Test cases: [docs/qa/test-cases/001-github-collectors.md](../../docs/qa/test-cases/001-github-collectors.md)

## Approach

Two async collector functions in `app/collectors/`, each taking a DB session and an `httpx.AsyncClient`, doing idempotent upserts. The scheduler registers them as interval jobs; the CLI calls the same functions once. Momentum is a pure function over snapshots, so it is unit-testable without a DB.

## Changes

| Area | File / module | Change |
| --- | --- | --- |
| Backend | `app/collectors/__init__.py` | `make_client(github_api)` (timeouts, User-Agent, GitHub token + API-version headers) and `transient_retry` (tenacity: transport errors and 5xx, 3 attempts, exponential backoff) |
| Backend | `app/collectors/github_trending.py` | `trending_urls(cfg)`, pure `parse_trending(html)`, `collect_trending()`: fetch pages, upsert repos |
| Backend | `app/collectors/github_api.py` | `tracked_repos()`, pure `parse_repo_payload()` and `rate_limit_wait()`, `fetch_repo()` (404 → `None`), `collect_github()`: update repos, insert snapshots, count requests |
| Backend | `app/momentum.py` | `Snapshot`, `stars_per_day(snapshots)`, `stars_gained(snapshots, since)`; pure functions |
| Backend | `app/scheduler.py` | `run_job()` wrapper (log + isolate failures); both jobs with `max_instances=1`, `coalesce=True`, `misfire_grace_time=3600`, first run at startup + 60 s (trending) / + 120 s (API) |
| Backend | `app/cli.py` | `collect trending`, `collect github`, `momentum --top N` (argparse + `asyncio.run`) |
| DB | — | No schema change; tables exist from 000 |
| Config | `config.yaml` | None (uses existing `sources.*`) |
| Dev deps | `backend/pyproject.toml` | `pytest-asyncio` (auto mode) for async tests |
| Tests | `tests/fixtures/trending.html`, `tests/test_trending_parse.py`, `tests/test_momentum.py`, `tests/test_github_api.py`, `tests/test_scheduler.py` | Unit tests per [test cases](../../docs/qa/test-cases/001-github-collectors.md); HTTP faked with `httpx.MockTransport` |

## Details

**Trending fetch:** `GET https://github.com/trending/{language}?since={daily|weekly}` (language `""` = all). Parse with selectolax: each `article.Box-row h2 a` has `href="/owner/repo"`. 3 languages × 2 ranges = 6 pages per run, 25 repos each, about 50–100 unique after dedupe. If a page parses to 0 repos, log a warning (layout probably changed) without failing other pages.

**Upsert:** `INSERT ... ON CONFLICT (full_name) DO UPDATE SET last_seen = now()` via SQLAlchemy's PostgreSQL `insert`. Store `full_name` lowercased to dedupe case variants.

**Tracked set:** repos with `last_seen >= now() - track_days` (window counted from last seen, Q-001).

**Scheduling:** the API job's first run is one minute after the Trending job's, so a fresh install has candidates before the first snapshot run (Q-003).

**GitHub API, per repo (2 requests):**
- `GET /repos/{full_name}`: `stargazers_count`, `forks_count`, `description`, `topics`, `language`, `license.spdx_id`. If `full_name` changed (redirect/rename), update the row's name when it doesn't collide.
- `GET /repos/{full_name}/readme` with `Accept: application/vnd.github.raw`: sha256 of the body → `readme_hash`. 404 = no README → `NULL`.
- Headers: `Authorization: Bearer $GITHUB_TOKEN`, `X-GitHub-Api-Version: 2022-11-28`.
- Concurrency: `asyncio.Semaphore(5)`.
- Rate limits: read `X-RateLimit-Remaining` / `X-RateLimit-Reset`; on 403/429 with remaining 0, sleep until reset (cap 15 min) then retry once; otherwise tenacity exponential backoff (3 attempts) for 5xx and network errors.
- Budget: ~100 repos × 2 = ~200 requests/run, ~800/day, against 5,000/hour.

**Momentum:** `stars_per_day` = (latest.stars − base.stars) / hours × 24, where base is the snapshot closest to 24 h before latest, with at least 6 h of span; returns `None` if there isn't enough history.

**Errors:** each job wraps its whole run in try/except, logs the exception with the job name, and returns; APScheduler keeps the schedule.

## Testing

Full list with IDs and results: [docs/qa/test-cases/001-github-collectors.md](../../docs/qa/test-cases/001-github-collectors.md).

- Unit: trending parser on a saved fixture; momentum on synthetic snapshots (normal, gap, too-short history, star loss); repo payload parsing; 404 and rate-limit handling via `httpx.MockTransport`; job isolation and registration.
- Integration (needs DB + token): AC-1, AC-2, AC-4 via the CLI.
- Soak: leave the app running ~24 h, then AC-6.

## Risks

- GitHub changes the Trending HTML → parser returns 0; mitigated by the warning plus fixture test, fix is quick.
- Laptop asleep → fewer snapshots; momentum uses actual time gaps, so values stay correct, just less fresh.

## Docs to update when done

- [x] `docs/architecture/overview.md`: collectors marked as built; CLI mentioned under Deployment.
- [x] `README.md`: CLI commands under Common tasks.
- [ ] `docs/qa/test-cases/001-github-collectors.md`: results for every test case.
- [ ] ADR needed? No (no hard-to-reverse choice).
