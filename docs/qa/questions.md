# Q&A log

Questions asked to the user, with the suggestion given, the answer, and where the decision was recorded. Format and rules: [README.md](README.md).

### Q-001 — Track window for star snapshots

- **Status:** answered
- **Asked:** 2026-10-10
- **Context:** spec [001](../../specs/001-github-collectors/spec.md) · REQ-COL-002 · `app/collectors/github_api.py`
- **Question:** A candidate repo gets a star snapshot every run for `track_days` (30). Counted from when it was last seen on Trending/HN, or from when it was first seen?
- **Suggestion:** Last seen: repos that keep trending stay tracked, fading ones drop off on their own. Alternative: first seen (fixed 30-day window, even if still trending).
- **Answer:** Last seen. (2026-10-10)
- **Recorded in:** spec 001 v1.0 change log; REQ-COL-002 note.

### Q-002 — GitHub Trending languages

- **Status:** answered
- **Asked:** 2026-10-10
- **Context:** spec [001](../../specs/001-github-collectors/spec.md) · REQ-COL-001 · `app/collectors/github_trending.py`, `config.yaml`
- **Question:** Which Trending language pages should the collector read?
- **Suggestion:** Keep all languages + Python + TypeScript (6 pages per run). Alternatives: add Rust and Go (10 pages), or all-languages only (2 pages).
- **Answer:** All + Python + TypeScript, unchanged. (2026-10-10)
- **Recorded in:** spec 001 v1.0 change log; `config.yaml` unchanged.

### Q-003 — First collector run after startup

- **Status:** superseded (by Q-014, 2026-10-11)
- **Asked:** 2026-10-10
- **Context:** spec [001](../../specs/001-github-collectors/spec.md) · REQ-COL-005 · `app/scheduler.py`
- **Question:** Should collectors first run shortly after the app starts, or only once the interval has passed?
- **Suggestion:** About 1 minute after startup, then every `every_hours`, so each laptop wake/start refreshes data. Alternative: only on schedule (first run 6 h after start).
- **Answer:** Shortly after startup. (2026-10-10)
- **Recorded in:** spec 001 v1.0 (AC-8); REQ-COL-005 note.

### Q-004 — What "QA" covers

- **Status:** answered
- **Asked:** 2026-10-10
- **Context:** process · `CLAUDE.md`, `docs/qa/`
- **Question:** Does QA mean a Q&A log, quality assurance (test plans/cases), or both?
- **Suggestion:** Both, in one `docs/qa/` area, each entry pointing to specs, REQ-IDs and modules.
- **Answer:** Both. (2026-10-10)
- **Recorded in:** `docs/qa/README.md`; `CLAUDE.md` (Where things live, Definition of Done).

### Q-005 — Starting interest keywords

- **Status:** open
- **Asked:** 2026-10-04
- **Context:** spec 003 (scoring) · REQ-SCO-001, REQ-SCO-002 · `config.yaml` → `interests.keywords`
- **Question:** Which keywords should boost scores at the start?
- **Suggestion:** Current draft: agents, mcp, claude, coding assistant, small models, llm. Add anything you follow closely; keep it under ~15 so the boost stays meaningful.
- **Answer:** —
- **Recorded in:** —

### Q-006 — Brief time

- **Status:** open
- **Asked:** 2026-10-04
- **Context:** spec 005 (daily brief) · REQ-BRF-001 · `config.yaml` → `brief_time`
- **Question:** Build the daily brief at 07:00 UTC+7, or another time?
- **Suggestion:** 07:30, right after the daily collection (07:00–07:20, Q-014) so the brief uses fresh data; the startup catch-up covers mornings when the laptop was off. (Updated 2026-10-11; was 07:00.)
- **Answer:** —
- **Recorded in:** —

### Q-007 — OpenAI model for cards

- **Status:** open
- **Asked:** 2026-10-10
- **Context:** spec 004 (cards) · REQ-CRD-001, REQ-CRD-002 · `config.yaml` → `llm.model`, `app/llm.py`
- **Question:** Which OpenAI model should write the cards?
- **Suggestion:** Start with a small, cheap model (`gpt-5-mini` is the placeholder) and judge card quality during the 2-week trial; confirm the exact id your key can use.
- **Answer:** —
- **Recorded in:** —

### Q-008 — What the frontend should show before scoring and cards exist

- **Status:** answered
- **Asked:** 2026-10-11
- **Context:** new spec (frontend) · REQ-COL-002, REQ-BRF-003 · `frontend/src/pages/`, `app/api/`, `app/momentum.py`
- **Question:** The collectors now fill the DB (60 repos, 120 snapshots), but no page shows data: the roadmap's first content page (Today, spec 005) needs scoring (003) and cards (004). What should the frontend show now?
- **Suggestion:** A **Rising repos** page now (pulled forward from the v1 dashboard): every tracked repo with stars, stars/day once 6 h of history exists, description, language, topics, GitHub link, sortable; plus collector status (last run, counts). Alternatives: a provisional Today brief from raw momentum, or stay in roadmap order (HN collector next) and leave the UI for spec 005.
- **Answer:** Rising repos page. (2026-10-11)
- **Recorded in:** spec [008](../../specs/008-rising-repos-page/spec.md); REQ-UI-001; roadmap.

### Q-009 — Show collector status in the UI

- **Status:** answered
- **Asked:** 2026-10-11
- **Context:** spec [008](../../specs/008-rising-repos-page/spec.md) · REQ-COL-007, REQ-UI-002 · `app/scheduler.py`, `app/models.py`, `frontend/src/components/CollectorStatus.tsx`
- **Question:** Should the frontend show collector status (last run, repos found, failures), so it's visible that background jobs work?
- **Suggestion:** Yes, a small panel; needs a `collector_runs` table (new migration) recording every job run. Alternative: rely on backend logs.
- **Answer:** Yes, small panel. (2026-10-11)
- **Recorded in:** spec 008; REQ-COL-007, REQ-UI-002; data model.

### Q-010 — Which Hacker News stories to collect

- **Status:** answered
- **Asked:** 2026-10-11
- **Context:** spec [002](../../specs/002-hn-collector/spec.md) · REQ-COL-003 · `app/collectors/hacker_news.py`
- **Question:** Which HN stories should the hourly collector fetch?
- **Suggestion:** The current front page (~30 stories) every hour plus any story above 100 points from the last 24 h, so strong stories that left the front page between runs aren't missed (2 Algolia requests per run). Alternatives: front page only; or the official top-500 list (500+ requests per run).
- **Answer:** Front page + stories above 100 points from the last 24 h. (2026-10-11)
- **Recorded in:** spec 002 v1.0; REQ-COL-003 note.

### Q-011 — Topic filter at collection or at scoring

- **Status:** answered
- **Asked:** 2026-10-11
- **Context:** spec [002](../../specs/002-hn-collector/spec.md) · REQ-COL-003, REQ-SCO-002 · `app/collectors/hacker_news.py`, `app/scoring.py`
- **Question:** Store every collected story, or only those matching AI/dev keywords?
- **Suggestion:** Store every story (a few hundred rows a week, pruned after 30 days) and filter in scoring (spec 003), as REQ-SCO-002 already says; keyword changes then apply to past stories too. Alternative: drop non-matching stories at collection.
- **Answer:** Store all, filter in scoring. (2026-10-11)
- **Recorded in:** spec 002 v1.0; REQ-COL-003 note; REQ-SCO-002 unchanged.

### Q-012 — Show HN stories in the UI now

- **Status:** answered
- **Asked:** 2026-10-11
- **Context:** spec [002](../../specs/002-hn-collector/spec.md) · REQ-UI-003 (proposed) · `frontend/src/pages/`, `app/api/`
- **Question:** Should collected stories get a simple page now, like Rising repos, or wait for the daily brief (spec 005)?
- **Suggestion:** A small News page now (title, link, points, comments, age, linked-repo badge, points/hour sort), same pattern as Rising repos; it lets you eyeball the feed before scoring. Alternative: no UI until spec 005 (the HN job still appears in the status panel).
- **Answer:** Small News page now. (2026-10-11)
- **Recorded in:** spec 002 v1.0; new REQ-UI-003; roadmap.

### Q-013 — Pruning before briefs exist

- **Status:** answered
- **Asked:** 2026-10-11
- **Context:** spec [002](../../specs/002-hn-collector/spec.md) · REQ-COL-006 · `app/collectors/prune.py`, `app/scheduler.py`
- **Question:** REQ-COL-006 prunes HN items older than 30 days and snapshots of repos that "never reached a brief". No briefs exist yet, so the second rule would match every repo. Prune what now?
- **Suggestion:** Weekly prune of HN items older than 30 days now; for snapshots, only delete those of repos no longer tracked (`last_seen` older than `track_days`), and add the "never in a brief" condition in spec 005. Alternative: defer all pruning to spec 005.
- **Answer:** HN items older than 30 days + snapshots of untracked repos only; brief rule in spec 005. (2026-10-11)
- **Recorded in:** spec 002 v1.0; REQ-COL-006 changed.

### Q-014 — How often collectors run

- **Status:** answered
- **Asked:** 2026-10-11
- **Context:** specs [001](../../specs/001-github-collectors/spec.md), [002](../../specs/002-hn-collector/spec.md) · REQ-COL-001, REQ-COL-002, REQ-COL-003, REQ-COL-005, REQ-COL-006 · `app/scheduler.py`, `config.yaml`, `app/runs.py`
- **Question:** Raised by the user: Trending and snapshots every 6 h and HN hourly is more than needed; run them daily instead?
- **Suggestion:** Daily at fixed times just before the brief rather than every 24 h from startup; on startup run a job only if its last successful run is older than ~20 h (replaces Q-003's run-on-every-start); widen HN's popular window to 26 h so daily runs overlap; weekly prune also only catches up if > 7 days old.
- **Answer:** Daily at 07:00 (Hacker News), 07:10 (GitHub Trending), 07:20 (star snapshots), with the startup catch-up. (2026-10-11)
- **Recorded in:** spec 001 v2.0, spec 002 v2.0 change logs; REQ-COL-001/002/003/005/006 notes; `config.yaml` `run_at`; supersedes Q-003; Q-006 suggestion moved to 07:30.
