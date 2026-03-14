"""add_job_checkpoint_wo39

Revision ID: g7h8i9j0k1l2
Revises: f2b3c4d5e6a7
Create Date: 2026-03-14

WO-39: Job Persistence, Checkpointing, and Recovery
"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = "g7h8i9j0k1l2"
down_revision: Union[str, Sequence[str], None] = "f2b3c4d5e6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "jobs",
        sa.Column("checkpoint_s3_key", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("jobs", "checkpoint_s3_key")
