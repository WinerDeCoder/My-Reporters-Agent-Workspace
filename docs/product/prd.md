# Tech Radar — Product Requirements (MVP)

Owner: @Nguyen Phuoc Nguyen Phuo · Created 2026-10-04 · Updated 2026-10-10

## Problem

Keeping up with rising GitHub repos and AI news takes too long: trending pages are noisy, Hacker News moves fast, and most items need a README read to understand. I want a short daily brief that keeps only what matters to me and explains each item in plain words.

## Goal of the MVP

The MVP answers one question: **do I actually read and value a daily brief of rising repos and AI news?** It is the smallest thing that can answer that. The full [v1 requirements](v1-requirements.md) become the roadmap only if the answer is yes.

### Success criteria (after 2 weeks of daily use)

- I open the brief on most days (measured by `briefs.opened_at`).
- Most items get a thumbs up (measured by `feedback`).
- I want more from it (more sources, a dashboard), not less noise.

If not, fix scoring and cards before building anything else.

The **Stats** page (spec 007) measures these: brief opened on ≥ 10 of 14 days, ≥ 60 % of rated items 👍, ≥ 50 % of brief items rated (Q-028; thresholds and trial dates in `config.yaml` → `trial`).

## User

Just me: one developer, on my own machine, reading the brief once each morning.

## Scope

A small local web app is the whole interface: four pages, nothing more until v1.

| Area | In the MVP | Waits for v1 |
| --- | --- | --- |
| Sources | GitHub Trending, GitHub API star snapshots, Hacker News | HF Daily Papers, RSS blogs |
| Processing | Dedupe, simple rule-based score, cards for the top ~8 | Embeddings, learned relevance, classification |
| Delivery | Daily brief, weekly leaderboard (web pages) | Alerts with caps and quiet hours, push |
| Interface | 4 pages: Today, Leaderboard, Card, Stats | Full dashboard (8 pages), chat, deep dives |
| Personalization | Interest keywords in `config.yaml`; thumbs up/down | Watches, Saved / Playbook |
| Content | Repos and AI news | Tip of the day, papers |
| Storage | PostgreSQL (pgvector image) | pgvector embeddings |

## Core use cases

1. **Morning brief.** I open the Today page and see a top story, 3–5 rising repos and 2–3 news items, readable in two minutes.
2. **Understand an item.** I open its card: what it is, the problem it solves, what's special, whether it's worth trying, and its signals.
3. **Weekly leaderboard.** On Mondays I see the top 10 repos by stars gained over the last 7 days.
4. **Rate items.** I give each item 👍 or 👎; it feeds the success check and nudges future scores.
5. **Check the experiment.** A Stats page shows whether the MVP is working.

The detailed, numbered requirements are in [requirements.md](requirements.md). The build order is in [roadmap.md](roadmap.md).

## Out of scope for the MVP

Everything in the "Waits for v1" column above, plus multi-user accounts, hosting on a server, and mobile access.

## Open questions

Tracked in the [Q&A log](../qa/questions.md):

- [ ] Q-005: Starting interest keywords
- [ ] Q-006: Brief time
- [ ] Q-007: OpenAI model for cards
