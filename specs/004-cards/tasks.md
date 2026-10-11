# 004 — Tasks

Spec: [spec.md](spec.md) · Plan: [plan.md](plan.md) · QA: [test cases](../../docs/qa/test-cases/004-cards.md)

- [x] T0: QA test cases; probe call confirming gpt-6-luna structured output
- [x] T1: Config: token cap, prices, `cards` section
- [x] T2: `LlmUsage` model + migration 0003; apply locally
- [x] T3: `llm.generate()` returns usage
- [x] T4: `cards.py`: sources (README, article, fallback), hash, cache, cap, `get_or_write_card`, `write_daily_cards`
- [x] T5: Unit tests (TC-004-01…05)
- [x] T6: Scheduler `cards` job + catch-up; CLI `cards`, `usage`
- [x] T7: API: cards GET/POST, LLM usage; `has_card` on rows
- [x] T8: Prompt `card.md`
- [x] T9: Frontend: Card page + Write card, list links, usage line; typecheck + build (TC-004-10)
- [x] T10: Live checks: daily cards, cache, cap 0, API (TC-004-06…08)
- [x] T11: Browser check (TC-004-09)
- [x] T12: Update docs listed in plan.md
- [ ] T13: Close-out (`/done`)
