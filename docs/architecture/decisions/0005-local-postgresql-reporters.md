# 0005. The Reporters database on a local PostgreSQL install

- **Status:** Accepted
- **Date:** 2026-10-11
- **Supersedes:** [0002](0002-postgresql.md) (the "in Docker" part; PostgreSQL itself stays)

## Context

ADR-0002 chose PostgreSQL 17 in Docker. In practice the project has always run on the user's own **PostgreSQL 18 installed on Windows** (service `postgresql-x64-18`), in a database named **Reporters**: `.env` points there and all data lives there. The Docker container was never used; when Q-018 bound it to 127.0.0.1, it could no longer start because the local PostgreSQL owns port 5432 (Q-024).

## Options considered

1. **Local PostgreSQL, database `Reporters` (what's in use):** no Docker needed to run the app; the user manages the server.
2. **Docker Postgres as originally planned:** reproducible, but needs a migration of the existing data and a free port.

## Decision

The app uses the **Reporters** database on the local PostgreSQL (`DATABASE_URL` in `.env`). Docker Compose stays in the repo as an optional alternative on host port 5433 (so it never clashes with a local install); it is not required.

## Consequences

- Setup docs say "PostgreSQL 15+ (local install or Docker)"; the migration commands are the same.
- Securing the server is the user's job: as of 2026-10-11 it listens on all interfaces (`listen_addresses = '*'`); set it to `'localhost'` in `C:\Program Files\PostgreSQL\18\data\postgresql.conf` and restart the service.
- pgvector (v1 embeddings) must be installed into the local PostgreSQL when needed; the Docker image had it built in.
