# QA

Two kinds of QA live here. Both always point to the feature (spec), the requirements (REQ-IDs) and the code modules they concern.

| File | What | IDs |
| --- | --- | --- |
| [questions.md](questions.md) | **Q&A log**: questions Claude asks the user, suggestions, answers and the decision they led to | `Q-NNN` |
| [test-strategy.md](test-strategy.md) | **Quality assurance**: how we test (levels, tools, conventions, what blocks "done") | — |
| [test-cases/](test-cases/) | One file per spec: test cases mapped to acceptance criteria, REQ-IDs and modules, with their last result | `TC-<spec>-NN`, e.g. `TC-001-03` |
| [traceability.md](traceability.md) | **Generated** by `python scripts/status.py`: REQ → spec → test cases → modules → open questions | — |

## Q&A rules

- Any question that needs the user's decision gets a `Q-NNN` entry **before** it's asked, with Claude's suggestion and the options.
- When answered: fill **Answer** (dated), set **Status** to `answered`, then apply the decision where it belongs (spec change log, requirement note, ADR) and name that place in **Recorded in**.
- Specs list their open questions as links to Q-IDs instead of repeating them.
- Never delete an entry; a reversed decision gets a new Q-ID and the old one becomes `superseded`.

## Test-case rules

- `/plan` writes `test-cases/NNN-name.md` with at least one test case per acceptance criterion.
- **Last result** is one of: `pass YYYY-MM-DD`, `fail YYYY-MM-DD (note)`, `not run`, `blocked (reason)`.
- A spec can be `done` only when every test case is `pass`, or `blocked`/`not run` with the user's explicit sign-off (written in the spec change log).
- Automated tests are named in the **Automated test** column (`backend/tests/test_x.py::test_name`); manual and soak cases list the exact command or steps in **Steps**.

## Module names

Use repo-relative paths without the `backend/` prefix for backend code (`app/collectors/github_api.py`) and with `frontend/` for frontend code (`frontend/src/pages/Today.tsx`). The traceability matrix groups by these strings.
