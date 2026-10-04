# My-Reporters-Agent-Workspace

A platform to manage, control and view agents that report on news and repos.

The first project here is **Tech Radar**: a local web app that collects rising GitHub repos and AI news, scores them, writes short cards with Claude, and shows a daily brief you can rate with 👍/👎.

- MVP scope: [requirements/Tech Radar — MVP.md](requirements/Tech%20Radar%20—%20MVP.md)
- Full v1 roadmap: [requirements/Tech Radar — v1 Requirements.md](requirements/Tech%20Radar%20—%20v1%20Requirements.md)

## Stack

| Layer | Choice |
| --- | --- |
| Backend | Python 3.12+, FastAPI, APScheduler (in-process jobs) |
| Database | PostgreSQL 17 (pgvector image) in Docker, SQLAlchemy 2.0 async + asyncpg, Alembic |
| Collectors | httpx, tenacity, selectolax |
| LLM | Claude via the official `anthropic` SDK |
| Frontend | React 19, Vite, TypeScript, Tailwind CSS, TanStack Query, React Router |
| Tooling | uv, ruff, pytest |

## Project layout

```text
.
├── config.yaml            # keywords, brief time, top-N counts, LLM model and budget
├── .env.example           # secrets template (copy to .env)
├── docker-compose.yml     # Postgres
├── backend/
│   ├── pyproject.toml     # source of truth for Python deps (uv)
│   ├── requirements.txt   # exported from uv, for pip users
│   ├── alembic/           # DB migrations
│   ├── prompts/card.md    # the card prompt, tuned by hand
│   ├── app/
│   │   ├── main.py        # FastAPI app, scheduler start/stop, serves frontend/dist
│   │   ├── config.py      # loads .env + config.yaml
│   │   ├── db.py  models.py  scheduler.py
│   │   └── api/           # /api/* routes
│   └── tests/
├── frontend/
│   └── src/ pages/ (Today, Leaderboard, Stats, Card)  api/
└── requirements/          # product docs
```

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (installs Python for you)
- [Node.js](https://nodejs.org/) 20.19+ or 22 LTS
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (for Postgres)

## First-time setup

```powershell
# 1. Secrets
Copy-Item .env.example .env      # then fill in GITHUB_TOKEN and ANTHROPIC_API_KEY

# 2. Database
docker compose up -d db

# 3. Backend
cd backend
uv sync                          # or: pip install -r requirements.txt
uv run alembic upgrade head
cd ..

# 4. Frontend
cd frontend
npm install
cd ..
```

## Running

**Development** (two terminals, hot reload):

```powershell
cd backend;  uv run fastapi dev app/main.py      # http://localhost:8000/docs
cd frontend; npm run dev                          # http://localhost:5173
```

The Vite dev server proxies `/api` to the backend.

**Daily use** (one process, one URL):

```powershell
cd frontend; npm run build; cd ..
cd backend;  uv run fastapi run app/main.py      # http://localhost:8000
```

When `frontend/dist` exists, FastAPI serves it alongside the API.

## Common tasks

```powershell
# Backend (from backend/)
uv run pytest                                    # tests
uv run ruff check . ; uv run ruff format .       # lint + format
uv run alembic revision --autogenerate -m "..."  # new migration after editing models.py
uv add <package>                                 # add a dependency, then refresh requirements.txt:
uv export --no-hashes --no-dev -o requirements.txt

# Frontend (from frontend/)
npm run typecheck
npm run gen:api      # regenerate TS types from the backend's OpenAPI (backend must be running)
```

## Configuration

- **`.env`**: `DATABASE_URL`, `GITHUB_TOKEN`, `ANTHROPIC_API_KEY` and the Postgres credentials used by Docker Compose.
- **`config.yaml`**: interest keywords, brief time and timezone, top-N counts, collector intervals, Claude model, effort and monthly budget cap.

## Status

- [x] Skeleton: Docker Compose, config, schema + migration, FastAPI, React shell
- [ ] GitHub collectors (Trending + API star snapshots)
- [ ] Hacker News collector
- [ ] Scoring
- [ ] Cards (Claude)
- [ ] Today page: daily brief with 👍/👎
- [ ] Weekly leaderboard
- [ ] Stats page
