# 007 — Plan

Spec: [spec.md](spec.md) · Plan version 1.0

## Approach

`app/stats.py`: async `day_rows(session, start, end)` (one row per date: built, opened_at, items, rated, up, down) and pure `summarize(rows, window, today, thresholds)` → totals, shares, check states, verdict. API returns both; the page renders cards for the checks and a per-day table.

## Changes

| Area | File / module | Change |
| --- | --- | --- |
| Config | `config.yaml`, `app/config.py` | `trial` section |
| Backend | `app/stats.py` | `TrialConfig` use, `day_rows()`, `summarize()`, `check_state()` |
| Backend | `app/api/stats.py` | `GET /api/stats?view=trial|rolling` |
| Frontend | `src/pages/Stats.tsx`, `src/api/client.ts` | Page |

## Details

- **Check states:** pass if the threshold is already met (for opened days: count ≥ min); fail if it can't be met anymore (opened days + remaining days < min); otherwise "not yet". Shares: pass/fail judged only at the end; before that "on track" if currently ≥ threshold, else "below".
- Days counted in the configured timezone; "opened" = the day's brief has `opened_at`.

## Docs to update when done

- [x] `docs/architecture/overview.md`, `api.md`
- [x] PRD success criteria: link to Stats
- [x] Test case results
