# 005 — Plan

Spec: [spec.md](spec.md) · Plan version 1.0 · Test cases: [docs/qa/test-cases/005-daily-brief.md](../../docs/qa/test-cases/005-daily-brief.md)

## Approach

`app/brief.py` holds pure selection (`select_brief_items`) and timing (`brief_due`) plus the async `build_daily_brief()` job and readers. The API adds brief and feedback endpoints; the Today page renders the brief. Card summaries are read live (latest card), so a card written after the brief still shows.

## Changes

| Area | File / module | Change |
| --- | --- | --- |
| Config | `config.yaml` | `brief_time: "07:30"`; uses `brief.top_repos` (5, incl. the top story), `brief.top_news` (3) |
| Backend | `app/brief.py` | `select_brief_items()`, `brief_due()`, `build_daily_brief()`, `load_brief()`, `mark_opened()`, `set_rating()` |
| Backend | `app/scheduler.py` | `brief` job at `brief_time`; catch-up +5 min (prune moves to +6 min) |
| Backend | `app/api/briefs.py` | `GET /api/briefs/today`, `POST /api/briefs/today/build`, `POST /api/feedback` |
| Backend | `app/collectors/prune.py` | keep stories referenced by briefs; snapshots only of untracked repos never briefed |
| Backend | `app/cli.py` | `brief` |
| DB | — | No schema change (`briefs`, `feedback` exist since 0001) |
| Frontend | `src/pages/Today.tsx`, `src/components/Rating.tsx`, `src/api/client.ts` | Brief view, empty state + Build now, 👍/👎 |

## Details

- **Local date** = `now` in `config.timezone`. `brief_due(now_local, brief_time)` = local time ≥ brief_time.
- **Items JSON**: `{section, item_type, item_id, title, url, hn_url, stars, stars_per_day, points, comments, points_per_hour, linked_repo, matched_topics, score, description}`.
- **Feedback**: rating ∈ {1, −1, 0}; 0 deletes the row for (item, brief); otherwise replace. Current rating per item = the row for that brief.
- **Prune**: referenced ids collected from `briefs.items` in Python (few rows).

## Testing

Unit: selection cases, `brief_due`, scheduler registration and catch-up order, rating validation. Integration: CLI `brief` twice (second = no-op), API GET (opened_at set once), feedback switch/clear, prune with a brief reference. Manual: Today page in the browser.

## Docs to update when done

- [x] `docs/architecture/overview.md`, `api.md`, `data-model.md` (`briefs.items` fields)
- [x] `README.md`: `brief` command
- [x] `docs/qa/test-cases/005-daily-brief.md`: results
