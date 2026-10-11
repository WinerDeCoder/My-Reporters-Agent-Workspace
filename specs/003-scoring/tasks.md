# 003 — Tasks

Spec: [spec.md](spec.md) · Plan: [plan.md](plan.md) · QA: [test cases](../../docs/qa/test-cases/003-scoring.md)

- [x] T0: QA test cases for every acceptance criterion
- [x] T1: Config: `interests.topics`, `ai_dev_terms`, boosts; `scoring` penalties
- [x] T2: `scoring.py`: normalize, `TopicMatcher`, boost, `score_item`, texts
- [x] T3: Unit tests: matching, boost, scores, penalties, fixture check (TC-003-01…05)
- [x] T4: `load_signals()` (empty until briefs/feedback exist)
- [x] T5: Wire into `repo_stats` and `/api/repos`, `/api/news`
- [x] T6: CLI `top`
- [x] T7: Frontend: "For you" sort, topic badges, AI/dev toggle; typecheck + build (TC-003-09)
- [x] T8: Live checks: `top`, API fields (TC-003-06, 07)
- [x] T9: Browser check (TC-003-08)
- [x] T10: Update docs listed in plan.md
- [ ] T11: Close-out (`/done`): requirements status, CHANGELOG, STATUS.md
