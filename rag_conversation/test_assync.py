import asyncio
from suggestions import generate_workout_suggestions
from sql.schemas import UserDetailsCreate


async def test_generate_workout_suggestions():
    test_user_details = UserDetailsCreate(
        age=25, height=175.0, weight=70.0, gender="Male", fitness_level="Intermediate"
    )
    try:
        workout_suggestions = await generate_workout_suggestions(test_user_details)
        print("Workout Suggestions:", workout_suggestions)
    except Exception as e:
        print("Error:", str(e))


if __name__ == "__main__":
    asyncio.run(test_generate_workout_suggestions())
