"""add simulation params

Revision ID: f2b3c4d5e6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-13

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f2b3c4d5e6a7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "simulations",
        sa.Column("params_json", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("simulations", "params_json")
