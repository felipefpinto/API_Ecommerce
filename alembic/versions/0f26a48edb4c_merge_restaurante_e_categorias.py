"""merge restaurante e categorias

Revision ID: 0f26a48edb4c
Revises: 3c4d5e6f7a8b, c7dabc4f51ea
Create Date: 2026-09-08 10:01:21.216515

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0f26a48edb4c'
down_revision: Union[str, Sequence[str], None] = ('3c4d5e6f7a8b', 'c7dabc4f51ea')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
