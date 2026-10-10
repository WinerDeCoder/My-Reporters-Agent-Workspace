"""Stop-hook check: application code changed, but tracking files didn't.

Claude Code runs this when Claude is about to end its turn (see .claude/settings.json).
It looks at uncommitted changes (staged, unstaged, untracked). It blocks (exit 2,
reason on stderr, which Claude reads and must act on) when:

  1. app code changed but none of CHANGELOG.md, STATUS.md or specs/** changed, or
  2. STATUS.md is out of date with the specs (run scripts/status.py).

It never blocks twice in a row (`stop_hook_active`), so it can't trap Claude in a loop.
Run it by hand any time: `python scripts/check_tracking.py`.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CODE_PREFIXES = (
    "backend/app/",
    "backend/alembic/",
    "backend/prompts/",
    "frontend/src/",
    "config.yaml",
    "docker-compose.yml",
)
TRACKING_PREFIXES = ("CHANGELOG.md", "STATUS.md", "specs/", "docs/qa/")


def changed_files() -> list[str]:
    out = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout
    files = []
    for line in out.splitlines():
        path = line[3:].strip().strip('"')
        if " -> " in path:  # rename: keep the new path
            path = path.split(" -> ", 1)[1]
        files.append(path.replace("\\", "/"))
    return files


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    try:
        payload = json.loads(sys.stdin.read() or "{}") if not sys.stdin.isatty() else {}
    except json.JSONDecodeError:
        payload = {}
    if payload.get("stop_hook_active"):
        return 0  # already blocked once this turn; let Claude stop

    try:
        files = changed_files()
    except (OSError, subprocess.CalledProcessError):
        return 0  # not a git repo / git missing: nothing to check

    code = [f for f in files if f.startswith(CODE_PREFIXES)]
    tracking = [f for f in files if f.startswith(TRACKING_PREFIXES)]
    problems = []

    if code and not tracking:
        listed = ", ".join(code[:5]) + (" …" if len(code) > 5 else "")
        problems.append(
            f"Application code changed ({listed}) but no tracking file did. "
            "Tick the related tasks in specs/<NNN>/tasks.md, and if a feature or change is "
            "finished, follow the Definition of Done in CLAUDE.md (requirements status, "
            "CHANGELOG [Unreleased], scripts/status.py). If this change is genuinely not "
            "tracked work, say so to the user."
        )

    status = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "status.py"), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if status.returncode != 0:
        problems.append(
            "STATUS.md or docs/qa/traceability.md is out of date: run `python scripts/status.py`."
        )

    if problems:
        print("Tracking check failed:\n- " + "\n- ".join(problems), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
