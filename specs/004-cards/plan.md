# 004 — Plan

Spec: [spec.md](spec.md) · Plan version 1.0 · Test cases: [docs/qa/test-cases/004-cards.md](../../docs/qa/test-cases/004-cards.md)

## Approach

`app/cards.py` owns sources, caching and the budget check; `app/llm.py` stays the only module that calls OpenAI and now also returns token usage. Pure helpers (truncation, hashing, cache decision, budget check, article extraction) are unit-tested with fakes; the LLM call is injected so tests never hit the network.

## Changes

| Area | File / module | Change |
| --- | --- | --- |
| Config | `config.yaml`, `app/config.py` | `llm.monthly_token_cap` (3,000,000; replaces `monthly_budget_usd`), optional `llm.price_per_million {input, output}`; `cards.run_at` 07:25, `cards.max_source_chars` 12000; top counts from `brief.top_repos` / `brief.top_news` |
| DB | `models.py`, `alembic/versions/0003_llm_usage.py` | `LlmUsage` (at, model, purpose, item_type, item_id, input_tokens, output_tokens, ok, error) |
| Backend | `app/llm.py` | `generate()` returns `LlmResult(parsed, input_tokens, output_tokens, model)` |
| Backend | `app/cards.py` | `CardContent` schema; `fetch_readme()`, `extract_article()`, `card_source()`; `truncate()`, `source_hash()`; `needs_new_card()`; `tokens_this_month()`, `within_cap()`; `get_or_write_card()`; `write_daily_cards()` |
| Backend | `app/scheduler.py` | `cards` job at `cards.run_at`, 20 h catch-up, after collectors (+200 s) |
| Backend | `app/api/cards.py` | `GET /api/cards/{type}/{id}` (item + card or null), `POST` same path (write on demand; 429 when capped) |
| Backend | `app/api/cards.py` | `GET /api/llm/usage` (tokens this month, cap, calls) |
| Backend | `app/repo_stats.py`, `app/news_feed.py` | `has_card` flag |
| Backend | `app/cli.py` | `cards`, `usage` |
| Prompt | `backend/prompts/card.md` | English, field guidance, limited-source rule |
| Frontend | `src/pages/Card.tsx`, `src/pages/Repos.tsx`, `src/pages/News.tsx`, `src/components/CollectorStatus.tsx`, `src/api/client.ts` | Card page with Write card; card links in lists; LLM usage line |

## Details

- **README:** `GET /repos/{name}/readme` with `Accept: application/vnd.github.raw` (same bytes as `readme_hash`).
- **Article:** GET the URL (15 s timeout, follow redirects, max 2 MB, HTML only); `trafilatura.extract()`; empty → limited.
- **Hash:** sha256 of the final (truncated) source text + source kind; stored in `cards.source_hash`.
- **Budget:** sum of `input_tokens + output_tokens` in `llm_usage` since the first day of the month (configured timezone); skip when `>= cap`.
- **Order of daily cards:** top repos by score (scored only), then top AI/dev stories by score; failures are logged per item and don't stop the job.

## Testing

Unit: truncation, hashing, cache decision, cap check, month start, article extraction on a saved HTML fixture, `get_or_write_card` with a fake LLM and fake sources (no DB: session-free core). Integration: CLI `cards` once with the real model (≈8 calls), second run = 0 calls; cap 0 run; API endpoints. Manual: Card page + Write card in the browser.

## Risks

- Article sites block bots or need JS: fallback keeps a (limited) card.
- Token cost per card ≈ source (~3k tokens) + output; 8/day ≈ well under 3M/month.

## Docs to update when done

- [x] `docs/architecture/overview.md`, `data-model.md` (`llm_usage`), `api.md`
- [x] `README.md`: `cards`, `usage`
- [x] `docs/qa/test-cases/004-cards.md`: results
