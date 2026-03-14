"""add_theory_validation_fields

Revision ID: c58e1a49d413
Revises: c92728ca1ff0
Create Date: 2026-03-12 13:10:47.767019

WO-21: Theory registration and validation
"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'c58e1a49d413'
down_revision: Union[str, Sequence[str], None] = 'c92728ca1ff0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add theory validation fields for WO-21."""
    op.add_column('theories', sa.Column('identifier', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('theories', sa.Column('version', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('theories', sa.Column('code', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('theories', sa.Column('validation_passed', sa.Boolean(), nullable=True))
    op.add_column('theories', sa.Column('validation_report', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.create_index(op.f('ix_theories_identifier'), 'theories', ['identifier'], unique=True)


def downgrade() -> None:
    """Remove theory validation fields."""
    op.drop_index(op.f('ix_theories_identifier'), table_name='theories')
    op.drop_column('theories', 'validation_report')
    op.drop_column('theories', 'validation_passed')
    op.drop_column('theories', 'code')
    op.drop_column('theories', 'version')
    op.drop_column('theories', 'identifier')
