import json
import re
from fastapi import HTTPException
from sql.schemas import UserDetailsCreate
from chain_classifier import chain_classifier


# Function to parse response and ensure valid JSON
def parse_json_response(response: str) -> dict:
    try:
        # Use regex to extract JSON from the response if there's additional text
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            raise ValueError("No valid JSON found in the response.")
    except json.JSONDecodeError:
        raise ValueError("Failed to parse JSON from the response.")


# Function to generate workout suggestions using the adapted chain
def generate_workout_suggestions(user_details: UserDetailsCreate) -> dict:
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
                "question": "Crie um plano de treino personalizado com base nas informações fornecidas.",
                "context": prompt_context,
            }
        )

        # Attempt to parse the response as JSON
        workout_plan = parse_json_response(response)
        return workout_plan

    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse the workout plan response: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while generating workout suggestions: {str(e)}",
        )
