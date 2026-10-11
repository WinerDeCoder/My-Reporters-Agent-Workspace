# 002 — Plan

Spec: [spec.md](spec.md) · Plan version 1.0 · Test cases: [docs/qa/test-cases/002-hn-collector.md](../../docs/qa/test-cases/002-hn-collector.md)

## Approach

Same shape as spec 001: pure parsing functions + a thin async collector doing idempotent upserts, scheduled through `run_job()` (so runs are recorded), with a CLI entry. Repo candidates reuse `upsert_candidates()` from the Trending collector. A pure `points_per_hour()` lives in `app/news_stats.py` so scoring (spec 003) can reuse it. The News page copies the Rising repos pattern.

## Changes

| Area | File / module | Change |
| --- | --- | --- |
| Config | `config.yaml`, `app/config.py` | `sources.hacker_news`: `popular_min_points: 100`, `popular_window_hours: 24`, `retention_days: 30` |
| Backend | `app/collectors/hacker_news.py` | `algolia_queries()`, pure `parse_hits()`, `github_repo_from_url()`, `merge_stories()`; `collect_hacker_news()` |
| Backend | `app/collectors/prune.py` | pure `prune_cutoffs()`; `prune_old_data()` deletes old stories + untracked snapshots, returns rows deleted |
| Backend | `app/news_stats.py` | pure `points_per_hour(points, posted_at, now)` (age floored at 1 h) |
| Backend | `app/scheduler.py` | Jobs `hacker_news` (daily 07:00) and `prune` (Mondays 07:40); startup catch-up if stale (v2.0, Q-014) |
| Backend | `app/api/news.py` | `GET /api/news?days=7` |
| Backend | `app/cli.py` | `collect hn`, `prune` |
| DB | — | No schema change (`news_items` exists) |
| Frontend | `src/api/client.ts`, `src/pages/News.tsx`, `src/App.tsx`, `src/components/CollectorStatus.tsx` | News types + page + nav; labels/units for the new jobs |

## Details

- **Algolia queries** (`https://hn.algolia.com/api/v1/search`): `tags=front_page&hitsPerPage=50`, and `tags=story&numericFilters=points>100,created_at_i>{now-24h}&hitsPerPage=100`. Two requests per run; Algolia needs no key.
- **Parsing:** `hn_id = int(objectID)`, `posted_at` from `created_at_i` (UTC), `comments = num_comments or 0`; hits without a title are skipped; `url` may be null (Ask HN) and is stored as null.
- **Merging:** union by `hn_id`, keeping the higher points/comments.
- **GitHub URL rule:** host `github.com` or `www.github.com`; first two path segments are owner/repo; owner not in a reserved list (`orgs`, `topics`, `sponsors`, `marketplace`, `features`, `collections`, `trending`, `settings`, `apps`, `about`, `enterprise`, `pricing`, `explore`, `search`, `login`, `site`, `security`, `readme`, `customer-stories`); repo name loses a `.git` suffix; lowercased.
- **Upsert order:** upsert repo candidates first, read their ids, then upsert stories with `ON CONFLICT (hn_id) DO UPDATE` (title, url, points, comments, linked_repo_id, fetched_at).
- **Prune:** `DELETE FROM news_items WHERE posted_at < now - retention_days`; `DELETE FROM repo_snapshots USING repos WHERE repos.last_seen < now - track_days`. Briefs don't exist yet, so "unless a brief references it" is a no-op until spec 005.
- **Points/hour:** `points / max(age_hours, 1)`.

## Testing

See test cases. Unit: fixtures `tests/fixtures/hn_front_page.json`, `hn_popular.json` (saved from the live API 2026-10-11). Integration: CLI runs against the local DB + SQL checks. Manual: News page in the browser.

## Risks

- Algolia's `front_page` tag lags the real front page by a few minutes: fine for a daily job. With one run a day, stories that peak and fade between runs are caught by the 26 h popular query.
- Pruning deletes data: the cutoffs are unit-tested, and the live check verifies tracked repos keep their snapshots.

## Docs to update when done

- [x] `docs/architecture/overview.md`: modules, flows, pages
- [x] `docs/architecture/api.md`: `/api/news`
- [x] `docs/architecture/data-model.md`: retention rules
- [x] `README.md`: CLI commands
- [x] `docs/qa/test-cases/002-hn-collector.md`: results
