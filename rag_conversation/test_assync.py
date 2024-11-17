import asyncio
import sys
sys.path.append("C:/ITA/csi-28/deepmuscle-app-api")
from suggestions import generate_workout_suggestions
from sql.schemas import UserDetailsCreate


def test_generate_workout_suggestions():
    test_user_details = UserDetailsCreate(
        age=27, height=175.0, weight=70.0, gender="Male", fitness_level="Intermediate"
    )
    try:
        workout_suggestions = generate_workout_suggestions(test_user_details)
        print("Workout Suggestions:", workout_suggestions)
    except Exception as e:
        print("Error:", str(e))


if __name__ == "__main__":
    test_generate_workout_suggestions()
