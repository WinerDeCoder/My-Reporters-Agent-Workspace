"""Initial schema: repos, repo_snapshots, news_items, cards, briefs, feedback.

Revision ID: 0001
Revises:
Create Date: 2026-10-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TS = sa.DateTime(timezone=True)


def upgrade() -> None:
    op.create_table(
        "repos",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("full_name", sa.Text, nullable=False, unique=True),
        sa.Column("description", sa.Text),
        sa.Column("topics", postgresql.ARRAY(sa.Text), nullable=False, server_default="{}"),
        sa.Column("language", sa.Text),
        sa.Column("license", sa.Text),
        sa.Column("readme_hash", sa.Text),
        sa.Column("first_seen", TS, nullable=False, server_default=sa.func.now()),
        sa.Column("last_seen", TS, nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "repo_snapshots",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column(
            "repo_id",
            sa.Integer,
            sa.ForeignKey("repos.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("taken_at", TS, nullable=False, server_default=sa.func.now()),
        sa.Column("stars", sa.Integer, nullable=False),
        sa.Column("forks", sa.Integer, nullable=False),
    )
    op.create_index("ix_repo_snapshots_repo_taken", "repo_snapshots", ["repo_id", "taken_at"])

    op.create_table(
        "news_items",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("hn_id", sa.BigInteger, nullable=False, unique=True),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("url", sa.Text),
        sa.Column("points", sa.Integer, nullable=False),
        sa.Column("comments", sa.Integer, nullable=False),
        sa.Column("posted_at", TS, nullable=False),
        sa.Column("linked_repo_id", sa.Integer, sa.ForeignKey("repos.id", ondelete="SET NULL")),
        sa.Column("fetched_at", TS, nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "cards",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("item_type", sa.Text, nullable=False),
        sa.Column("item_id", sa.Integer, nullable=False),
        sa.Column("content", postgresql.JSONB, nullable=False),
        sa.Column("model", sa.Text, nullable=False),
        sa.Column("source_hash", sa.Text),
        sa.Column("created_at", TS, nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("item_type IN ('repo', 'news')", name="ck_cards_item_type"),
    )
    op.create_index("ix_cards_item", "cards", ["item_type", "item_id"])

    op.create_table(
        "briefs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("type", sa.Text, nullable=False),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("items", postgresql.JSONB, nullable=False),
        sa.Column("created_at", TS, nullable=False, server_default=sa.func.now()),
        sa.Column("opened_at", TS),
        sa.CheckConstraint("type IN ('daily', 'weekly')", name="ck_briefs_type"),
        sa.UniqueConstraint("type", "date", name="uq_briefs_type_date"),
    )

    op.create_table(
        "feedback",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("item_type", sa.Text, nullable=False),
        sa.Column("item_id", sa.Integer, nullable=False),
        sa.Column("rating", sa.SmallInteger, nullable=False),
        sa.Column("brief_id", sa.Integer, sa.ForeignKey("briefs.id", ondelete="SET NULL")),
        sa.Column("rated_at", TS, nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("item_type IN ('repo', 'news')", name="ck_feedback_item_type"),
        sa.CheckConstraint("rating IN (-1, 1)", name="ck_feedback_rating"),
    )


def downgrade() -> None:
    op.drop_table("feedback")
    op.drop_table("briefs")
    op.drop_index("ix_cards_item", table_name="cards")
    op.drop_table("cards")
    op.drop_table("news_items")
    op.drop_index("ix_repo_snapshots_repo_taken", table_name="repo_snapshots")
    op.drop_table("repo_snapshots")
    op.drop_table("repos")
