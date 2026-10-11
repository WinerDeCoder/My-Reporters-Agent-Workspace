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

- **Status:** answered
- **Asked:** 2026-10-04
- **Context:** spec 003 (scoring) · REQ-SCO-001, REQ-SCO-002 · `config.yaml` → `interests.keywords`
- **Question:** Which keywords should boost scores at the start?
- **Suggestion:** Current draft: agents, mcp, claude, coding assistant, small models, llm. Add anything you follow closely; keep it under ~15 so the boost stays meaningful.
- **Answer:** agents, mcp, claude, skills, new llm models. (2026-10-11) How each is matched: Q-015.
- **Recorded in:** `config.yaml` → `interests`; spec 003.

### Q-006 — Brief time

- **Status:** open
- **Asked:** 2026-10-04
- **Context:** spec 005 (daily brief) · REQ-BRF-001 · `config.yaml` → `brief_time`
- **Question:** Build the daily brief at 07:00 UTC+7, or another time?
- **Suggestion:** 07:30, right after the daily collection (07:00–07:20, Q-014) so the brief uses fresh data; the startup catch-up covers mornings when the laptop was off. (Updated 2026-10-11; was 07:00.)
- **Answer:** —
- **Recorded in:** —

### Q-007 — OpenAI model for cards

- **Status:** answered
- **Asked:** 2026-10-10
- **Context:** spec 004 (cards) · REQ-CRD-001, REQ-CRD-002 · `config.yaml` → `llm.model`, `app/llm.py`
- **Question:** Which OpenAI model should write the cards?
- **Suggestion:** Start with a small, cheap model (`gpt-5-mini` is the placeholder) and judge card quality during the 2-week trial; confirm the exact id your key can use.
- **Answer:** gpt-6-luna. (2026-10-11) Verified available for the configured key via the models API; structured output and reasoning effort to be confirmed in spec 004.
- **Recorded in:** `config.yaml` → `llm.model`.

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

### Q-015 — How interest topics are matched

- **Status:** answered
- **Asked:** 2026-10-11
- **Context:** spec [003](../../specs/003-scoring/spec.md) · REQ-SCO-001, REQ-SCO-002 · `config.yaml` → `interests`, `app/scoring.py`
- **Question:** "new llm models" never appears literally, and "skills" alone also matches posts like "improve your coding skills". How should the 5 interests be matched against repo name/description/topics and HN titles?
- **Suggestion:** Each interest becomes a topic with a list of match terms, editable in `config.yaml`: agents (agent, agents, agentic, multi-agent), mcp (mcp, model context protocol), claude (claude, anthropic, claude code), skills (only with AI context: "agent skills", "claude skills", "skills" in a repo also tagged agents/claude/mcp), new llm models (model names and release words: gpt, gemini, llama, qwen, mistral, deepseek, grok, open weights, new model, release + llm). Whole-word, case-insensitive. Alternative: literal keyword match only.
- **Answer:** Topics + editable term lists; generic terms like "skills" only count alongside another topic. (2026-10-11)
- **Recorded in:** `config.yaml` → `interests.topics`; spec 003; REQ-SCO-001/002 notes.

### Q-016 — Which HN stories count as AI/dev

- **Status:** answered
- **Asked:** 2026-10-11
- **Context:** spec [003](../../specs/003-scoring/spec.md) · REQ-SCO-002 · `config.yaml` → `interests`, `app/scoring.py`
- **Question:** REQ-SCO-002 keeps only AI/dev stories for the news section. Should that filter be just your 5 interests (strict, few stories), or a broader AI/dev topic list with your interests as a boost?
- **Suggestion:** Broader: a configurable AI/dev list (ai, llm, ml, model, programming, open source, github, python, rust, typescript, database, compiler…) decides eligibility; your 5 interests boost ranking. Strict would often leave the news section empty.
- **Answer:** Broad AI/dev term list decides eligibility; the 5 interests boost. (2026-10-11)
- **Recorded in:** `config.yaml` → `interests.ai_dev_terms`; spec 003; REQ-SCO-002 note.

### Q-017 — Show scores in the UI now

- **Status:** answered
- **Asked:** 2026-10-11
- **Context:** spec [003](../../specs/003-scoring/spec.md) · REQ-SCO-001, REQ-SCO-002 · `frontend/src/pages/Repos.tsx`, `frontend/src/pages/News.tsx`, `app/api/`
- **Question:** Spec 003 originally only adds a CLI to print today's top list. Should Rising repos and News also get a "For you" sort with the score and matched-topic badges?
- **Suggestion:** Yes: default sort "For you" on both pages, topic badges on each item, and an "AI/dev only" toggle on News; it's the easiest way to judge the ranking before the brief uses it. Alternative: CLI only.
- **Answer:** Yes: "For you" sort, topic badges, "AI/dev only" toggle on News. (2026-10-11)
- **Recorded in:** spec 003; new REQ-UI-004.

### Q-018 — Improvements raised by Claude (2026-10-11)

- **Status:** answered
- **Asked:** 2026-10-11
- **Context:** process + ops · REQ-NFR-001, REQ-NFR-002 · `docker-compose.yml`, `README.md`, `docs/architecture/api.md`, `.gitattributes`, `frontend/src/api/`
- **Question:** Which of these should be done now?
  1. **Network exposure (bug vs docs):** `fastapi run` listens on all interfaces (0.0.0.0) and Compose publishes Postgres 5432 on all interfaces with password `radar`, so both are reachable from the local network; `api.md` says "only listens on localhost". Fix: `--host 127.0.0.1` and `127.0.0.1:5432:5432`.
  2. **Auto-start for the 2-week trial:** collection and the brief only happen while the backend runs. Add `start.ps1` + a Windows Task Scheduler task at logon (and Docker Desktop autostart).
  3. **Close-out and release:** specs 001/008/002/003 are effectively done but not closed; `morluto/rea` momentum verified against GitHub (79,356 stars now), so the soak check can close with 3 repos; then tag `v0.2.0`.
  4. **Dev hygiene:** `.gitattributes` (LF) to stop CRLF warnings; generate frontend types from OpenAPI (`npm run gen:api`) instead of hand-written ones; DB-backed integration tests against a separate test database.
- **Suggestion:** 1, 2 and 3 now (small, high value); 4 later.
- **Answer:** Do 1 (localhost only) now. 2 (auto-start), 3 (close-out + v0.2.0) and 4 (dev hygiene) not now; raise again later. (2026-10-11)
- **Recorded in:** `docker-compose.yml`, README, CLAUDE.md, `docs/architecture/overview.md`; REQ-NFR-001 note.

### Q-019 — Balance between momentum and interests

- **Status:** answered
- **Asked:** 2026-10-11
- **Context:** spec [003](../../specs/003-scoring/spec.md) · REQ-SCO-001 · `app/scoring.py`, `config.yaml` → `interests`
- **Question:** Raw stars/day dominates: one viral repo (+22,000/day) is 6× the next, and a repo with none of your topics (+3,600/day) ranks 2nd ahead of topic matches. Should momentum be damped so your topics matter more?
- **Suggestion:** Score = log(1 + stars/day) × topic boost: 22,000/day vs 1,500/day becomes ~10 vs ~7.3, so a 2-topic match (×2.25) beats an off-topic repo with 10× the stars/day. Same for news with points/hour. Alternatives: keep linear and raise the boost (e.g. 2.0/topic, cap 5), or keep as is.
- **Answer:** Stronger boost, linear: 2.0 per topic, cap 5.0. (2026-10-11)
- **Recorded in:** `config.yaml` → `interests.topic_boost` / `max_boost`; spec 003 v1.1; REQ-SCO-001 note.

### Q-020 — When cards are generated

- **Status:** answered
- **Asked:** 2026-10-11
- **Context:** spec [004](../../specs/004-cards/spec.md) · REQ-CRD-001, REQ-CRD-003, REQ-NFR-005 · `app/cards.py`, `app/scheduler.py`, `frontend/src/pages/`
- **Question:** Generate cards only for the daily top items, on demand for any item, or both?
- **Suggestion:** Both: a daily job at 07:25 (after collection, before the brief) writes cards for the top 5 repos + top 3 AI/dev stories; plus a "Write card" button on any item in Rising repos / News for one-off cards. Cached by source hash either way. Alternatives: daily top items only (cheapest); or automatically for every item opened (unpredictable cost).
- **Answer:** Daily top items at 07:25 + a "Write card" button on any item. (2026-10-11)
- **Recorded in:** spec 004; REQ-CRD-001 note; new REQ-UI-005.

### Q-021 — Source text for news cards

- **Status:** answered
- **Asked:** 2026-10-11
- **Context:** spec [004](../../specs/004-cards/spec.md) · REQ-CRD-001 · `app/cards.py`, `backend/pyproject.toml`
- **Question:** What should a news card be written from?
- **Suggestion:** Fetch the article and extract its main text (the `trafilatura` library), capped at ~12k characters; for stories linking a GitHub repo use the README; if the fetch fails (paywall, PDF), write a short card from the title and mark it "limited source". Alternative: title + domain only (cheap, but cards would be guesses).
- **Answer:** Article text via trafilatura (cap ~12k chars); README for GitHub-linked stories; title fallback marked limited. (2026-10-11)
- **Recorded in:** spec 004; REQ-CRD-001 note.

### Q-022 — Card language

- **Status:** answered
- **Asked:** 2026-10-11
- **Context:** spec [004](../../specs/004-cards/spec.md) · REQ-CRD-001 · `backend/prompts/card.md`, `config.yaml` → `llm`
- **Question:** Which language should cards be written in?
- **Suggestion:** English (sources are English, terms stay exact). Alternatives: Vietnamese; or a `card_language` setting in `config.yaml`.
- **Answer:** English. (2026-10-11)
- **Recorded in:** `backend/prompts/card.md`; spec 004.

### Q-023 — How the monthly LLM cap is measured

- **Status:** answered
- **Asked:** 2026-10-11
- **Context:** spec [004](../../specs/004-cards/spec.md) · REQ-CRD-004, REQ-NFR-005 · `config.yaml` → `llm`, `app/llm.py`
- **Question:** The cap is `monthly_budget_usd: 15`, but I can't verify gpt-6-luna's price. Cap by tokens, or by USD with prices you provide?
- **Suggestion:** Cap by tokens (e.g. 3M tokens/month, input + output), logged per call in a new `llm_usage` table; optional `price_per_million` in config adds a USD estimate if you fill it in. Alternative: USD cap only, with input/output prices you enter.
- **Answer:** Token cap (3M tokens/month) with an `llm_usage` table; optional prices for a USD estimate. (2026-10-11)
- **Recorded in:** `config.yaml` → `llm.monthly_token_cap`; REQ-CRD-004 changed; REQ-NFR-005 note.

### Q-024 — Which PostgreSQL the project uses (port 5432 clash)

- **Status:** answered
- **Asked:** 2026-10-11
- **Context:** setup · REQ-NFR-001 · `.env`, `docker-compose.yml`, ADR-0005
- **Question:** After Q-018, `docker compose up -d db` failed: PostgreSQL 18 installed on Windows (service `postgresql-x64-18`) holds port 5432. Move the Docker Postgres to another port, or stop the Windows service?
- **Suggestion:** Move the Docker Postgres to 5433. (Applied, then found to be the wrong premise: `.env` points to the database `Reporters` on the Windows PostgreSQL, which holds all the data; the Docker Postgres was never used. `.env` was pointed at 5433 for a few minutes and reverted.)
- **Answer:** The project's database is **Reporters**, on the user's own PostgreSQL. (2026-10-11) Keep using it; the Docker Postgres stays optional (host port 5433, stopped).
- **Recorded in:** ADR-0005 (supersedes ADR-0002); `.env` unchanged in the end (5432 / Reporters); `docker-compose.yml` + `.env.example` default 5433; README, CLAUDE.md, overview; REQ-NFR-001 note. The Windows PostgreSQL listens on 0.0.0.0:5432; the user accepts this (private network, 2026-10-11), no change.
