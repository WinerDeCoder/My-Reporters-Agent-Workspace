# 0003. FastAPI + React, with the scheduler inside the backend process

- **Status:** Accepted
- **Date:** 2026-10-04

## Context

The app needs scheduled collectors, an API and a small UI, running locally on a laptop that may sleep.

## Options considered

1. **All TypeScript** (Next.js + node scheduler): one language, but weaker scraping and data tooling.
2. **Python backend (FastAPI) + React (Vite) frontend:** best libraries for scraping, data and LLMs; typed contract via OpenAPI.
3. **Separate worker process or system cron** for jobs: more robust isolation, more moving parts.

## Decision

FastAPI backend with APScheduler running inside the same process; React + Vite + TypeScript frontend. In daily use FastAPI also serves the built frontend, so it's one process and one URL. Python is managed with uv.

## Consequences

- One process to start; no separate worker.
- Jobs only run while the app runs, so missed jobs need a catch-up on startup (REQ-BRF-002).
- Frontend types are generated from FastAPI's OpenAPI schema.
- If jobs ever slow the API down, move them to a separate worker process.
