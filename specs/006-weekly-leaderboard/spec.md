---
id: 006
title: Weekly leaderboard
status: done
version: 1.0
requirements: [REQ-LDB-001]
target_release: 0.7.0
created: 2026-10-11
updated: 2026-10-11
---

# 006 — Weekly leaderboard

## Why

The daily brief shows what's rising today; once a week it's worth seeing what grew most overall. The leaderboard is computed from the star snapshots we already store.

## What (behavior)

1. **Build** Mondays at 07:35 (after the brief): one `briefs` row (type `weekly`, date = that Monday) with the top 10 tracked repos by **raw stars gained over the last 7 days** (Q-026); each entry stores rank, stars gained, total stars, description, language, topics, and "since" (first snapshot date) when the repo has been tracked for less than 7 days.
2. Built once per week; startup catch-up builds the current week's leaderboard if it's missing and it's past Monday 07:35; "Build now" on the page builds it immediately.
3. **Leaderboard page** shows the latest weekly leaderboard: rank, repo (link), stars gained this week, total stars, one line (card's "what it is" or description), topic badges, card link. No ratings (Q-027).
4. CLI `leaderboard`.

## Acceptance criteria

- [x] AC-1: Top 10 by stars gained over 7 days; repos without two snapshots are skipped; newer repos count from their first snapshot and carry `since`.
- [x] AC-2: Job scheduled Mondays 07:35; one leaderboard per week; a second build is a no-op.
- [x] AC-3: `GET /api/leaderboard/latest` returns the entries with card summaries; `POST /api/leaderboard/build` builds now.
- [x] AC-4: Leaderboard page renders it (or an empty state with Build now); no console errors; typecheck and build pass.

## Out of scope

Comparing past weeks (v1); star-history charts (v1).

## Open questions

- [x] Q-026: Raw stars gained.
- [x] Q-027: Card links only, no ratings.

## QA

Test cases: [docs/qa/test-cases/006-weekly-leaderboard.md](../../docs/qa/test-cases/006-weekly-leaderboard.md)

## Change log

- 1.0 (2026-10-11): Created and approved from the user's answers to Q-026 and Q-027; implementation started.
- 1.0 (2026-10-11): Done. All ACs verified on the Reporters DB; all test cases pass.
