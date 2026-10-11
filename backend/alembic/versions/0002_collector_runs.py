"""collector_runs: one row per background job run (spec 008, REQ-COL-007).

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-11
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TS = sa.DateTime(timezone=True)


def upgrade() -> None:
    op.create_table(
        "collector_runs",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("job", sa.Text, nullable=False),
        sa.Column("started_at", TS, nullable=False),
        sa.Column("finished_at", TS, nullable=False),
        sa.Column("ok", sa.Boolean, nullable=False),
        sa.Column("result", sa.Integer),
        sa.Column("error", sa.Text),
    )
    op.create_index("ix_collector_runs_job_started", "collector_runs", ["job", "started_at"])


def downgrade() -> None:
    op.drop_index("ix_collector_runs_job_started", table_name="collector_runs")
    op.drop_table("collector_runs")
