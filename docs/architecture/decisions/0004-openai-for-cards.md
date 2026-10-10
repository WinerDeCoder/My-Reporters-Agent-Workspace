# 0004. OpenAI for card generation

- **Status:** Accepted
- **Date:** 2026-10-10

## Context

Cards are short structured summaries (about 8 calls a day). On 2026-10-04 the skeleton was set up for Claude via the `anthropic` SDK (not recorded as an ADR at the time). On 2026-10-10 I chose to use the OpenAI API instead.

## Options considered

1. **Anthropic (Claude) via `anthropic` SDK:** the original choice.
2. **OpenAI via `openai` SDK:** my preference for now.

## Decision

Use the OpenAI Responses API through the official `openai` SDK, with structured output parsed into Pydantic models. All model settings (model, reasoning effort, max output tokens, timeout, optional `base_url`, prompt file, monthly budget) live in `config.yaml` → `llm`. `backend/app/llm.py` is the only module that calls the LLM.

## Consequences

- Switching model is a config change; switching provider again means rewriting only `llm.py`.
- `base_url` allows Azure OpenAI or any OpenAI-compatible server without code changes.
- The default model (`gpt-5-mini`) is a placeholder until confirmed.
