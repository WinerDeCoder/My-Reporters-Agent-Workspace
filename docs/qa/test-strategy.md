# Test strategy

How Tech Radar is tested. Per-feature test cases live in [test-cases/](test-cases/).

## Levels

| Level | What it covers | How | Runs |
| --- | --- | --- | --- |
| **Unit** | Pure logic: parsers, momentum, scoring, rate-limit math, config | pytest; no network, no DB. HTTP is faked with `httpx.MockTransport`; HTML/JSON inputs come from `backend/tests/fixtures/` | Every change (`uv run pytest`) |
| **Integration** | Collectors and queries against real Postgres and real APIs | CLI commands (`uv run python -m app.cli ...`) with Docker Postgres and a real `GITHUB_TOKEN` | Before closing a spec |
| **Manual** | Pages and end-to-end behavior | Steps written in the test case; result recorded by hand | Before closing a spec |
| **Soak** | Behavior over time (scheduled runs, momentum over 24 h, laptop sleep) | Leave the app running; check afterwards | Before closing specs that need history |

## Tools and commands

```powershell
cd backend; uv run pytest                       # all backend tests
cd backend; uv run pytest tests/test_momentum.py -q
cd backend; uv run ruff check . ; uv run ruff format --check .
cd frontend; npm run typecheck
```

Async tests use `pytest-asyncio` in auto mode (just write `async def test_...`).

## Conventions

- One test file per module: `backend/tests/test_<module>.py`.
- Fixtures (saved HTML/JSON) in `backend/tests/fixtures/`, named after their source.
- Tests never call real external services or need the database; anything that does is an integration/manual test case with written steps.
- Test names say the behavior: `test_fetch_repo_returns_none_on_404`.

## Recording results

Each test case's **Last result** in `test-cases/NNN-*.md` is updated whenever it is run: `pass YYYY-MM-DD`, `fail YYYY-MM-DD (note)`, `not run`, `blocked (reason)`. `/qa NNN` runs the automated ones and updates them. The roll-up appears in `STATUS.md` and [traceability.md](traceability.md).

## What blocks "done"

A spec is not done while any of its test cases is `fail`, or is `not run`/`blocked` without the user's sign-off recorded in the spec change log.
