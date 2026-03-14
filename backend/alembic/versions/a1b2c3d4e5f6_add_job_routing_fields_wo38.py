"""add_job_routing_fields_wo38

Revision ID: a1b2c3d4e5f6
Revises: f1a2b3c4d5e6
Create Date: 2026-03-13

WO-38: Job Submission and Cost-Based Routing
"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy import inspect

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "f1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    table_names = inspector.get_table_names()

    if "jobs" not in table_names:
        op.create_table(
            "jobs",
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column("celery_task_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("job_type", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column("progress_percent", sa.Float(), nullable=False),
            sa.Column("error_message", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("result_ref", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("started_at", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("completed_at", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("priority", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("retry_count", sa.Integer(), nullable=True),
            sa.Column("max_retries", sa.Integer(), nullable=True),
            sa.Column("estimated_flops", sa.Float(), nullable=True),
            sa.Column("estimated_memory_mb", sa.Float(), nullable=True),
            sa.Column("target_backend", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("user_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("payload_json", sa.JSON(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_jobs_celery_task_id"), "jobs", ["celery_task_id"])
        op.create_index(op.f("ix_jobs_job_type"), "jobs", ["job_type"])
        op.create_index(op.f("ix_jobs_status"), "jobs", ["status"])
        op.create_index(op.f("ix_jobs_target_backend"), "jobs", ["target_backend"])
    else:
        op.add_column("jobs", sa.Column("priority", sqlmodel.sql.sqltypes.AutoString(), nullable=True))
        op.add_column("jobs", sa.Column("retry_count", sa.Integer(), nullable=True))
        op.add_column("jobs", sa.Column("max_retries", sa.Integer(), nullable=True))
        op.add_column("jobs", sa.Column("estimated_flops", sa.Float(), nullable=True))
        op.add_column("jobs", sa.Column("estimated_memory_mb", sa.Float(), nullable=True))
        op.add_column("jobs", sa.Column("target_backend", sqlmodel.sql.sqltypes.AutoString(), nullable=True))
        op.add_column("jobs", sa.Column("user_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True))
        op.add_column("jobs", sa.Column("payload_json", sa.JSON(), nullable=True))
        op.create_index(op.f("ix_jobs_target_backend"), "jobs", ["target_backend"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "jobs" not in inspector.get_table_names():
        return
    try:
        op.drop_index(op.f("ix_jobs_target_backend"), table_name="jobs")
    except Exception:
        pass
    for col in ["payload_json", "user_id", "target_backend", "estimated_memory_mb", "estimated_flops", "max_retries", "retry_count", "priority"]:
        try:
            op.drop_column("jobs", col)
        except Exception:
            pass
