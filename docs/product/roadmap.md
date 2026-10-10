# Tech Radar — Roadmap

Each step ends with something I can run and check. Each step is one feature spec under `specs/`. Live progress is in [STATUS.md](../../STATUS.md).

## Milestone: MVP (v0.x)

| # | Spec | Delivers | Requirements | Target version |
| --- | --- | --- | --- | --- |
| 000 | Skeleton | Repo, Docker Compose (Postgres), config, schema + migration, FastAPI app, React shell, LLM client | NFR-001, 002, 003, 006 | 0.1.0 |
| 001 | GitHub collectors | Trending scraper + API star snapshots; check stars-per-day after a day of runs | COL-001, 002, 005, NFR-004 | 0.2.0 |
| 002 | HN collector | Top stories, keyword filter, GitHub links as candidates, weekly prune | COL-003, 004, 006 | 0.3.0 |
| 003 | Scoring | Repo and news scores; CLI prints today's top list for an eyeball check | SCO-001, 002, 003 | 0.4.0 |
| 004 | Cards | LLM prompt, structured output, cache, budget cap, Card page | CRD-001…005, NFR-005 | 0.5.0 |
| 005 | Daily brief | Built at 07:00 with catch-up; Today page with 👍/👎 and `opened_at` | BRF-001…004, FBK-001 | 0.6.0 |
| 006 | Weekly leaderboard | Monday leaderboard from 7 days of snapshots; Leaderboard page | LDB-001 | 0.7.0 |
| 007 | Stats | Stats page for the success check | FBK-002 | 0.8.0 |
| — | **2-week trial** | Live with it, tune keywords and the card prompt, then decide on v1 | PRD success criteria | — |

Spec numbers are reserved now so they stay stable; each spec folder is created when work on it starts.

## Milestone: v1 (1.0.0) — only if the MVP succeeds

Source: [v1-requirements.md](v1-requirements.md). In rough order: more sources (HF Daily Papers, RSS), embeddings and learned relevance, watches, full dashboard, alerts, chat and deep dives.
