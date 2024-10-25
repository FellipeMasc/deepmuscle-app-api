"""Create User Training

Revision ID: 576f4985fe15
Revises: 784e55206630
Create Date: 2024-10-24 10:26:53.904585

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '576f4985fe15'
down_revision: Union[str, None] = '784e55206630'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "user_training",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("height", sa.Float(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("training_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_foreign_key(
        "fk_user_training_user_id",
        "user_training",
        "users",
        ["user_id"],
        ["id"],
    )


def downgrade():
    op.drop_table("user_training")
    pass
