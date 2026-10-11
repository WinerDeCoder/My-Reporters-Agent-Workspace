# 008 — Tasks

Spec: [spec.md](spec.md) · Plan: [plan.md](plan.md) · QA: [test cases](../../docs/qa/test-cases/008-rising-repos-page.md)

- [x] T0: QA test cases for every acceptance criterion
- [x] T1: `CollectorRun` model + migration 0002; apply to local DB
- [x] T2: `record_run` + `run_job` recording; CLI collect goes through `run_job`; unit tests (TC-008-04, 05)
- [x] T3: `repo_stats.build_repo_rows` + `load_repo_rows`; CLI momentum reuses it; unit tests (TC-008-01, 02)
- [x] T4: `GET /api/repos`, `GET /api/collectors/status`; scheduler on `app.state`
- [x] T5: Frontend types, `CollectorStatus` component, Today panel
- [x] T6: Rising repos page: list, search, language filter, sort; nav + route; favicon
- [x] T7: Typecheck + build; integration checks on the endpoints (TC-008-03, 06)
- [x] T8: Manual check in the browser (TC-008-07…09)
- [x] T9: Update docs listed in plan.md
- [ ] T10: Close-out (`/done`): requirements status, CHANGELOG, STATUS.md
