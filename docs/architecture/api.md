# Tech Radar — API

**Source of truth:** FastAPI's OpenAPI schema. With the backend running, see http://localhost:8000/docs (interactive) or `/openapi.json`. The frontend generates its types from it with `npm run gen:api`. This page lists the endpoints and conventions; update it in the same commit as any route change.

## Conventions

- All routes live under `/api`. Everything else is served by the SPA.
- JSON in and out; responses are Pydantic models (typed in OpenAPI).
- Dates are ISO 8601; timestamps include the timezone offset.
- Errors use FastAPI's default shape: `{"detail": "..."}` with a 4xx/5xx status.
- No auth: the app only listens on localhost (`fastapi run --host 127.0.0.1`, Q-018).

## Endpoints

| Method | Path | Purpose | Spec | Status |
| --- | --- | --- | --- | --- |
| GET | `/api/health` | API up + DB reachable (`{status, db}`) | 000 | done |
| GET | `/api/repos` | Tracked repos, highest stars/day first: name, url, description, language, topics, license, stars, `stars_per_day` (null until 6 h of history), snapshots, first/last seen; `score`, `matched_topics` (spec 003) | 008, 003 | done |
| GET | `/api/news?days=7` | HN stories posted in the last `days` (1–30) days, "For you" order (score, then points/hour): title, url (null for Ask HN), domain, hn_url, points, comments, posted_at, points_per_hour, linked_repo; `matched_topics`, `ai_dev`, `score` (spec 003) | 002, 003 | done |
| GET | `/api/collectors/status` | Per job: `last_run` (`started_at`, `finished_at`, `ok`, `result`, `error`) and `next_run` (null if the scheduler isn't running) | 008 | done |
| GET | `/api/briefs/today` | Latest daily brief; sets `opened_at` on first view | 005 | planned |
| GET | `/api/briefs/{date}` | Daily brief for a date | 005 | planned |
| GET | `/api/leaderboard/latest` | Latest weekly leaderboard | 006 | planned |
| GET | `/api/cards/{item_type}/{item_id}` | Full card for a repo or news item | 004 | planned |
| POST | `/api/feedback` | Save a 👍/👎 (`{item_type, item_id, rating, brief_id}`) | 005 | planned |
| GET | `/api/stats?days=14` | Success-check numbers | 007 | planned |
