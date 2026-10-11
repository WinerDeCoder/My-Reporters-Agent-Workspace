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

- **Status:** answered
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
- **Suggestion:** 07:00, before a typical start of day; the startup catch-up covers mornings when the laptop was off.
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
