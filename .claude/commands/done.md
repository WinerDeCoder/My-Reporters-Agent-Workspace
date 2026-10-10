---
description: Close out a finished feature (Definition of Done) and commit
argument-hint: <spec number, e.g. 001>
---

Close out spec $ARGUMENTS using the Definition of Done in `CLAUDE.md`.

1. Check `tasks.md`: every task ticked or struck with a reason. If any are open, stop and tell me which.
2. Check every acceptance criterion in `spec.md`. Tick only those actually verified; for any you can't verify (e.g. needs a 24 h soak), stop and tell me.
3. Run the checks: `cd backend; uv run ruff check . ; uv run ruff format --check . ; uv run pytest`, plus `cd frontend; npm run typecheck` if the frontend changed. Stop on failure and show the output.
4. Update the spec front matter: `status: done`, `updated:` today; add a change-log line.
5. Set the linked REQ-IDs in `docs/product/requirements.md` to `done`.
6. Update the docs listed in the plan's "Docs to update when done".
7. Add the user-visible changes to `CHANGELOG.md` under `## [Unreleased]` (Added / Changed / Fixed / Removed), naming the spec.
8. Run `python scripts/status.py` and `python scripts/check_tracking.py`.
9. Show me the diff summary, then commit with a Conventional Commit message naming the spec. Don't push unless I say so.
10. Tell me whether this completes a roadmap version (then suggest `/release`), and what the next spec is.
