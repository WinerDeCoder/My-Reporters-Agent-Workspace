# Tech Radar — MVP

Oct 4, 2026 · @Nguyen Phuoc Nguyen Phuo

## Goal

The MVP answers one question: do I actually read and value a daily brief of rising repos and AI news? It is the smallest thing that can answer that, built in a weekend or two; the full v1 requirements doc becomes the roadmap only if the answer is yes.

It worked if, after 2 weeks of daily use:

- I open the brief on most days.
- Most items get a thumbs up.
- I want more from it (more sources, a dashboard), not less noise.

If not, fix scoring and cards before building anything else.

## Scope

A small local web app (React frontend + FastAPI backend) is the whole interface: four pages, nothing more until v1.

| Area | In the MVP | Waits for v1 |
| --- | --- | --- |
| Sources | GitHub Trending, GitHub API star snapshots, Hacker News | HF Daily Papers, RSS blogs |
| Processing | Dedupe, simple score, cards for the top \~8 | Embeddings, learned relevance |
| Delivery | Daily brief, weekly leaderboard (web pages) | Alerts with caps and quiet hours |
| Interface | 4 pages: Today, Leaderboard, Card, Stats | Full dashboard (8 pages), chat, deep dives |
| Personalization | Interest keywords in a config file; thumbs up/down | Watches with pages, Saved / Playbook |
| Content | Repos and AI news | Tip of the day |
| Storage | PostgreSQL (pgvector image, ready for embeddings) | pgvector embeddings |

## Sources

Three collectors, each running on its own schedule and writing to the database; one failing never stops the others.

| Collector | What it gets | How | How often |
| --- | --- | --- | --- |
| GitHub Trending | Repo names from the daily and weekly trending pages (all languages + Python, TypeScript) | Scrape the HTML page | Every 6 h |
| GitHub API | For every candidate repo: stars, description, topics, language, license, README | REST API with a personal token | Every 6 h |
| Hacker News | Top stories: title, URL, points, comments; GitHub links become repo candidates | Algolia HN Search API | Hourly |

A repo is a **candidate** once it appears on Trending or in an HN link. Candidates get a star snapshot every run for 30 days, which is what makes stars-per-day and the weekly leaderboard possible.

## Scoring and cards

Scoring is simple rules, no ML; only the top items cost an LLM call.

**Repo score** = stars gained in the last 24 h, boosted when the repo matches an interest keyword, lowered if it was already in a brief in the last 7 days.

**News score** = HN points per hour since posting, boosted on keyword match, AI and dev topics only (keyword filter).

Each morning the top \~5 repos and top \~3 news items get a card. The card is written by an LLM from the README or article text:

- **What it is:** one sentence, no jargon.
- **Problem it solves:** who has this pain.
- **What's special:** the one idea that sets it apart.
- **Worth trying?:** effort, maturity, license.
- **Signals:** stars, stars gained, HN points, links.

The card prompt lives in one file so it is easy to tune. Cards are cached; a repo gets a new card only if its README changes a lot.

## Daily brief and weekly leaderboard

One brief each morning on the **Today** page, short enough to read in two minutes; each item links to its full card page.

**Daily brief** (built every day at 07:00 UTC+7; if the machine was asleep, built on next startup): a top story, then 3 to 5 rising repos, then 2 to 3 news items. Sample layout:

```text
Tech Radar · Mon 5 Oct

TOP STORY
<title> — <one line: what it is and why it matters> [card]

RISING REPOS
1. owner/repo  +<stars gained> today (<total> total)
   <what it is, one line> [card]
2. ...

NEWS
• <headline> — <one line> (<points> pts on HN) [link]

[👍] [👎] under each item
```

**Weekly leaderboard** (Mondays, 07:00 UTC+7, on the Leaderboard page): the top 10 repos by stars gained over the last 7 days, each with stars gained, total stars and one line on what it is.

## Feedback

Ratings happen right on the brief, so the data for the success check collects itself.

- Each item has 👍 and 👎 buttons; a click is saved with the item and time.
- Opening the Today page records `opened_at` on the brief, which replaces "I open the message" now that there is no push.
- A **Stats** page shows the last 14 days: briefs built, briefs opened, items rated, share of thumbs up.
- A 👎 also lowers future scores for repos and stories with the same keywords (simple rule, tuned by hand).

## Data

Six PostgreSQL tables; star snapshots are the most important, since momentum comes from them.

| Table | Columns |
| --- | --- |
| repos | full\_name, description, topics, language, license, readme\_hash, first\_seen, last\_seen |
| repo\_snapshots | repo, taken\_at, stars, forks |
| news\_items | hn\_id, title, url, points, comments, posted\_at, linked\_repo |
| cards | item\_type, item\_id, content (JSONB), model, source\_hash, created\_at |
| briefs | type (daily or weekly), date, items (JSONB), created\_at, opened\_at |
| feedback | item\_type, item\_id, rating, brief\_id, rated\_at |

Raw HN items older than 30 days and snapshots of repos that never scored are pruned weekly.

## Setup

Runs locally on my own machine. One backend process runs the scheduler and the API and serves the built frontend; only Postgres runs in Docker.

| Part | Choice |
| --- | --- |
| Backend | Python 3.12+, FastAPI, managed with uv |
| Scheduler | APScheduler inside the FastAPI process, plus a catch-up on startup |
| HTTP + scraping | httpx + tenacity + selectolax |
| Database | PostgreSQL 17 (pgvector image) via Docker Compose; SQLAlchemy 2.0 async + asyncpg; Alembic migrations |
| LLM | Claude (`claude-opus-5-5`, effort low) via the official `anthropic` SDK, structured output into a `Card` model; prompt in `backend/prompts/card.md` |
| Frontend | React + Vite + TypeScript, Tailwind CSS, TanStack Query, React Router |
| Run modes | Dev: Vite on :5173 proxying to FastAPI on :8000. Daily: FastAPI serves `frontend/dist` on :8000 |

Config lives in one `config.yaml`: interest keywords, brief time, top-N counts, trending languages, Claude model and budget. Secrets (GitHub token, Anthropic API key, database URL) live in `.env`.

Cost stays small: about 8 card calls a day, with a monthly budget cap in config. The GitHub token allows 5,000 API requests per hour, far above what 6-hourly snapshots need.

## Build steps

Each step ends with something I can run and check.

- [x] **Skeleton:** repo, Docker Compose (Postgres), config.yaml, .env, schema + Alembic migration, logging, FastAPI app, React shell.
- [ ] **GitHub collectors:** Trending scraper + API snapshots; check that stars-per-day looks right after a day of runs.
- [ ] **HN collector:** top stories, keyword filter, GitHub links added as repo candidates.
- [ ] **Scoring:** repo and news scores; print today's top list to the terminal and sanity-check it by eye.
- [ ] **Cards:** Claude prompt, structured output, cache, Card page.
- [ ] **Today page:** daily brief built at 07:00 (catch-up on startup), with links and 👍/👎 buttons.
- [ ] **Weekly leaderboard:** Leaderboard page from 7 days of snapshots.
- [ ] **Stats:** Stats page.
- [ ] **Live with it for 2 weeks**, tune keywords and the card prompt, then decide on v1.

## Open questions

- [x] Stack: Python backend (FastAPI) + React frontend.
- [x] LLM: Claude via the `anthropic` SDK. Budget cap: start at $15/month in config.
- [x] Runs locally on my own machine.
- [ ] My starting interest keywords (for example: agents, MCP, Claude, coding assistants, small models).
- [ ] Brief time: 07:00 UTC+7, or another time?
