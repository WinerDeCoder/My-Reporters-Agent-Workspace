# 0002. PostgreSQL from day one

- **Status:** Superseded by [0005](0005-local-postgresql-reporters.md) (the Docker part; PostgreSQL itself stays)
- **Date:** 2026-10-04

## Context

The MVP draft used SQLite. v1 needs embeddings (pgvector) for relevance and watches. I prefer PostgreSQL.

## Options considered

1. **SQLite:** zero setup, one file. Migrating to Postgres later means a data move and dialect fixes.
2. **PostgreSQL in Docker (pgvector image):** one `docker compose up`; JSONB, arrays and pgvector available now. Needs Docker Desktop running.

## Decision

PostgreSQL 17 using the `pgvector/pgvector:pg17` image, accessed through SQLAlchemy 2.0 async + asyncpg, with Alembic migrations.

## Consequences

- Docker Desktop must be running before the app starts.
- Schema changes go through Alembic migrations.
- v1 embeddings need no database change.
