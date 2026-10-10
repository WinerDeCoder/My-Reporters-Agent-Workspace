---
description: Approve a spec and write its technical plan (plan.md)
argument-hint: <spec number, e.g. 001>
---

Write the plan for spec $ARGUMENTS.

1. Read `CLAUDE.md`, the spec, `docs/architecture/overview.md`, `docs/architecture/data-model.md`, and the code it will touch.
2. If the spec is still `draft` and I have approved it in this conversation, set `status: approved`, `version: 1.0`, `updated:` today, and add a change-log line. If I haven't approved it, ask first.
3. Write `plan.md` from `specs/_template/plan.md`: approach, file-by-file changes, details (APIs, algorithms, errors, edge cases), testing, risks, and the docs to update when done.
4. If the plan makes a significant, hard-to-reverse choice, draft an ADR in `docs/architecture/decisions/` (status Proposed).
5. Then write `tasks.md` (same as `/tasks`).
6. Write `docs/qa/test-cases/NNN-name.md`: at least one test case per acceptance criterion, each with Covers (AC + REQ-IDs), Module, Type (unit / integration / manual / soak), the automated test name or exact steps, and Last result `not run`. Follow `docs/qa/test-strategy.md`.
7. Any design question that needs my decision goes to `docs/qa/questions.md` as a `Q-NNN` and is asked with AskUserQuestion.
8. Run `python scripts/status.py`, then summarize the plan and any real design choices for me to confirm.
