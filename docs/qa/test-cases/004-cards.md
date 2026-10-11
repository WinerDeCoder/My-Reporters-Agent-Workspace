# Test cases — 004 Cards

Spec: [004](../../../specs/004-cards/spec.md) · Plan: [plan.md](../../../specs/004-cards/plan.md)

| TC | Title | Covers | Module | Type | Automated test / Steps | Last result |
| --- | --- | --- | --- | --- | --- | --- |
| TC-004-01 | Source text truncated at the cap; hash changes with text and kind | AC-3, REQ-CRD-003 | app/cards.py | unit | `backend/tests/test_cards.py::test_truncate_and_hash` | pass 2026-10-11 |
| TC-004-02 | Article extraction from saved HTML; empty/garbage → limited fallback | AC-2, REQ-CRD-001 | app/cards.py | unit | `backend/tests/test_cards.py::test_extract_article*` | pass 2026-10-11 (unit fixture; live: 1 story from article text, 1 FT story HTTP 403 → title fallback, limited) |
| TC-004-03 | Cache: same source hash → no LLM call; changed hash or force → new card | AC-3, REQ-CRD-003 | app/cards.py | unit | `backend/tests/test_cards.py::test_needs_new_card` | pass 2026-10-11 |
| TC-004-04 | Token cap: under cap allowed, at/over cap blocked, cap 0 blocks; month start in local timezone | AC-4, REQ-CRD-004 | app/cards.py | unit | `backend/tests/test_cards.py::test_within_cap`, `::test_month_start` | pass 2026-10-11 |
| TC-004-05 | `cards` job scheduled at 07:25 with catch-up | AC-6, REQ-CRD-001 | app/scheduler.py | unit | `backend/tests/test_scheduler.py::test_jobs_registered_daily_at_run_at` | pass 2026-10-11 |
| TC-004-06 | Live daily cards: top repos + stories get cards with all fields; usage rows written; second run = 0 calls | AC-1, AC-3, AC-5, REQ-CRD-001, REQ-CRD-003, REQ-NFR-005 | app/cards.py, app/llm.py, app/cli.py | integration | `cd backend; uv run python -m app.cli cards` twice; check `cards` and `llm_usage` rows | pass 2026-10-11 (8 cards: 5 repo READMEs, 1 linked-repo README, 1 article, 1 title-only; 20,615 tokens; second run 0 new llm_usage rows; no empty fields) |
| TC-004-07 | Cap 0: no call made, job ends cleanly, API returns 429 | AC-4, REQ-CRD-004 | app/cards.py, app/api/cards.py | integration | Set `monthly_token_cap: 0`, run `cards` and POST a card; restore | pass 2026-10-11 (cap 0: CapReached, no usage row, daily job ends cleanly; API 429 via `backend/tests/test_api_cards.py`) |
| TC-004-08 | `GET/POST /api/cards/...` and `GET /api/llm/usage` return documented shapes | AC-5, AC-7, REQ-CRD-005, REQ-UI-005 | app/api/cards.py | integration | curl endpoints on a test instance | pass 2026-10-11 (GET card + item signals, GET /llm/usage, unknown item 404, bad type 422) |
| TC-004-09 | Card page shows card + signals; Write card works; list links show card status; no console errors | AC-7, REQ-CRD-005, REQ-UI-005 | frontend/src/pages/Card.tsx, frontend/src/pages/Repos.tsx, frontend/src/pages/News.tsx | manual | Open a card from Rising repos; open an item without one and click Write card; console clean | pass 2026-10-11 (Playwright: card page for mattpocock/skills; Write card on news 20 wrote a README-based card in ~10 s; News shows 3 card / 15 write-card links; usage line "20.6K of 3M"; 0 console messages) |
| TC-004-10 | Frontend typecheck and production build pass | AC-7, REQ-UI-005 | frontend/src | unit | `cd frontend; npm run typecheck; npm run build` | pass 2026-10-11 |
