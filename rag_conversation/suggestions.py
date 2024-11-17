import json
import re
from fastapi import HTTPException
from sql.schemas import UserDetailsCreate
from rag_conversation.chain_classifier import chain_classifier, retriever, _combine_documents


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


# Updated generate_workout_suggestions function
def generate_workout_suggestions(user_details: UserDetailsCreate) -> dict:
    prompt_context = f"""
    Idade: {user_details.age}
    Altura: {user_details.height}
    Peso: {user_details.weight}
    Gênero: {user_details.gender}
    Nível de condicionamento físico: {user_details.fitness_level}
    """

    try:
        # Retrieve relevant context using user details as the query
        query = f"Plano de treino para {user_details.fitness_level} nível de condicionamento físico."
        retrieved_context = retriever._get_relevant_documents(query, run_manager=None)

        if not retrieved_context:
            raise ValueError("No relevant context retrieved from Pinecone.")

        # Combine retrieved context with prompt context
        context_combined = _combine_documents(retrieved_context)
        combined_input = f"{prompt_context}\n\n{context_combined}"

        # Invoke the chain classifier with question and context
        response = chain_classifier.invoke(
            {
                "question": "Crie um plano de treino personalizado com base nas informações fornecidas.",
                "context": combined_input,
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
