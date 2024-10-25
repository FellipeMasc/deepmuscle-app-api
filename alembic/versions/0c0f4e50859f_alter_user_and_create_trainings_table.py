"""alter user and create trainings table

Revision ID: 0c0f4e50859f
Revises: 576f4985fe15
Create Date: 2024-10-25 09:29:21.813411

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c0f4e50859f'
down_revision: Union[str, None] = '576f4985fe15'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("created_at", sa.DateTime(), nullable=True))
    op.add_column("users", sa.Column("updated_at", sa.DateTime(), nullable=True))
    
    op.alter_column("user_training", "training_id", new_column_name="workout_id")
    op.rename_table("user_training", "user_details")
    
    
    op.create_table(
        "workouts",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    
    op.create_table(
        "exercises",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    
    op.create_table(
        "workout_days",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("day", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    
    op.create_table(
        "day_exercises",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("workout_day_id", sa.Integer(), nullable=False),
        sa.Column("exercise_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    
    op.create_foreign_key(
        "fk_day_exercises_exercise_id",
        "day_exercises",
        "exercises",
        ["exercise_id"],
        ["id"],
    )
    
    
    op.create_foreign_key(
        "fk_workout_days_user_id",
        "workout_days",
        "users",
        ["user_id"],
        ["id"],
    )
    
    op.create_foreign_key(
        "fk_day_exercises_workout_day_id",
        "day_exercises",
        "workout_days",
        ["workout_day_id"],
        ["id"],
    )
    
    

def downgrade() -> None:
    op.drop_table("day_exercises")
    op.drop_table("workout_days")
    op.drop_table("exercises")
    op.drop_table("workouts")
    
