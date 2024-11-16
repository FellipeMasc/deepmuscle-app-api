import os
from operator import itemgetter
from typing import List, Tuple

from langchain_openai import ChatOpenAI
from langchain_community.embeddings import OpenAIEmbeddings
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
import os
import pandas as pd

load_dotenv()

if os.environ.get("PINECONE_API_KEY", None) is None:
    raise Exception("Missing `PINECONE_API_KEY` environment variable.")

PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX", "langchain-test")



### Ingest code - you may need to run this the first time
# Load
from langchain_community.document_loaders import PDFMinerLoader
# loader = WebBaseLoader("https://lilianweng.github.io/posts/2023-06-23-agent/")
# data = loader.load()
loader = PDFMinerLoader("C:\ITA\csi-28\deepmuscle-app-api\docs\Treinos.pdf")
data = loader.load()
# Load DataFrame
# Split
from langchain_text_splitters import RecursiveCharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
all_splits = text_splitter.split_documents(data)

# Add to vectorDB
vectorstore = PineconeVectorStore.from_documents(
    documents=all_splits, embedding=HuggingFaceEmbeddings(), index_name=PINECONE_INDEX_NAME
)

print(vectorstore)