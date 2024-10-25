"""alter column nullable in user detail

Revision ID: 15b474505423
Revises: 3d036d481baa
Create Date: 2024-10-25 20:13:42.941158

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '15b474505423'
down_revision: Union[str, None] = '3d036d481baa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('user_details', 'workout_id', new_column_name='workout_id', existing_type=sa.INTEGER(), nullable=True)


def downgrade() -> None:
    pass
