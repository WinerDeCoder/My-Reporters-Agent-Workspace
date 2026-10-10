# 001 — Tasks

Spec: [spec.md](spec.md) · Plan: [plan.md](plan.md)

Not started: the spec and plan need approval first.

- [ ] T1: Shared HTTP client + retry helper (`app/collectors/__init__.py`)
- [ ] T2: Trending fetch + parser + upsert (`github_trending.py`); save HTML fixture
- [ ] T3: Parser unit test on fixture
- [ ] T4: Tracked-repo query + GitHub API fetch + README hash + snapshot insert (`github_api.py`)
- [ ] T5: Rate-limit and 404 handling
- [ ] T6: `momentum.py` + unit tests
- [ ] T7: Register both jobs in `scheduler.py` (independent, `max_instances=1`)
- [ ] T8: CLI: `collect trending`, `collect github`, `momentum --top N`
- [ ] T9: Manual run against real GitHub: AC-1 … AC-5
- [ ] T10: 24 h soak, then AC-6 eyeball check
- [ ] T11: Update docs listed in plan.md
- [ ] T12: Close-out (`/done`): requirements status, CHANGELOG, STATUS.md
