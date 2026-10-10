---
description: Record a change to a requirement, spec or decision, with versioning
argument-hint: <what changed, e.g. "001: also scrape Rust trending">
---

Record this change: $ARGUMENTS

1. Read `CLAUDE.md` ("When something changes") and the affected spec / requirements / ADR.
2. **Spec or requirement change:**
   - Edit the spec in place. Bump its version: minor (x.Y) for clarifications, major (X.0) for behavior changes. Set `updated:` today and add a dated `## Change log` line saying what changed and why.
   - Set affected REQ-IDs in `requirements.md` to `changed`, edit their wording, and add a dated note.
   - Update `plan.md`; reopen or add tasks in `tasks.md` (strike removed tasks with a reason).
   - If the spec was `done`, set it back to `in-progress`.
3. **Design decision change:** write a new ADR from `docs/architecture/decisions/0000-template.md`; set the old ADR's status to `Superseded by NNNN`; link both ways. Never rewrite an accepted ADR's body.
4. If shipped behavior changes, add a CHANGELOG line under `[Unreleased]` → Changed.
5. Run `python scripts/status.py`, then summarize what changed and which versions bumped.
