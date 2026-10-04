# Tech Radar — v1 Requirements

Oct 4, 2026 · @Nguyen Phuoc Nguyen Phuo

## Vision and v1 goal

Tech Radar is a personal analyst: it reads GitHub, AI research and tech news every day, keeps only what matters to me, and explains each item in plain words. v1 has one job to prove: a daily brief I actually want to read every morning.

v1 is done when:

- A brief arrives every day at a fixed time (UTC+7) with 10 items or fewer.
- Every item has a card that says what it is, what it solves, and why it matters now.
- Rising GitHub repos are ranked by stars gained per day, not total stars.
- I can set up at least one custom watch and see its hits.
- I can rate items, and after two weeks most items feel worth reading.

&#91;embedded content: system overview · 4 stages, 1 feedback loop\]

Collectors feed one processing pipeline; everything is stored, and only the best items reach the brief.

## Core use cases

1. **Morning brief.** I open one message and see the 5 to 10 things worth knowing today, each in two lines.
2. **Understand a repo.** I tap a rising repo and get its card: what it is, the problem, what's special, alternatives, and whether it's worth trying.
3. **Spot momentum.** I see which repos are gaining stars fastest, with a small star-history chart.
4. **Weekly leaderboard.** Once a week I get the top repos ranked by stars gained in the last 7 days, each with a one-line description.
5. **Learn techniques.** I get practical tips (Claude, prompting, skills, agent setups, workflows) and save the good ones to my playbook.
6. **Follow a topic.** I create a watch ("browser agents", "small coding models") and get its hits in the brief, or instantly if it's big.
7. **Get alerted.** I'm pinged only for real events: a major model release, a watched topic spiking, a followed repo shipping a big release.
8. **Ask questions.** I chat over everything collected: "what agent frameworks trended this month?", "compare repo A and B".
9. **Teach it my taste.** I mark items useful or not, and the ranking adapts.

## Sources in v1

v1 starts with four sources that cover repos, research and news; more come only after filtering works well.

| Source | What we collect | How | How often |
| --- | --- | --- | --- |
| GitHub Trending | Trending repos (daily, weekly; all languages + Python, TypeScript, Rust) | Scrape the trending page (no official API) | Every 6 h |
| GitHub API | Stars, star history, description, topics, README, latest release for candidate and followed repos | REST/GraphQL API with a personal token | Every 6 h |
| Hacker News | Top and new stories, points, comment counts, linked URL | Algolia HN Search API | Hourly |
| Hugging Face Daily Papers | Papers of the day, upvotes, abstract, linked arXiv id | Hugging Face API | Daily |
| AI lab and tech blogs | New posts from a starter list of 10 to 20 feeds | RSS/Atom where available | Every 3 h |

New repos also enter as candidates when they appear on HN or in a blog post, so we can track their star velocity before they trend.

## Processing

Every collected item runs the same pipeline; only the top-scored items get an LLM-written card, which keeps cost low.

1. **Normalize** into one Item shape (title, url, source, published time, raw text).
2. **Deduplicate** by canonical URL and repo name; group the same story from several sources into one item.
3. **Enrich**: fetch the README for repos, the abstract for papers, the article text for posts.
4. **Classify** into categories: Repos, Agents and coding, Models, Research, Tools, Tips and techniques, Industry news (cheap model).
5. **Score** each item on three signals:
   - Momentum: stars per day, HN points per hour, paper upvotes.
   - Relevance: similarity to my interests, my watches and my past ratings.
   - Novelty: not already shown to me, not a minor update of something seen.
6. **Write cards** for the top items only (better model).
7. **Store** everything, scored or not, so chat and search can use it later.

Each card has the same fields:

| Field | Answers |
| --- | --- |
| What it is | One sentence, no jargon |
| Problem it solves | Who has this pain and how they handle it today |
| Why now | Why it is trending or released this week |
| What's special | The one idea that sets it apart |
| Alternatives | 1 to 3 similar projects and how this differs |
| Worth trying? | Effort to try, maturity, license |
| Signals | Stars, stars per day, HN points, links |

## Watches

A watch is a standing topic the system checks every new item against, so I can follow a trend without searching for it.

| Field | Example |
| --- | --- |
| Name | Browser agents |
| Description in plain words | Agents that control a web browser to do tasks |
| Keywords and seed repos | browser-use, playwright agent, computer use |
| Sources | All, or a subset |
| Sensitivity | Only big news / normal / everything |
| Delivery | In the daily brief, or instant alert |
| Expires | Never, or on a date |

Matching uses keywords plus meaning (embeddings), so "web automation agent" still hits "browser agents". Each watch has its own page: a timeline of hits, newest first. In v1, watches are created from a form in the dashboard.

## Delivery

The brief goes out once a day; alerts are rare by design, so I keep trusting them.

**Daily brief** (Telegram message plus the Today page in the dashboard):

- Top story: the single most important item, 3 to 4 lines.
- Rising repos: 3 to 5, each with stars gained and one line on what it is.
- Models and research: 1 to 3.
- News: 1 to 3. Tip of the day: one practical technique (Claude, prompting, skills, workflows), ranked by usefulness rather than momentum.
- Watch hits: grouped by watch.
- Every line links to its full card.

**Alerts** fire only when:

- A major model or tool release from a lab on my list.
- A watch set to "instant" gets a strong hit.
- A followed repo publishes a major release.
- A repo crosses a star-velocity threshold I set.

Alerts have a daily cap and quiet hours, both configurable.

**Weekly leaderboard** (every Monday morning, with the brief): the top 10 repos ranked by stars gained in the last 7 days, each with stars gained, total stars and one line on what it is, linking to its card. It is computed from the star snapshots we already store.

## Dashboard and chat

The dashboard is where I browse, manage and dig deeper; v1 needs eight pages.

| Page | What it shows | Actions |
| --- | --- | --- |
| Today | The latest brief | Open card, rate |
| Feed | All scored items | Filter by category, source, date; search |
| Rising repos | Repos ranked by stars per day | Star-history chart, follow repo |
| Leaderboard | This week's top repos by stars gained, plus past weeks | Open card, compare weeks |
| Item | The full card and links | Rate, save, deep dive, chat about it |
| Saved / Playbook | Items and tips I saved, grouped by category | Tag, note, remove |
| Watches | My watches and their hits | Create, edit, pause, delete |
| Settings | Interests, brief time, alert rules, sources | Edit |

**Chat (v1, light):** questions answered from the stored items, with links to the items it used. On an item page, "Deep dive" reads the full README or paper and writes a longer explanation. Creating watches by chat comes later.

## Data model

Nine entities cover v1; star snapshots over time are what make momentum possible.

| Entity | Key fields |
| --- | --- |
| Source | name, type (github, hn, hf, rss), url, schedule, enabled, last run, last error |
| Item | id, source, url, title, raw text, published at, category, scores, embedding, cluster id |
| Repo | full name, description, topics, language, license, followed |
| RepoSnapshot | repo, time, stars, forks (one row per check, for star history and stars per day) |
| Card | item, fields from the card table, model used, created at |
| Watch | name, description, keywords, sources, sensitivity, delivery, expires |
| WatchHit | watch, item, match score, notified |
| Brief | type (daily or weekly leaderboard), date, items in order, sent at, channel |
| Feedback | item, rating, note, time |

Interests (my standing topics of interest) live in Settings and feed the relevance score.

## Non-functional requirements

It is a single-user app that should run cheaply and quietly for months without attention.

- **Users:** just me; a simple login is enough.
- **Hosting:** one small server or my own machine; everything in Docker so it moves easily.
- **Scheduling:** each collector runs on its own schedule; one failing source never blocks the others.
- **Limits:** stay inside API rate limits (GitHub token, HN, HF) and respect each site's terms when scraping.
- **LLM cost:** a monthly budget cap; cheap model for classifying, better model only for cards and deep dives; cache every result.
- **Reliability:** a run log per collector, and an alert to me if a source fails for a day.
- **Time zone:** all schedules in UTC+7.
- **Secrets:** API keys in environment variables, never in code.
- **Retention:** keep cards and scored items; prune raw text of low-score items after a set period.

## Out of scope for v1

These are deliberately left for later so v1 stays small:

- Reddit, X/Twitter, YouTube and podcasts as sources.
- The full arXiv feed (v1 relies on Hugging Face Daily Papers as the filter).
- A written weekly trend recap (v1 ships the weekly leaderboard only).
- Creating and editing watches through chat.
- Multi-user accounts and sharing.
- A mobile app (Telegram covers mobile).
- Automatically cloning and trying repos.

## Open questions

- [ ] Tech stack: Python backend (FastAPI) + Next.js frontend, or all TypeScript?
- [ ] Database: SQLite to start, or Postgres with pgvector from day one?
- [ ] LLM provider(s) and a monthly budget cap.
- [ ] Hosting: my own machine, or a small cloud server?
- [ ] Brief channel: Telegram, email, or both?
- [ ] Brief time each morning.
- [ ] My starting interest list and the first 2 to 3 watches.
- [ ] Starter list of blogs and labs to follow.
- [ ] How long to keep raw data.

## Build order

Each step ends with something usable, so the brief is useful before the dashboard exists.

1. **Collect:** GitHub Trending, GitHub API snapshots and HN into the database, with dedupe and a run log.
2. **Score and card:** momentum and relevance scores, then cards for the top 10.
3. **Brief:** daily brief sent to Telegram. Live with it for a week and tune the scoring.
4. **Dashboard:** Today, Feed, Item, Rising repos, Leaderboard and Saved pages, with ratings; the weekly leaderboard goes out with the brief.
5. **More sources:** Hugging Face Daily Papers and RSS blogs.
6. **Watches:** create, match, show hits in the brief.
7. **Alerts and chat:** event alerts with caps, then chat over stored items and deep dives.
