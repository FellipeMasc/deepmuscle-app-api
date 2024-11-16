import os
from operator import itemgetter
from typing import List, Tuple

from langchain_openai import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    format_document,
)
from langchain_core.prompts.prompt import PromptTemplate
from pydantic import BaseModel, Field
from langchain_core.runnables import (
    RunnableBranch,
    RunnableLambda,
    RunnableParallel,
)
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
import json
import re

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

# RAG answer synthesis prompt specifically for workout plan in Portuguese
template = """Com base nas informações do usuário e no contexto fornecido, crie um plano de treino personalizado em formato JSON que possa ser armazenado no banco de dados.
Informações do Usuário:
{context}

Use as informações do usuário, como idade, nível de condicionamento físico, gênero, altura e peso, em conjunto com o contexto da base de dados para criar um plano que inclua:
- Um nome adequado para o treino.
- Uma descrição detalhada do plano de treino.
- Exercícios para diferentes dias da semana (pelo menos 4 dias), incluindo uma variedade de atividades.
- Cada exercício deve incluir o nome, a categoria (por exemplo, Força, Cardio, Flexibilidade) e uma descrição.

Apenas forneça uma resposta em JSON no seguinte formato (não inclua nenhuma explicação ou texto adicional fora deste formato):
{{
    "workout_name": "Plano de Treino Personalizado",
    "description": "Um plano de treino elaborado especificamente para as necessidades do usuário.",
    "days": [
        {{
            "day": "Segunda-feira",
            "exercises": [
                {{
                    "name": "Nome do exercício",
                    "category": "Categoria",
                    "description": "Descrição do exercício."
                }}
            ]
        }},
        {{
            "day": "Terça-feira",
            "exercises": [
                {{
                    "name": "Nome do exercício",
                    "category": "Categoria",
                    "description": "Descrição do exercício."
                }}
            ]
        }},
        {{
            "day": "Quarta-feira",
            "exercises": [
                {{
                    "name": "Nome do exercício",
                    "category": "Categoria",
                    "description": "Descrição do exercício."
                }}
            ]
        }},
        {{
            "day": "Quinta-feira",
            "exercises": [
                {{
                    "name": "Nome do exercício",
                    "category": "Categoria",
                    "description": "Descrição do exercício."
                }}
            ]
        }},
        {{
            "day": "Sexta-feira",
            "exercises": [
                {{
                    "name": "Nome do exercício",
                    "category": "Categoria",
                    "description": "Descrição do exercício."
                }}
            ]
        }}
    ]
}}
Certifique-se de que a resposta seja um JSON válido, sem nenhum texto adicional fora da estrutura JSON."""  # Reforcei que a resposta deve ser exclusivamente em JSON.
ANSWER_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", template),
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


_search_query = RunnableLambda(itemgetter("question"))

_inputs = RunnableParallel(
    {
        "question": lambda x: x["question"],
        "context": _search_query | retriever | _combine_documents,
    }
).with_types(input_type=None)

# Chain for generating structured workout suggestions
chain_classifier = (
    _inputs
    | ANSWER_PROMPT
    | ChatOpenAI(model="gpt-4", temperature=0.7)
    | StrOutputParser()
)
