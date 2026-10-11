# 006 — Plan

Spec: [spec.md](spec.md) · Plan version 1.0

## Approach

`app/leaderboard.py`: pure `rank_weekly(rows, now)` over (repo, snapshots) using `momentum.stars_gained`; async `build_weekly_leaderboard(force)`; reader. Stored as a `briefs` row of type `weekly` (no schema change). API + page reuse the brief patterns.

## Changes

| Area | File / module | Change |
| --- | --- | --- |
| Config | `config.yaml` | `leaderboard.run_at` 07:35; size from `brief.leaderboard_size` (10) |
| Backend | `app/leaderboard.py` | `week_start()`, `rank_weekly()`, `build_weekly_leaderboard()`, `latest_leaderboard()` |
| Backend | `app/scheduler.py` | `leaderboard` job Mondays 07:35; always caught up (idempotent) |
| Backend | `app/api/leaderboard.py` | `GET /api/leaderboard/latest`, `POST /api/leaderboard/build` |
| Backend | `app/cli.py` | `leaderboard` |
| Frontend | `src/pages/Leaderboard.tsx`, `src/api/client.ts` | Page |

## Details

- Window: snapshots from `now - 7 days` (plus 1 day margin for the base) to now; base = last snapshot at/before the window start, else the first snapshot (then `since` = its date).
- Week key = Monday of the current local week; build only if `now >= Monday run_at` unless forced.

## Docs to update when done

- [x] `docs/architecture/overview.md`, `api.md`, `data-model.md`
- [x] `README.md`: `leaderboard`
- [x] Test case results
