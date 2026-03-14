"""add_api_keys_and_usage_wo48

Revision ID: d4a8f2b1c5e6
Revises: c58e1a49d413
Create Date: 2026-03-12 18:00:00.000000

WO-48: API Authentication and Rate Limiting Infrastructure
"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = "d4a8f2b1c5e6"
down_revision: Union[str, Sequence[str], None] = "c58e1a49d413"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "api_keys",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("key_hash", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("email", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("affiliation", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("rate_limit_per_hour", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("last_used_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_api_keys_key_hash"), "api_keys", ["key_hash"], unique=True)
    op.create_index(op.f("ix_api_keys_name"), "api_keys", ["name"], unique=False)
    op.create_index(op.f("ix_api_keys_email"), "api_keys", ["email"], unique=False)
    op.create_index(op.f("ix_api_keys_expires_at"), "api_keys", ["expires_at"], unique=False)

    op.create_table(
        "api_usage",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("api_key_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("endpoint", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("theory_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("parameters_json", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.ForeignKeyConstraint(["api_key_id"], ["api_keys.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_api_usage_api_key_id"), "api_usage", ["api_key_id"], unique=False)
    op.create_index(op.f("ix_api_usage_endpoint"), "api_usage", ["endpoint"], unique=False)
    op.create_index(op.f("ix_api_usage_theory_id"), "api_usage", ["theory_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_api_usage_theory_id"), table_name="api_usage")
    op.drop_index(op.f("ix_api_usage_endpoint"), table_name="api_usage")
    op.drop_index(op.f("ix_api_usage_api_key_id"), table_name="api_usage")
    op.drop_table("api_usage")
    op.drop_index(op.f("ix_api_keys_expires_at"), table_name="api_keys")
    op.drop_index(op.f("ix_api_keys_email"), table_name="api_keys")
    op.drop_index(op.f("ix_api_keys_name"), table_name="api_keys")
    op.drop_index(op.f("ix_api_keys_key_hash"), table_name="api_keys")
    op.drop_table("api_keys")
