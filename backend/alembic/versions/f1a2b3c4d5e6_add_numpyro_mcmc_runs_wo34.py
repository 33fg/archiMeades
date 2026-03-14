"""add_numpyro_mcmc_runs_wo34

Revision ID: f1a2b3c4d5e6
Revises: e5f9c3d2b7a1
Create Date: 2026-03-12

WO-34: NumPyro HMC-NUTS Sampling Integration
"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "e5f9c3d2b7a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "numpyro_mcmc_runs",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("theory_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("dataset_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("prior_config", sa.JSON(), nullable=False),
        sa.Column("num_samples", sa.Integer(), nullable=False),
        sa.Column("num_warmup", sa.Integer(), nullable=False),
        sa.Column("num_chains", sa.Integer(), nullable=False),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("posterior_ref", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("error_message", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_numpyro_mcmc_runs_theory_id"), "numpyro_mcmc_runs", ["theory_id"])
    op.create_index(op.f("ix_numpyro_mcmc_runs_dataset_id"), "numpyro_mcmc_runs", ["dataset_id"])
    op.create_index(op.f("ix_numpyro_mcmc_runs_status"), "numpyro_mcmc_runs", ["status"])


def downgrade() -> None:
    op.drop_index(op.f("ix_numpyro_mcmc_runs_status"), table_name="numpyro_mcmc_runs")
    op.drop_index(op.f("ix_numpyro_mcmc_runs_dataset_id"), table_name="numpyro_mcmc_runs")
    op.drop_index(op.f("ix_numpyro_mcmc_runs_theory_id"), table_name="numpyro_mcmc_runs")
    op.drop_table("numpyro_mcmc_runs")
