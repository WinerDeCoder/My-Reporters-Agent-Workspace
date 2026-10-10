---
description: Draft a new feature spec (specs/NNN-name/spec.md) for review
argument-hint: <feature name or roadmap number, e.g. "002" or "HN collector">
---

Draft a feature spec for: $ARGUMENTS

1. Read `CLAUDE.md`, `STATUS.md`, `docs/product/prd.md`, `docs/product/requirements.md` and `docs/product/roadmap.md`.
2. Pick the spec number: the roadmap number if this feature is on the roadmap, otherwise the next free number. Folder: `specs/NNN-kebab-name/`.
3. Copy `specs/_template/spec.md` and fill it in: status `draft`, version `0.1`, today's date, the REQ-IDs it covers. Acceptance criteria must be checkable by running something.
4. If the feature needs requirements that don't exist yet, add them to `requirements.md` with status `planned` and this spec number.
5. Don't guess on product decisions or unclear requirements: add each question (with your suggestion and the options) to `docs/qa/questions.md` as a new `Q-NNN`, link it from the spec's "Open questions", and ask me with AskUserQuestion.
6. Run `python scripts/status.py`.
7. Show me a short summary and the open questions. Do not write a plan or code until I approve the spec.
