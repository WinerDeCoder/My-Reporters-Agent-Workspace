# 001 — Tasks

Spec: [spec.md](spec.md) · Plan: [plan.md](plan.md) · QA: [test cases](../../docs/qa/test-cases/001-github-collectors.md)

- [x] T0: QA test cases for every acceptance criterion
- [x] T1: Shared HTTP client + retry helper (`app/collectors/__init__.py`)
- [x] T2: Trending fetch + parser + upsert (`github_trending.py`); save HTML fixture
- [x] T3: Parser unit tests on fixture (TC-001-01…03)
- [x] T4: Tracked-repo query + GitHub API fetch + README hash + snapshot insert (`github_api.py`)
- [x] T5: Rate-limit and 404 handling + MockTransport tests (TC-001-05…07)
- [x] T6: `momentum.py` + unit tests (TC-001-04)
- [x] T7: Register both jobs in `scheduler.py` with startup offsets + isolation tests (TC-001-08, 09)
- [x] T8: CLI: `collect trending`, `collect github`, `momentum --top N`
- [x] T9: Live run against real GitHub + Postgres (TC-001-10, 11)
- [x] T13: Daily schedule + startup catch-up (Q-014): cron triggers, `jobs_to_catch_up`, `schedule_catch_up`, tests (TC-001-09, 13)
- [ ] T10: 24 h soak, then momentum eyeball check (TC-001-12)
- [x] T11: Update docs listed in plan.md
- [ ] T12: Close-out (`/done`): requirements status, CHANGELOG, STATUS.md
