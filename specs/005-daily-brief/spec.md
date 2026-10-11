---
id: 005
title: Daily brief
status: in-progress
version: 1.0
requirements: [REQ-BRF-001, REQ-BRF-002, REQ-BRF-003, REQ-BRF-004, REQ-FBK-001, REQ-COL-006]
target_release: 0.6.0
created: 2026-10-11
updated: 2026-10-11
---

# 005 — Daily brief

## Why

This is the MVP's whole point: one short brief each morning, readable in two minutes, rated item by item. The success check (open it most days, mostly 👍) needs the brief, `opened_at` and ratings.

## What (behavior)

1. **Build** (daily at `brief_time` 07:30, Q-006): one `briefs` row (type `daily`, local date) with, in order:
   - **Top story**: the #1 repo by score (Q-025);
   - **Rising repos**: repos #2–#5 by score;
   - **News**: the top 3 AI/dev stories by score.
   Each entry stores `section`, `item_type`, `item_id` and the signals at build time (title, url, stars, stars/day, points…, topics, score). Unscored items are never included. A brief is built once per day and never rebuilt.
2. **Catch-up** (REQ-BRF-002): on startup, if it's past `brief_time` and today's brief is missing, build it after the collector and card catch-ups (~5 min). Starting before `brief_time` builds nothing early.
3. **Today page** shows the latest daily brief: date, top story (larger), rising repos, news; each item with the card's "what it is" line (or the description), signals, topic badges, a card link and 👍/👎. The first view sets `opened_at` (REQ-BRF-004). If no brief exists yet, it says when the next one is built and offers "Build today's brief now".
4. **Feedback** (REQ-FBK-001): 👍/👎 saved per item and brief; clicking the selected one again clears it; clicking the other switches. The latest rating counts. Ratings feed the 👎 penalty in scoring (spec 003) from the next day on; items in a brief within 7 days get the repeat penalty.
5. **Prune** (REQ-COL-006): stories referenced by a brief are kept; snapshots are deleted only for untracked repos that never reached a brief.
6. **CLI** `brief` builds today's brief now (same rules).

## Acceptance criteria

- [x] AC-1: Item selection: top story = #1 repo; repos #2–#5; top 3 AI/dev stories; unscored items skipped; fewer candidates → shorter brief, no error.
- [x] AC-2: The brief job runs daily at 07:30; one brief per local date; a second build the same day does nothing.
- [x] AC-3: Startup after `brief_time` without today's brief builds it after the catch-ups; before `brief_time` nothing is built.
- [x] AC-4: `GET /api/briefs/today` returns the latest daily brief with items, card summaries and current ratings, and sets `opened_at` once.
- [x] AC-5: `POST /api/feedback` saves, switches and clears ratings; the Today page reflects them after reload.
- [x] AC-6: Repeat and 👎 penalties now apply from real briefs/feedback (spec 003 signals).
- [x] AC-7: Prune keeps stories referenced by a brief and snapshots of repos that reached a brief.
- [x] AC-8: Today page renders the brief (or the empty state + Build now); no console errors; typecheck and build pass.

## Out of scope

- Weekly leaderboard (spec 006); stats page (spec 007).
- Push notifications; browsing past briefs (later).

## Open questions

Logged in [docs/qa/questions.md](../../docs/qa/questions.md).

- [x] Q-006: Brief at 07:30.
- [x] Q-025: Top story = #1 repo.

## QA

Test cases: [docs/qa/test-cases/005-daily-brief.md](../../docs/qa/test-cases/005-daily-brief.md)

## Change log

- 1.0 (2026-10-11): Implemented and verified live; first real brief built for 2026-10-11. The brief job is always caught up at startup (the build is idempotent and time-checked), since an age rule could miss a day.
- 1.0 (2026-10-11): Created and approved from the user's answers to Q-006 and Q-025; implementation started.
