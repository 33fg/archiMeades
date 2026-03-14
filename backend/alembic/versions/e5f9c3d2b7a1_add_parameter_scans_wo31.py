"""add_parameter_scans_wo31

Revision ID: e5f9c3d2b7a1
Revises: d4a8f2b1c5e6
Create Date: 2026-03-12

WO-31: Parameter Grid Generation and Scan Configuration
"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = "e5f9c3d2b7a1"
down_revision: Union[str, Sequence[str], None] = "d4a8f2b1c5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "parameter_scans",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("theory_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("dataset_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("axes_config", sa.JSON(), nullable=True),
        sa.Column("fixed_params", sa.JSON(), nullable=True),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("total_points", sa.Integer(), nullable=False),
        sa.Column("result_shape", sa.JSON(), nullable=True),
        sa.Column("result_ref", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("error_message", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("job_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_parameter_scans_theory_id"), "parameter_scans", ["theory_id"])
    op.create_index(op.f("ix_parameter_scans_dataset_id"), "parameter_scans", ["dataset_id"])
    op.create_index(op.f("ix_parameter_scans_status"), "parameter_scans", ["status"])
    op.create_index(op.f("ix_parameter_scans_job_id"), "parameter_scans", ["job_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_parameter_scans_job_id"), table_name="parameter_scans")
    op.drop_index(op.f("ix_parameter_scans_status"), table_name="parameter_scans")
    op.drop_index(op.f("ix_parameter_scans_dataset_id"), table_name="parameter_scans")
    op.drop_index(op.f("ix_parameter_scans_theory_id"), table_name="parameter_scans")
    op.drop_table("parameter_scans")
