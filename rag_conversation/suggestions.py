import json
from fastapi import HTTPException
from sql.schemas import UserDetailsCreate
from rag_conversation.chain_classifier import chain_classifier


# Function to generate workout suggestions using the adapted chain
async def generate_workout_suggestions(user_details: UserDetailsCreate) -> dict:
    # Constructing prompt context based on user details
    prompt_context = f"""
    Age: {user_details.age}
    Height: {user_details.height} cm
    Weight: {user_details.weight} kg
    Gender: {user_details.gender}
    Fitness Level: {user_details.fitness_level}
    """

    try:
        response = chain_classifier.invoke(
            {
                "chat_history": [],
                "question": "Create a personalized workout plan",
                "context": prompt_context,
            }
        )
        # Assuming response is a valid JSON formatted string
        workout_plan = json.loads(response)
        return workout_plan
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500, detail="Failed to parse the workout plan response."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while generating workout suggestions: {str(e)}",
        )


# Test the function
async def test_generate_workout_suggestions():
    test_user_details = UserDetailsCreate(
        age=25, height=175.0, weight=70.0, gender="Male", fitness_level="Intermediate"
    )
    try:
        workout_suggestions = await generate_workout_suggestions(test_user_details)
        print("Workout Suggestions:", workout_suggestions)
    except HTTPException as e:
        print("Error:", e.detail)
