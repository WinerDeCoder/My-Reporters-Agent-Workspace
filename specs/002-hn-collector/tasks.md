# 002 — Tasks

Spec: [spec.md](spec.md) · Plan: [plan.md](plan.md) · QA: [test cases](../../docs/qa/test-cases/002-hn-collector.md)

- [x] T0: QA test cases for every acceptance criterion; Algolia fixtures saved
- [x] T1: Config: `popular_min_points`, `popular_window_hours`, `retention_days`
- [x] T2: `hacker_news.py`: queries, `parse_hits`, `github_repo_from_url`, `merge_stories`, `collect_hacker_news`
- [x] T3: Unit tests on fixtures (TC-002-01…04)
- [x] T4: `news_stats.points_per_hour` + tests (TC-002-05)
- [x] T5: `prune.py` + cutoff tests (TC-002-06)
- [x] T6: Scheduler jobs + registration test (TC-002-07); CLI `collect hn`, `prune`
- [x] T7: `GET /api/news`
- [x] T8: Frontend: News page, nav, status labels; typecheck + build (TC-002-13)
- [x] T9: Live checks against the local DB (TC-002-08…11)
- [x] T10: Browser check (TC-002-12)
- [x] T11: Update docs listed in plan.md
- [ ] T12: Close-out (`/done`): requirements status, CHANGELOG, STATUS.md
