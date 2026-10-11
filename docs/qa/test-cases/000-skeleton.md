# Test cases — 000 Project skeleton

Spec: [000](../../../specs/000-skeleton/spec.md) · Recorded after the fact on 2026-10-10.

| TC | Title | Covers | Module | Type | Automated test / Steps | Last result |
| --- | --- | --- | --- | --- | --- | --- |
| TC-000-01 | Health endpoint answers when the DB is down | AC-2, REQ-NFR-001 | app/api/health.py | unit | `backend/tests/test_health.py::test_health_responds_without_db` | pass 2026-10-10 |
| TC-000-02 | `config.yaml` loads and validates | AC-4, REQ-NFR-006 | app/config.py | unit | `backend/tests/test_config.py::test_config_yaml_loads` | pass 2026-10-10 |
| TC-000-03 | Card prompt file configured in `llm.prompt_file` exists | REQ-CRD-002 | app/config.py | unit | `backend/tests/test_config.py::test_card_prompt_file_exists` | pass 2026-10-10 |
| TC-000-04 | Migration creates the 6 MVP tables | AC-1 | alembic/versions/0001_initial_schema.py | integration | `docker compose up -d db`; `cd backend; uv run alembic upgrade head`; `\dt` in psql shows 6 tables + alembic_version | pass 2026-10-11 (`alembic_version` = 0001 on the local DB, all 6 tables queried; 0002 applied on top) |
| TC-000-05 | Today page shows system status | AC-3 | frontend/src/pages/Today.tsx | manual | `cd frontend; npm run dev`; open http://localhost:5173; status box shows API ok | pass 2026-10-11 (Playwright on :5173: "API: ok", "Database: connected") |
| TC-000-06 | `.env` is never committed | REQ-NFR-002 | .gitignore | unit | `git check-ignore .env` prints `.env` | pass 2026-10-10 |
