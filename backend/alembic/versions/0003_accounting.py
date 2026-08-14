"""chart of accounts and journal entries

Revision ID: 0003
Revises: 0002
Create Date: 2026-08-14

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
        "accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(16), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", sa.String(16), nullable=False),
        sa.Column("parent_id", sa.Integer(), sa.ForeignKey("accounts.id"), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_accounts_code", "accounts", ["code"], unique=True)

    op.create_table(
        "journal_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("description", sa.String(255), nullable=False),
        sa.Column("reference_type", sa.String(16), nullable=False),
        sa.Column("reference_id", sa.Integer(), nullable=True),
        sa.Column("date", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "journal_entry_lines",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "journal_entry_id", sa.Integer(), sa.ForeignKey("journal_entries.id"), nullable=False
        ),
        sa.Column("account_id", sa.Integer(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("debit", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("credit", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("description", sa.Text(), nullable=True),
    )
    op.create_index("ix_journal_entry_lines_account_id", "journal_entry_lines", ["account_id"])


def downgrade() -> None:
    op.drop_index("ix_journal_entry_lines_account_id", table_name="journal_entry_lines")
    op.drop_table("journal_entry_lines")
    op.drop_table("journal_entries")
    op.drop_index("ix_accounts_code", table_name="accounts")
    op.drop_table("accounts")
