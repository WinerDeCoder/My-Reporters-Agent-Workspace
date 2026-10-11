---
id: 002
title: HN collector
status: in-progress
version: 2.0
requirements: [REQ-COL-003, REQ-COL-004, REQ-COL-006, REQ-UI-003]
target_release: 0.3.0
created: 2026-10-11
updated: 2026-10-11
---

# 002 — HN collector

## Why

Hacker News is where AI and dev news breaks first, and where many rising repos are first shown ("Show HN"). This feature fills `news_items` for the brief's news section (spec 005) and adds HN-linked repos as candidates, so their star momentum is tracked before they hit GitHub Trending. A News page makes the feed visible now (Q-012), and a weekly prune keeps the database small.

## What (behavior)

1. **HN collector** (daily at 07:00, Q-014): fetches from the Algolia HN API the current front page and every story above 100 points from the last 26 h (Q-010; window > 24 h so daily runs overlap); stores **every** story (Q-011), updating points and comments on later runs.
2. **Repo candidates:** a story whose URL is a GitHub repo (`github.com/owner/repo…`) creates or refreshes that repo (`last_seen = now`), so the GitHub API collector starts snapshotting it, and the story's `linked_repo_id` points to it. Non-repo GitHub URLs (gists, orgs, topics, marketplace…) are ignored.
3. **Weekly prune** (Mondays 07:40, after the collection; caught up on startup only if the last prune is > 7 days old): deletes HN stories older than 30 days and the snapshots of repos no longer tracked (`last_seen` older than `track_days`) (Q-013). Tracked repos keep all their snapshots.
4. **News page** (`/news`, nav "News"): stories from the last 7 days with title (link), domain, points, comments, age, points/hour, HN discussion link, and a badge for a linked repo. Search; sort by points/hour (default), points, or newest. Refreshes every minute.
5. Both new jobs appear in the collector status panel; CLI: `collect hn`, `prune`.

## Acceptance criteria

- [x] AC-1: `collect hn` stores the front page plus popular stories (about 30–60), logging counts per query; a second run updates points/comments without creating duplicates.
- [x] AC-2: A story linking a GitHub repo creates or refreshes that repo and sets `linked_repo_id`; gist/org/topic/marketplace URLs are ignored.
- [x] AC-3: The HN job runs daily at 07:00 and the prune weekly (Mon 07:40); on startup each is caught up only if its last success is too old (20 h / 7 days); a failure is isolated and recorded like the other jobs.
- [x] AC-4: The prune job deletes HN stories older than 30 days and snapshots of untracked repos, and nothing else.
- [x] AC-5: `GET /api/news` returns stories from the last 7 days with points/hour, HN link and linked repo name.
- [x] AC-6: The News page lists those stories with working search and sort; the status panel shows the HN and prune jobs; no console errors; typecheck and build pass.
- [x] AC-7: Parsing, GitHub-URL matching, merging of the two queries, points/hour and prune cutoffs are unit-tested on saved Algolia fixtures.

## Out of scope

- Keyword/topic filtering and news scoring (spec 003).
- Fetching article text for cards (spec 004).
- The "never reached a brief" pruning rule (spec 005, once briefs exist).
- Comments content.

## Open questions

Logged in [docs/qa/questions.md](../../docs/qa/questions.md).

- [x] Q-010: Front page + stories > 100 points / 24 h.
- [x] Q-011: Store all, filter in scoring.
- [x] Q-012: Small News page now.
- [x] Q-013: Prune HN > 30 days and untracked snapshots only.
- [x] Q-014: Daily HN at 07:00, popular window 26 h; prune weekly.

## QA

Test cases: [docs/qa/test-cases/002-hn-collector.md](../../docs/qa/test-cases/002-hn-collector.md)

## Change log

- 2.0 (2026-10-11): Daily schedule (Q-014): HN 07:00 instead of hourly, popular window 24 → 26 h, prune Mondays 07:40; startup catch-up only for stale jobs. AC-3 rewritten; TC-002-03 and TC-002-07 updated.
- 1.0 (2026-10-11): Created and approved from the user's answers to Q-010…Q-013; implementation started.
