# Changelog

All notable changes to this project are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning: [Semantic Versioning](https://semver.org/) (`0.x` during the MVP).
Each entry names the spec it belongs to.

## [Unreleased]

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
