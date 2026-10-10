---
description: Run a spec's tests and record results in its QA test-case file
argument-hint: <spec number, e.g. 001>
---

Run QA for spec $ARGUMENTS.

1. Read `docs/qa/test-strategy.md` and `docs/qa/test-cases/$ARGUMENTS-*.md`.
2. Run every **unit** test case's automated test (`cd backend; uv run pytest <paths> -q`; frontend: `npm run typecheck`). Set each Last result to `pass YYYY-MM-DD` or `fail YYYY-MM-DD (short reason)`.
3. For **integration** cases: if Docker Postgres is up and `.env` has the needed keys, run the listed steps and record results; otherwise set `blocked (reason)`.
4. Don't fake **manual** or **soak** results: leave them `not run` unless I report the outcome, and list their steps for me.
5. If a test case is missing for an acceptance criterion, add it.
6. Run `python scripts/status.py` and summarize: pass / fail / blocked / not run, with the next action for each non-pass case.
