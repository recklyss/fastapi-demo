"""add phone_number to user table

Revision ID: 7cf2e6296515
Revises: b7c4e1a90f12
Create Date: 2026-09-21 14:40:59.614079

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7cf2e6296515'
down_revision: Union[str, Sequence[str], None] = 'b7c4e1a90f12'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("phone_number", sa.String(length=20), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "phone_number")
