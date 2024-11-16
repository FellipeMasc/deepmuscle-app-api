import os
from operator import itemgetter
from typing import List, Tuple

from langchain_openai import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    format_document,
)
from langchain_core.prompts.prompt import PromptTemplate
from pydantic import BaseModel, Field
from langchain_core.runnables import (
    RunnableBranch,
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
)
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
import json

load_dotenv()

# Load environment variables
if os.environ.get("PINECONE_API_KEY", None) is None:
    raise Exception("Missing `PINECONE_API_KEY` environment variable.")

PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX", "langchain-test")

# Create vectorstore retriever
vectorstore = PineconeVectorStore.from_existing_index(
    PINECONE_INDEX_NAME, HuggingFaceEmbeddings()
)
retriever = vectorstore.as_retriever()

# Condense a chat history and follow-up question into a standalone question
_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.
Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""  # noqa: E501
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)

# RAG answer synthesis prompt specifically for workout plan
template = """Based on the user's information, provide a workout plan in JSON format that can be stored in the database.
User Information:
{context}
Provide a JSON response in the following format:
{{
    "workout_name": "Workout Plan for Beginner",
    "description": "A personalized workout plan based on user details.",
    "days": [
        {{
            "day": "Monday",
            "exercises": [
                {{
                    "name": "Push-up",
                    "category": "Strength",
                    "description": "A bodyweight exercise for upper body strength."
                }},
                {{
                    "name": "Squat",
                    "category": "Strength",
                    "description": "A lower body exercise focusing on the quadriceps and glutes."
                }}
            ]
        }},
        {{
            "day": "Wednesday",
            "exercises": [
                {{
                    "name": "Plank",
                    "category": "Core",
                    "description": "An exercise to strengthen the core muscles."
                }}
            ]
        }}
    ]
}}
Make sure the response is a valid JSON."""
ANSWER_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", template),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{question}"),
    ]
)

# Conversational Retrieval Chain
DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")


def _combine_documents(
    docs, document_prompt=DEFAULT_DOCUMENT_PROMPT, document_separator="\n\n"
):
    doc_strings = [format_document(doc, document_prompt) for doc in docs]
    return document_separator.join(doc_strings)


def _format_chat_history(chat_history: List[Tuple[str, str]]) -> List:
    buffer = []
    for human, ai in chat_history:
        buffer.append(HumanMessage(content=human))
        buffer.append(AIMessage(content=ai))
    return buffer


# User input
class ChatHistory(BaseModel):
    chat_history: List[Tuple[str, str]] = Field(..., extra={"widget": {"type": "chat"}})
    question: str


_search_query = RunnableBranch(
    # If input includes chat_history, we condense it with the follow-up question
    (
        RunnableLambda(lambda x: bool(x.get("chat_history"))).with_config(
            run_name="HasChatHistoryCheck"
        ),  # Condense follow-up question and chat into a standalone_question
        RunnablePassthrough.assign(
            chat_history=lambda x: _format_chat_history(x["chat_history"])
        )
        | CONDENSE_QUESTION_PROMPT
        | ChatOpenAI(temperature=0, max_tokens=100, model="gpt-3.5-turbo")
        | StrOutputParser(),
    ),
    # Else, we have no chat history, so just pass through the question
    RunnableLambda(itemgetter("question")),
)

_inputs = RunnableParallel(
    {
        "question": lambda x: x["question"],
        "chat_history": lambda x: _format_chat_history(x["chat_history"]),
        "context": _search_query | retriever | _combine_documents,
    }
).with_types(input_type=ChatHistory)

# Chain for generating structured workout suggestions
chain_classifier = (
    _inputs
    | ANSWER_PROMPT
    | ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    | StrOutputParser()
)
