import sys
sys.path.append("C:/ITA/csi-28/deepmuscle-app-api")
from sql.models import (
    DayExercises,
    Exercises,
    UserDetails,
    Users,
    WorkoutDays,
    Workouts,
)
import datetime
from sql.database import SessionLocal
from sqlalchemy import func, text

db = SessionLocal()

def reset_exercise_id_sequence(db):
    max_id = db.query(func.max(Exercises.id)).scalar()
    if max_id is not None:
        db.execute(text(f"ALTER SEQUENCE exercises_id_seq RESTART WITH {max_id + 1}"))
        db.commit()
    print("Exercise ID sequence reset")

reset_exercise_id_sequence(db)

def test_exercise_add(db):
    new_exercise = Exercises(
        name="teste",
        category="teste",
        description="teste",
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),)
    db.add(new_exercise)
    db.commit()
    db.refresh(new_exercise)
    
test_exercise_add(db)
    