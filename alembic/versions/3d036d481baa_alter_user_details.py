"""alter user details

Revision ID: 3d036d481baa
Revises: 0c0f4e50859f
Create Date: 2024-10-25 10:17:21.811202

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d036d481baa'
down_revision: Union[str, None] = '0c0f4e50859f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("user_details", sa.Column("gender", sa.String(), nullable=True))
    op.add_column("user_details", sa.Column("age", sa.Integer(), nullable=True))
    op.add_column("user_details", sa.Column("fitness_level", sa.String(), nullable=True))


def downgrade() -> None:
    pass
