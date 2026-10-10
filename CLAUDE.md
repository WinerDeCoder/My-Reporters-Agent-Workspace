# CLAUDE.md

Guidance for Claude Code in this repository. Read this first, every session.

## Project

**Tech Radar**: a local web app that collects rising GitHub repos and Hacker News stories, scores them, writes short cards with an LLM (OpenAI), and shows a daily brief I rate with 👍/👎. Single user, runs on my Windows laptop. Currently building the **MVP** (v0.x).

## Start of every session

1. Read `STATUS.md`: released version, active spec, what's next, blockers.
2. Read the active spec's `spec.md`, `plan.md` and `tasks.md`.
3. Only then plan or write code. If the user's request isn't covered by a spec, say so and propose `/spec` (or `/change` for an existing one) before coding anything non-trivial.

## Where things live (one source of truth each)

| What | Where |
| --- | --- |
| Product goal, scope, success criteria | `docs/product/prd.md` |
| Numbered requirements (REQ-IDs) + status | `docs/product/requirements.md` |
| Build order / milestones | `docs/product/roadmap.md` |
| Post-MVP backlog | `docs/product/v1-requirements.md` |
| Architecture (containers, flows, deployment) | `docs/architecture/overview.md` |
| Data model explained | `docs/architecture/data-model.md` (truth = `backend/app/models.py` + migrations) |
| API list | `docs/architecture/api.md` (truth = FastAPI OpenAPI at `/docs`) |
| Decisions and why | `docs/architecture/decisions/NNNN-*.md` (ADRs) |
| Feature specs, plans, task checklists | `specs/NNN-name/{spec,plan,tasks}.md` |
| Q&A log: questions to the user, suggestions, answers | `docs/qa/questions.md` (`Q-NNN`) |
| Test strategy | `docs/qa/test-strategy.md` |
| Test cases per feature, with last result | `docs/qa/test-cases/NNN-name.md` (`TC-NNN-NN`) |
| REQ → spec → test → module map | `docs/qa/traceability.md` (generated) |
| Progress dashboard | `STATUS.md` (generated: `python scripts/status.py`) |
| Release history | `CHANGELOG.md` + git tags `vX.Y.Z` |
| Settings / secrets | `config.yaml` / `.env` (never commit `.env`) |

## Feature workflow (spec-driven)

1. **Spec** (`/spec`): write `specs/NNN-name/spec.md` from `specs/_template/` (status `draft`, version `0.1`). Link REQ-IDs. Stop for user review.
2. **Approve**: on user approval set `status: approved`, `version: 1.0`, add a change-log line.
3. **Plan** (`/plan`): write `plan.md`, `tasks.md` (`/tasks`) and `docs/qa/test-cases/NNN-name.md` (every acceptance criterion gets at least one test case). Stop for user review if the design has real choices.
4. **Implement**: set spec `in-progress` and its REQ-IDs `in-progress`. Work task by task; tick each task in `tasks.md` in the same change as the code. Keep tests and lint green; record test results (`/qa`).
5. **Done** (`/done`): run the Definition of Done below.

## Asking questions (Q&A)

Don't hesitate to ask: whenever a requirement is unclear, a product choice is needed, or there's a suggestion worth making, ask instead of guessing. Every such question:

1. gets a `Q-NNN` entry in `docs/qa/questions.md` (Context links spec, REQ-IDs and modules; Suggestion gives my recommendation and the options) **before** asking;
2. is asked with the AskUserQuestion tool where possible;
3. once answered: fill Answer (dated), set Status `answered`, apply the decision (spec change log, requirement note, ADR) and name that place in "Recorded in".

Specs list open questions as links to Q-IDs.

Small fixes that don't change behavior (typos, refactors, dependency bumps) need no spec, but still get a CHANGELOG line under `[Unreleased]` if user-visible.

## Definition of Done (a feature is not done until all are true)

- [ ] Every task in `tasks.md` is ticked (or struck through with a reason).
- [ ] Every acceptance criterion in `spec.md` is checked and was actually verified.
- [ ] `docs/qa/test-cases/NNN-name.md` exists, covers every AC, and every test case has a dated result; none is `fail`; any `not run`/`blocked` has the user's sign-off written in the spec change log.
- [ ] No open `Q-NNN` in `docs/qa/questions.md` still points at this spec.
- [ ] `cd backend; uv run ruff check . ; uv run ruff format --check . ; uv run pytest` pass. Frontend changes: `npm run typecheck`.
- [ ] Spec front matter: `status: done`, `updated:` today.
- [ ] Linked REQ-IDs in `requirements.md` set to `done`.
- [ ] Docs listed in the plan's "Docs to update" are updated (architecture, data model, API, README).
- [ ] `CHANGELOG.md` has a line under `## [Unreleased]` (Added / Changed / Fixed / Removed) naming the spec.
- [ ] `python scripts/status.py` was run (updates `STATUS.md` and `docs/qa/traceability.md`).
- [ ] Commit message follows Conventional Commits and names the spec, e.g. `feat(collectors): add GitHub trending + snapshots (spec 001)`.

## When something changes

- **Requirement or spec changes** (`/change`): edit in place; bump the spec version (minor = clarification, major = behavior change); add a dated line to the spec's `## Change log`; set affected REQ-IDs to `changed` with a dated note; reopen or add tasks; if the spec was `done`, set it back to `in-progress`.
- **Design decision changes**: never edit an accepted ADR. Write a new ADR from `0000-template.md`, mark the old one `Superseded by NNNN`, link both ways.
- **Schema changes**: edit `models.py`, autogenerate an Alembic migration, review it, update `data-model.md` in the same commit.

## Versioning and releases

- SemVer, `0.x` during the MVP. Each finished roadmap spec normally bumps the minor version (target in the roadmap).
- Release (`/release`): move `[Unreleased]` entries to `## [X.Y.Z] - YYYY-MM-DD`, update compare links, bump `version` in `backend/pyproject.toml` and `frontend/package.json`, run `scripts/status.py`, commit `chore(release): vX.Y.Z`, tag `vX.Y.Z`.

## Commands

```powershell
docker compose up -d db                              # Postgres
cd backend; uv run alembic upgrade head              # migrations
cd backend; uv run fastapi dev app/main.py           # API on :8000
cd frontend; npm run dev                             # UI on :5173
cd backend; uv run ruff check . ; uv run ruff format . ; uv run pytest
cd frontend; npm run typecheck
python scripts/status.py                             # regenerate STATUS.md
python scripts/check_tracking.py                     # the Stop-hook check, by hand
```

Run npm commands from `frontend/`, never from the repo root.

## Code conventions

- Python 3.12+, async throughout (SQLAlchemy async, httpx). Ruff for lint + format (line length 100).
- Config only through `app.config` (`get_config()`, `get_secrets()`); no hard-coded settings.
- All LLM calls go through `app/llm.py`.
- Collectors are idempotent upserts; one failing job must never stop another.
- Pure logic (scoring, momentum) lives in pure functions with unit tests.
- Frontend: TypeScript strict, TanStack Query for server data, Tailwind for styling.

## Working agreements

- Commit or push only when the user asks (`/done` and `/release` count as asking for a commit; pushing still needs a separate yes).
- A Stop hook (`scripts/check_tracking.py`) blocks ending a turn if app code changed without any tracking file (`CHANGELOG.md`, `STATUS.md`, `specs/`, `docs/qa/`) changing, or if `STATUS.md` / `docs/qa/traceability.md` is stale. Fix the tracking rather than working around it; if the change really isn't tracked work, tell the user.
