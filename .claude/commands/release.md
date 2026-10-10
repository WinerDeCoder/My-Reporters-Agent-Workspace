---
description: Cut a release - CHANGELOG, version bumps, tag
argument-hint: <version, e.g. 0.2.0 (optional: defaults to the roadmap target)>
---

Cut release $ARGUMENTS.

1. Read `CHANGELOG.md`, `STATUS.md` and `docs/product/roadmap.md`. If no version was given, use the target version of the most recently finished spec. Confirm the version with me if it's ambiguous.
2. Stop if `## [Unreleased]` is empty or the working tree has unrelated uncommitted changes.
3. In `CHANGELOG.md`: move the Unreleased entries into a new `## [X.Y.Z] - YYYY-MM-DD` section, leave an empty `## [Unreleased]`, and update the compare links at the bottom.
4. Bump `version` in `backend/pyproject.toml` and `frontend/package.json`.
5. Run `python scripts/status.py`.
6. Commit `chore(release): vX.Y.Z` and create an annotated tag `vX.Y.Z` with the release notes as the message.
7. Ask me before pushing the commit and tag (`git push origin main --follow-tags`).
