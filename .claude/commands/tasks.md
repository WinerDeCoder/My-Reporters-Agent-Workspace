---
description: Break a spec's plan into a task checklist (tasks.md)
argument-hint: <spec number, e.g. 001>
---

Write or refresh `tasks.md` for spec $ARGUMENTS.

1. Read the spec and its `plan.md`.
2. Write `tasks.md` from `specs/_template/tasks.md`: small tasks (each finishable and testable on its own), in build order, ending with tests, a docs task and a close-out task.
3. Map every acceptance criterion to at least one task.
4. If refreshing, keep ticked tasks ticked; strike removed tasks with a reason instead of deleting them.
5. Run `python scripts/status.py` and show me the list.
