---
id: 004
title: Cards
status: in-progress
version: 1.0
requirements: [REQ-CRD-001, REQ-CRD-002, REQ-CRD-003, REQ-CRD-004, REQ-CRD-005, REQ-NFR-005, REQ-UI-005]
target_release: 0.5.0
created: 2026-10-11
updated: 2026-10-11
---

# 004 — Cards

## Why

A ranked list of names isn't enough to decide what to read: each brief item needs a short, plain-language explanation. Cards turn a README or article into four answers (what it is, the problem it solves, what's special, is it worth trying) so the brief can be read in two minutes. Cost must stay small and predictable.

## What (behavior)

1. **Card content** (structured output from `gpt-6-luna`, English, Q-022): what it is, problem it solves, what's special, worth trying (effort, maturity, license). Signals (stars, stars/day, points, links) are shown from live data, not written by the LLM.
2. **Source text:** repos use their README; stories use the extracted article text (Q-021), or the linked repo's README for GitHub links; capped at ~12k characters. If no text can be fetched, the card is written from the title and marked **limited source**.
3. **Daily cards** (07:25, after collection and before the brief; startup catch-up if stale): the top 5 repos and top 3 AI/dev stories by score (Q-020).
4. **On demand:** the Card page offers **Write card** for any item without one (REQ-UI-005); Rising repos and News link to each item's card page and show which already have a card.
5. **Cache:** a card is reused while its source text hash is unchanged (REQ-CRD-003).
6. **Token cap:** every LLM call is logged in `llm_usage` (tokens in/out, model, purpose, item, ok/error). No call is made once the month's total reaches `llm.monthly_token_cap` (3M) (Q-023); the status panel shows usage this month.
7. **CLI:** `cards` (run the daily job now), `usage` (this month's tokens).

## Acceptance criteria

- [x] AC-1: A card for a repo and for a story is stored with all four fields filled (or "unclear"), plus source kind and limited flag.
- [x] AC-2: News source text comes from the article (or README for GitHub links); failed fetches fall back to the title with `limited: true`.
- [x] AC-3: Re-running card generation on unchanged sources makes zero LLM calls.
- [x] AC-4: With `monthly_token_cap: 0` no LLM call is made, the job finishes without error, and the API answers the button with a clear "cap reached" error.
- [x] AC-5: Every call writes an `llm_usage` row; the status panel shows tokens used this month vs the cap.
- [x] AC-6: The daily cards job is scheduled at 07:25 with startup catch-up and writes cards for the configured top items.
- [x] AC-7: Card page shows the card with live signals and source links; Write card works for an item without a card; lists show card status; no console errors; typecheck and build pass.
- [x] AC-8: Prompt in `backend/prompts/card.md` and all model settings in `config.yaml`; changing them needs no code change.

## Out of scope

- The brief itself (spec 005); deep dives and chat (v1).
- Regenerating cards on small README edits (any hash change regenerates; tune later if costly).

## Open questions

Logged in [docs/qa/questions.md](../../docs/qa/questions.md).

- [x] Q-007: gpt-6-luna.
- [x] Q-020: Daily top items + Write card button.
- [x] Q-021: Article text via trafilatura, README for GitHub links, title fallback.
- [x] Q-022: English.
- [x] Q-023: Token cap with an `llm_usage` table.

## QA

Test cases: [docs/qa/test-cases/004-cards.md](../../docs/qa/test-cases/004-cards.md)

## Change log

- 1.0 (2026-10-11): Implemented and verified live: 9 cards written (≈2.6k tokens each), cache and cap checks pass.
- 1.0 (2026-10-11): Created and approved from the user's answers to Q-007, Q-020…Q-023; a probe call confirmed gpt-6-luna supports structured output and reasoning effort; implementation started.
