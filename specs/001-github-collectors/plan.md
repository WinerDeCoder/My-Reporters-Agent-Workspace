# 001 — Plan

Spec: [spec.md](spec.md) · Plan version 0.1 (draft, not yet approved)

## Approach

Two async collector functions in `app/collectors/`, each taking a DB session and an `httpx.AsyncClient`, doing idempotent upserts. The scheduler registers them as interval jobs; the CLI calls the same functions once. Momentum is a pure function over snapshots, so it is unit-testable without a DB.

## Changes

| Area | File / module | Change |
| --- | --- | --- |
| Backend | `app/collectors/__init__.py` | Shared `http_client()` (timeouts, User-Agent, GitHub token header) and `retrying` helper (tenacity) |
| Backend | `app/collectors/github_trending.py` | Fetch + parse trending pages; upsert repos |
| Backend | `app/collectors/github_api.py` | Select tracked repos; fetch repo + README; update repo; insert snapshot; rate-limit handling |
| Backend | `app/momentum.py` | `stars_per_day(snapshots, now)` and `stars_gained(snapshots, since)`; pure functions |
| Backend | `app/scheduler.py` | Register both jobs with `max_instances=1`, `coalesce=True`, first run shortly after startup |
| Backend | `app/cli.py` | `collect trending`, `collect github`, `momentum --top N` (argparse + `asyncio.run`) |
| DB | — | No schema change; tables exist from 000 |
| Config | `config.yaml` | None (uses existing `sources.*`) |
| Tests | `tests/fixtures/trending.html`, `tests/test_trending_parse.py`, `tests/test_momentum.py` | Parser and momentum unit tests |

## Details

**Trending fetch:** `GET https://github.com/trending/{language}?since={daily|weekly}` (language `""` = all). Parse with selectolax: each `article.Box-row h2 a` has `href="/owner/repo"`. 3 languages × 2 ranges = 6 pages per run, 25 repos each, about 50–100 unique after dedupe. If a page parses to 0 repos, log a warning (layout probably changed) without failing other pages.

**Upsert:** `INSERT ... ON CONFLICT (full_name) DO UPDATE SET last_seen = now()` via SQLAlchemy's PostgreSQL `insert`. Store `full_name` lowercased to dedupe case variants.

**Tracked set:** repos with `last_seen >= now() - track_days`.

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

- Unit: trending parser on a saved fixture (expected 25 names); momentum on synthetic snapshots (normal, gap, too-short history, star loss).
- Integration (manual, needs DB + token): AC-1…AC-4 via the CLI.
- Soak: leave the app running ~24 h, then AC-6.

## Risks

- GitHub changes the Trending HTML → parser returns 0; mitigated by the warning plus fixture test, fix is quick.
- Laptop asleep → fewer snapshots; momentum uses actual time gaps, so values stay correct, just less fresh.

## Docs to update when done

- [ ] `docs/architecture/overview.md`: collectors marked as built; CLI mentioned under Deployment.
- [ ] `README.md`: CLI commands under Common tasks.
- [ ] ADR needed? No (no hard-to-reverse choice).
