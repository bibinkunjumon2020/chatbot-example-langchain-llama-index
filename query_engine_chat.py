


""" Subquery Engine tool used""" # SUCCESS


import openai
from index_handler import load_index

import os, logging
from pathlib import Path
from dotenv import load_dotenv

# Set base directory and load environment variables -- IT is must

BASE_DIR = Path(__file__).resolve().parent
dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path)
openai.api_key = os.environ["OPENAI_API_KEY"]

import nest_asyncio

nest_asyncio.apply()


from llama_index import VectorStoreIndex, SimpleDirectoryReader
from llama_index.tools import QueryEngineTool, ToolMetadata
from llama_index.query_engine import SubQuestionQueryEngine
from llama_index.callbacks import CallbackManager, LlamaDebugHandler
from llama_index import ServiceContext
import json

# Using the LlamaDebugHandler to print the trace of the sub questions
# captured by the SUB_QUESTION callback event type
llama_debug = LlamaDebugHandler(print_trace_on_end=True)
callback_manager = CallbackManager([llama_debug])
service_context = ServiceContext.from_defaults(callback_manager=callback_manager)
cwd = os.getcwd()


file_repo_path = os.path.join(cwd, "file_repo")
index_repo_path = os.path.join(cwd, "index_repo")

#  Using the LlamaDebugHandler to print the trace of the sub questions
# captured by the SUB_QUESTION callback event type
llama_debug = LlamaDebugHandler(print_trace_on_end=True)
callback_manager = CallbackManager([llama_debug])
service_context = ServiceContext.from_defaults(callback_manager=callback_manager)

documents = SimpleDirectoryReader(input_dir=file_repo_path).load_data()
titles=[]

for document in documents:
    # taking title from the string using json
    json_string = document.get_text()
    # Split the JSON string into individual JSON objects
    json_strings = json_string.strip().split('\n')

# Parse and print each JSON object
    for json_str in json_strings:
        try:
            json_data = json.loads(json_str)
            title = str(json_data["title"]).replace(" ", "_")
            titles.append(title)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")


# # Load indices from disk
from llama_index import load_index_from_storage
from llama_index import VectorStoreIndex, ServiceContext, StorageContext

# build index and query engine
vector_query_engine = VectorStoreIndex.from_documents(
    documents, use_async=True, service_context=service_context
).as_query_engine()


# setup base query engine as tool
query_engine_tools = [
    QueryEngineTool(
        query_engine=vector_query_engine,
        metadata=ToolMetadata(
            name="documents", description="details about different botswana government services"
        ),
    ),
]

query_engine = SubQuestionQueryEngine.from_defaults(
    query_engine_tools=query_engine_tools,
    service_context=service_context,
    use_async=True,
)
from llama_index.callbacks.schema import CBEventType, EventPayload

def print_trace_subquestion():
    # iterate through sub_question items captured in SUB_QUESTION event
    for i, (start_event, end_event) in enumerate(
        llama_debug.get_event_pairs(CBEventType.SUB_QUESTION)
    ):
        qa_pair = end_event.payload[EventPayload.SUB_QUESTION]
        print("Sub Question " + str(i) + ": " + qa_pair.sub_q.sub_question.strip())
        print("Answer: " + qa_pair.answer.strip())
        print("====================================")


while True:
    question = input("ask?\n")
    response = query_engine.query(question)
    print(response)
    print_trace_subquestion()
