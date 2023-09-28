

# Langchain used chatbot agent - Total failure

import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

from langchain.agents import Tool
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent

from llama_index import VectorStoreIndex, SimpleDirectoryReader

import os, logging,openai
from pathlib import Path
from dotenv import load_dotenv

# Set base directory and load environment variables -- IT is must

BASE_DIR = Path(__file__).resolve().parent
dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path)
openai.api_key = os.environ["OPENAI_API_KEY"]

cwd = os.getcwd()


file_repo_path = os.path.join(cwd, "file_repo")
index_repo_path = os.path.join(cwd, "index_repo")


documents = SimpleDirectoryReader(file_repo_path).load_data()
index = VectorStoreIndex.from_documents(documents=documents)

tools = [
    Tool(
        name="LlamaIndex",
        func=lambda q: str(index.as_query_engine().query(q)),
        description="various immigration services of botswana government",
        return_direct=True,
    ),
]

# set Logging to DEBUG for more detailed outputs
memory = ConversationBufferMemory(memory_key="chat_history")
llm = ChatOpenAI(temperature=0)
agent_executor = initialize_agent(
    tools, llm, agent="conversational-react-description", memory=memory
)
while True:
    question = input("ask?\n")
    response = agent_executor.run(input=question)
    print(response)
