"""llm_usage: one row per LLM call, for the monthly token cap (spec 004, REQ-CRD-004).

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-11
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "llm_usage",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("model", sa.Text, nullable=False),
        sa.Column("purpose", sa.Text, nullable=False),
        sa.Column("item_type", sa.Text),
        sa.Column("item_id", sa.Integer),
        sa.Column("input_tokens", sa.Integer, nullable=False),
        sa.Column("output_tokens", sa.Integer, nullable=False),
        sa.Column("ok", sa.Boolean, nullable=False),
        sa.Column("error", sa.Text),
    )
    op.create_index("ix_llm_usage_at", "llm_usage", ["at"])


def downgrade() -> None:
    op.drop_index("ix_llm_usage_at", table_name="llm_usage")
    op.drop_table("llm_usage")
