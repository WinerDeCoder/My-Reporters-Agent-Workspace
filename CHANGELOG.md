# Changelog

All notable changes to this project are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning: [Semantic Versioning](https://semver.org/) (`0.x` during the MVP).
Each entry names the spec it belongs to.

## [Unreleased]

### Added

- QA area `docs/qa/`: Q&A log (`Q-NNN`, linked to specs, REQ-IDs and modules), test strategy, per-feature test cases with last results (`TC-NNN-NN`), generated traceability matrix; `STATUS.md` gains Tests and Quality sections; new `/qa` command.
- GitHub collectors (spec 001, in progress): Trending scraper and GitHub API star snapshots, scheduled daily (Trending 07:10, snapshots 07:20), rate-limit aware; `app/momentum.py` (stars/day); CLI `python -m app.cli collect trending|github` and `momentum --top N`.

- Rising repos page (spec 008): every tracked repo with stars and stars/day, search, language filter and sort; collector status panel on Today and Rising repos; `collector_runs` table (migration 0002) recording every job run; `GET /api/repos`, `GET /api/collectors/status`; favicon.

- Hacker News collector (spec 002): front page + stories > 100 points from the last 26 h, daily at 07:00; GitHub-linked stories become tracked repos; weekly prune of old stories and untracked repos' snapshots; News page (search, sort by points/hour); `GET /api/news`; CLI `collect hn`, `prune`.

- Scoring (spec 003): interest topics with editable term lists (agents, mcp, claude, skills, new llm models), repo score = stars/day × topic boost, news score = points/hour × topic boost for AI/dev stories only, repeat and 👎 penalties (active once briefs/feedback exist); "For you" sort and topic badges on Rising repos and News, "AI/dev only" toggle; CLI `top`.

- Cards (spec 004): gpt-6-luna writes what it is / problem / what's special / worth trying for the top 5 repos and top 3 AI/dev stories daily at 07:25, from the README or article text (title fallback marked limited); cached by source hash; "Write card" on any item; `llm_usage` table (migration 0003) with a 3M-token monthly cap; usage line in the status panel; CLI `cards`, `usage`; `GET/POST /api/cards/{type}/{id}`, `GET /api/llm/usage`.

- Daily brief (spec 005): built at 07:30 (Q-006) with a top story (#1 repo, Q-025), rising repos #2–#5 and the top 3 AI/dev stories, each with its card line; Today page with 👍/👎 (save, switch, clear) and `opened_at` on first view; "Build today's brief now"; repeat and 👎 penalties now live; prune keeps items referenced by a brief; `GET /api/briefs/today`, `POST /api/briefs/today/build`, `POST /api/feedback`; CLI `brief`.

### Changed

- `llm.generate()` returns token usage with the parsed result; `monthly_budget_usd` replaced by `monthly_token_cap` (Q-023).
- Backend binds to 127.0.0.1 only (`fastapi run --host 127.0.0.1`, Q-018). The database is the **Reporters** DB on the local PostgreSQL 18 (ADR-0005, supersedes ADR-0002); the optional Docker Compose Postgres now uses host port 127.0.0.1:5433 so it can't clash with a local install (Q-024).
- Interest boost raised to 2.0 per topic, cap 5.0 (Q-019); `config.yaml` model set to `gpt-6-luna` (Q-007).
- Collectors run once a day at fixed times from `config.yaml` (`run_at`: HN 07:00, Trending 07:10, snapshots 07:20; prune Mondays 07:40) instead of every 6 h / hourly; on startup a job runs only if its last success is older than 20 h (`catch_up_after_hours`), so restarts no longer trigger every collector (Q-014).
- Scheduler jobs defined in one table (`JOBS`, `job_specs`, `CATCH_UP_DELAY`); status panel labels and units per job.
- `config.yaml`: `interests.keywords` replaced by `interests.topics` + `ai_dev_terms`; new `scoring` section. Momentum looks back 72 h (was 48 h) so a missed daily snapshot doesn't hide stars/day.
- CLI `collect` runs are now recorded in `collector_runs` like scheduled runs; `momentum` shares its query with the API (`app/repo_stats.py`).
- `selectolax` pinned to `>=1.0` and switched to its `lexbor` backend (the old backend was removed in 1.0).

## [0.1.0] - 2026-10-10

### Added

- Project skeleton: Docker Compose (Postgres 17, pgvector image), `config.yaml`, `.env.example`, FastAPI app with in-process scheduler and `/api/health`, SQLAlchemy models and Alembic migration for the 6 MVP tables, React + Vite + TypeScript shell with 4 pages (spec 000).
- `backend/app/llm.py`: OpenAI client with a structured-output helper; all model settings in `config.yaml` → `llm` (spec 000).
- Project docs and workflow: `CLAUDE.md`, PRD, numbered requirements, roadmap, architecture overview, data model, API list, ADRs 0001–0004, spec template, `STATUS.md` generator, Stop-hook tracking check, slash commands.

### Changed

- LLM provider switched from Anthropic to OpenAI ([ADR-0004](docs/architecture/decisions/0004-openai-for-cards.md)) (spec 000).
- `requirements/` folder replaced by `docs/product/` (MVP doc split into `prd.md`, `requirements.md` and `roadmap.md`).

[Unreleased]: https://github.com/WinerDeCoder/My-Reporters-Agent-Workspace/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/WinerDeCoder/My-Reporters-Agent-Workspace/releases/tag/v0.1.0
