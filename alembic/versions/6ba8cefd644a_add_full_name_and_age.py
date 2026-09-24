"""add full_name and age

Revision ID: 6ba8cefd644a
Revises: 7cf2e6296515
Create Date: 2026-09-24 11:29:26.160716

"""
from typing import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '6ba8cefd644a'
down_revision: Union[str, Sequence[str], None] = '7cf2e6296515'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('full_name', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('age', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'age')
    op.drop_column('users', 'full_name')
    # ### end Alembic commands ###
