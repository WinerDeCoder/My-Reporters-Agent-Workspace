# Tech Radar — Requirements (MVP)

Every requirement has a stable ID. Specs, tasks, tests and commits refer to these IDs.

**Status values:** `planned` → `in-progress` → `done`, or `changed` (reworded after work started; see the note) / `dropped`.
**Spec** is the feature spec under `specs/` that implements it.

When a requirement changes, edit it in place, set its status, and add a dated line to its Notes. Git keeps the old wording.

## Collectors (COL)

| ID | Requirement | Acceptance criteria | Status | Spec | Notes |
| --- | --- | --- | --- | --- | --- |
| REQ-COL-001 | Scrape GitHub Trending (daily and weekly ranges) for the languages in `config.yaml`, daily at `run_at` (07:10). | Each run upserts every listed repo into `repos` and updates `last_seen`; a run with N trending pages logs how many repos it found. | in-progress | 001 | 2026-10-10: languages confirmed as all + Python + TypeScript (Q-002). 2026-10-11: daily at 07:10 instead of every 6 h (Q-014). |
| REQ-COL-002 | For every candidate repo whose `last_seen` is within `track_days`, fetch stars, forks, description, topics, language, license and README hash from the GitHub REST API, and store one star snapshot per run, daily at `run_at` (07:20). | After two runs, each tracked repo has two `repo_snapshots` rows; metadata columns are filled; README changes update `readme_hash`. | in-progress | 001 | 2026-10-10: window counted from `last_seen`, not `first_seen` (Q-001). 2026-10-11: daily at 07:20 instead of every 6 h (Q-014). |
| REQ-COL-003 | Collect Hacker News top stories (title, URL, points, comments, posted time) daily at 07:00 from the Algolia HN API: the current front page plus stories above 100 points from the last 26 h. Store every story; topic filtering happens in scoring. | Stories are upserted by `hn_id`; points and comments update on later runs. | in-progress | 002 | 2026-10-11: sources = front page + >100 pts/24 h (Q-010); store all, filter in scoring (Q-011). 2026-10-11: daily instead of hourly, window 26 h (Q-014). |
| REQ-COL-004 | GitHub repo links in HN stories become repo candidates. | A story linking `github.com/owner/repo` creates or updates that repo and sets `news_items.linked_repo_id`. | in-progress | 002 | |
| REQ-COL-005 | Each collector runs on its own daily schedule and retries transient errors; one failing never stops the others. On startup, a collector runs only if its last successful run is older than `catch_up_after_hours`. | Simulated failure in one collector is logged and the others still complete their runs; a restart soon after a successful run starts no collector. | changed | 001 | 2026-10-10: collectors also run ~1 min after startup (Q-003). 2026-10-11: replaced by daily runs + catch-up only when stale (Q-014). |
| REQ-COL-006 | Prune weekly: HN items older than 30 days (unless a brief references them), and snapshots of repos no longer tracked (`last_seen` older than `track_days`). Spec 005 adds "and never reached a brief" for snapshots. | After the prune job, no HN item older than 30 days and no snapshot of an untracked repo remains; tracked repos keep all snapshots. | changed | 002 | 2026-10-11: snapshot rule narrowed to untracked repos until briefs exist (Q-013). |
| REQ-COL-007 | Every collector run (scheduled or CLI) is recorded: job name, start, end, success, result count, error message. | A failed and a successful run each leave one `collector_runs` row with the right outcome; a DB error while recording never breaks the job. | in-progress | 008 | 2026-10-11: added (Q-009). |

## Scoring (SCO)

| ID | Requirement | Acceptance criteria | Status | Spec | Notes |
| --- | --- | --- | --- | --- | --- |
| REQ-SCO-001 | Repo score = stars gained per day (from the two nearest snapshots ~24 h apart), boosted on interest-keyword match, lowered if the repo was in a brief in the last `repeat_cooldown_days`. | A CLI command prints today's top repos with their score components; values match a hand calculation on test data. | planned | 003 | |
| REQ-SCO-002 | News score = HN points per hour since posting, boosted on keyword match; only AI/dev stories pass the keyword filter. | Off-topic stories never appear in the top list; ordering matches points/hour on test data. | planned | 003 | |
| REQ-SCO-003 | A 👎 lowers future scores for items sharing its keywords (simple rule, tuned by hand). | After a 👎 on an item tagged "x", a new item tagged "x" scores lower than it would without the rating. | planned | 003 | |

## Cards (CRD)

| ID | Requirement | Acceptance criteria | Status | Spec | Notes |
| --- | --- | --- | --- | --- | --- |
| REQ-CRD-001 | Each morning the top ~5 repos and ~3 news items get a card: what it is, problem it solves, what's special, worth trying, plus signals. | Cards are stored in `cards` as structured JSON with all fields filled (or "unclear"). | planned | 004 | |
| REQ-CRD-002 | The card prompt lives in one file and all model settings in `config.yaml` → `llm`. | Changing the model or prompt needs no code change. | planned | 004 | `llm.py` and config added in v0.1.0. |
| REQ-CRD-003 | Cards are cached; a new card is generated only when the source text hash changes. | Re-running card generation on unchanged items makes zero LLM calls. | planned | 004 | |
| REQ-CRD-004 | Card generation stops once the month's spend reaches `monthly_budget_usd`. | With the cap set to 0, no LLM call is made and the brief still builds (without new cards). | planned | 004 | |
| REQ-CRD-005 | A Card page shows the full card and links for any item. | `/cards/repo/<id>` and `/cards/news/<id>` render the stored card. | planned | 004 | |

## Brief (BRF)

| ID | Requirement | Acceptance criteria | Status | Spec | Notes |
| --- | --- | --- | --- | --- | --- |
| REQ-BRF-001 | Build a daily brief at `brief_time`: a top story, 3–5 rising repos, 2–3 news items. | One `briefs` row of type `daily` per day with the items in order. | planned | 005 | |
| REQ-BRF-002 | If the machine was off or asleep at `brief_time`, build the missed brief on next startup. | Starting the app after `brief_time` with no brief for today builds one within a minute. | planned | 005 | |
| REQ-BRF-003 | The Today page shows the latest brief; each item links to its card. | Page renders the latest brief; readable in about two minutes. | planned | 005 | |
| REQ-BRF-004 | Opening the Today page records `opened_at` the first time a brief is viewed. | `briefs.opened_at` is set once and never overwritten. | planned | 005 | |

## Leaderboard (LDB)

| ID | Requirement | Acceptance criteria | Status | Spec | Notes |
| --- | --- | --- | --- | --- | --- |
| REQ-LDB-001 | Every Monday at `brief_time`, build the weekly leaderboard: top 10 repos by stars gained over 7 days, each with stars gained, total stars and a one-line description; show it on the Leaderboard page. | One `briefs` row of type `weekly` per Monday; the page renders it. | planned | 006 | |

## Feedback and stats (FBK)

| ID | Requirement | Acceptance criteria | Status | Spec | Notes |
| --- | --- | --- | --- | --- | --- |
| REQ-FBK-001 | Every brief item has 👍 and 👎 buttons; a click is saved with the item, brief and time. | Clicking stores a `feedback` row; the button shows the saved state. | planned | 005 | |
| REQ-FBK-002 | A Stats page shows the last 14 days: briefs built, briefs opened, items rated, share of thumbs up. | Numbers match a direct SQL count. | planned | 007 | |

## Interface (UI)

| ID | Requirement | Acceptance criteria | Status | Spec | Notes |
| --- | --- | --- | --- | --- | --- |
| REQ-UI-001 | A Rising repos page lists every tracked repo with stars, stars/day (or "collecting" until 6 h of history), description, language, topics and a GitHub link; it can be searched, filtered by language and sorted by stars/day, stars or newest. | With the collectors' data loaded, the page shows every tracked repo; search, filter and each sort order change the list correctly. | in-progress | 008 | 2026-10-11: pulled forward from the v1 dashboard (Q-008). |
| REQ-UI-003 | A News page lists collected HN stories with title (link), points, comments, age, points/hour, HN discussion link and a badge for linked tracked repos; searchable and sortable by points/hour, points or newest. | With the HN collector's data loaded, the page shows every stored story from the last 7 days; search and each sort order work. | in-progress | 002 | 2026-10-11: added (Q-012). |
| REQ-UI-002 | The UI shows collector status: per job, the last run time, outcome, count and next scheduled run. | After a run, Today and Rising repos show its time and count; a failed run shows as failed with its error. | in-progress | 008 | 2026-10-11: added (Q-009). |

## Non-functional (NFR)

| ID | Requirement | Acceptance criteria | Status | Spec | Notes |
| --- | --- | --- | --- | --- | --- |
| REQ-NFR-001 | Runs locally: one backend process (API + scheduler + built frontend); only Postgres runs in Docker. | README setup works on a fresh Windows machine. | done | 000 | |
| REQ-NFR-002 | Secrets live only in `.env`, never in code or git. | `.env` is git-ignored; `.env.example` lists every secret. | done | 000 | |
| REQ-NFR-003 | All schedules use the timezone in `config.yaml` (Asia/Ho_Chi_Minh). | Scheduler is created with the configured timezone. | done | 000 | |
| REQ-NFR-004 | Stay within API rate limits (GitHub 5,000 req/h with token) and back off on 403/429. | A full GitHub run stays under 10% of the hourly limit; rate-limit responses trigger backoff, not failure. | in-progress | 001 | |
| REQ-NFR-005 | LLM token usage is logged per call and monthly spend is tracked. | Each call logs model and input/output tokens; spend is queryable per month. | in-progress | 004 | Per-call logging done in v0.1.0; spend tracking pending. |
| REQ-NFR-006 | Non-secret settings live in one `config.yaml`, validated at startup. | Invalid config fails fast with a clear error. | done | 000 | |
