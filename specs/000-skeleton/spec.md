---
id: 000
title: Project skeleton
status: done
version: 1.2
requirements: [REQ-NFR-001, REQ-NFR-002, REQ-NFR-003, REQ-NFR-006]
target_release: 0.1.0
created: 2026-10-04
updated: 2026-10-10
---

# 000 — Project skeleton

*Written after the fact (2026-10-10) to record work done before the spec process existed.*

## Why

Every later feature needs a running backend, a database with the MVP schema, a frontend shell and one place for settings.

## What (behavior)

- Postgres starts with one Docker Compose command.
- The backend starts, runs the (empty) scheduler, and answers `/api/health` with API and DB status.
- The frontend shows a Today page with system status and placeholder Leaderboard / Stats / Card pages.
- Secrets come from `.env`; all other settings from `config.yaml`, validated at startup.
- One module (`llm.py`) wraps the LLM client, configured from `config.yaml` → `llm`.

## Acceptance criteria

- [x] AC-1: `docker compose up -d db` then `uv run alembic upgrade head` creates the 6 MVP tables.
- [x] AC-2: `GET /api/health` returns `{"status": "ok", "db": <bool>}` even when the DB is down.
- [x] AC-3: `npm run dev` shows the Today page with system status.
- [x] AC-4: `ruff check` and `pytest` pass.

## Out of scope

Collectors, scoring, cards, brief: specs 001–007.

## QA

Test cases: [docs/qa/test-cases/000-skeleton.md](../../docs/qa/test-cases/000-skeleton.md). TC-000-04 (migration on a real DB) and TC-000-05 (Today page in a browser) were never run: the spec was closed before QA tracking existed. They'll be run during spec 001 setup.

## Change log

- 1.2 (2026-10-10): QA test cases recorded after the fact; 2 of 6 still to run (see QA).
- 1.1 (2026-10-10): LLM switched from Anthropic to OpenAI; `llm` config section expanded; `llm.py` added ([ADR-0004](../../docs/architecture/decisions/0004-openai-for-cards.md)).
- 1.0 (2026-10-04): Skeleton built: Compose, config, schema + migration, FastAPI, React shell.
