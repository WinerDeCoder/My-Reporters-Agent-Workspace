---
id: 007
title: Stats
status: done
version: 1.0
requirements: [REQ-FBK-002]
target_release: 0.8.0
created: 2026-10-11
updated: 2026-10-11
---

# 007 — Stats

## Why

The MVP exists to answer one question after two weeks: is the brief worth it? The Stats page answers it with the PRD's success criteria, turned into numbers (Q-028).

## What (behavior)

1. **Trial view** (Q-029): from `trial.start_date` (2026-10-12) for `trial.days` (14): "day N of 14", briefs built, briefs opened (days), brief items, items rated, 👍 / 👎, share of 👍 among rated, share of items rated.
2. **Checks** (Q-028): opened on ≥ 10 of 14 days; ≥ 60 % of rated items 👍; ≥ 50 % of brief items rated. Each shows pass / not yet / fail (fail only when it can no longer be reached). After day 14: a verdict: **continue to v1** if all pass, otherwise "fix scoring and cards first" (PRD).
3. **Rolling view:** the same numbers for the last 14 days, for after the trial.
4. **Per-day table:** date, built, opened time, items, rated, 👍, 👎.
5. Thresholds and dates live in `config.yaml` → `trial`.

## Acceptance criteria

- [x] AC-1: Numbers match direct SQL counts on the same data.
- [x] AC-2: Check states: pass / not yet / fail (unreachable) computed correctly, including mid-trial.
- [x] AC-3: Verdict appears only after the last trial day.
- [x] AC-4: `GET /api/stats?view=trial|rolling` returns the numbers; Stats page renders both views; no console errors; typecheck and build pass.

## Out of scope

Charts over time; per-topic breakdowns (v1).

## Open questions

- [x] Q-028: 10/14 days, 60 % 👍, 50 % rated.
- [x] Q-029: Fixed trial + rolling view.

## QA

Test cases: [docs/qa/test-cases/007-stats.md](../../docs/qa/test-cases/007-stats.md)

## Change log

- 1.0 (2026-10-11): Created and approved from the user's answers to Q-028 and Q-029; implementation started.
- 1.0 (2026-10-11): Done. All ACs verified on the Reporters DB; all test cases pass.
