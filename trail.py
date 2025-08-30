# from langgraph.graph import StateGraph, START, END
# from langgraph.checkpoint.memory import InMemorySaver
# from typing import Annotated
# from typing_extensions import TypedDict
# from operator import add
# from pprint import pprint
# class State(TypedDict):
#     foo: str
#     bar: list[str]

# def node_a(state: State):
#     return {"foo": "a", "bar": ["a"]}

# def node_b(state: State):
#     return {"foo": "b", "bar": ["b"]}


# workflow = StateGraph(State)
# workflow.add_node(node_a)
# workflow.add_node(node_b)
# workflow.add_edge(START, "node_a")
# workflow.add_edge("node_a", "node_b")
# workflow.add_edge("node_b", END)

# checkpointer = InMemorySaver()
# graph = workflow.compile(checkpointer=checkpointer)

# config = {"configurable": {"thread_id": "1"}}
# # graph.invoke({"foo": ""}, config)


# config = {"configurable": {"thread_id": "1"}}
# pprint(graph.get_state(config))

import logging

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_groq import ChatGroq
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langgraph.prebuilt import create_react_agent
from pydantic import SecretStr
from typing_extensions import List

from src.agent_project.core.prompts.system_prompt import (
    get_context_injection_prompt, get_memory_prompt)
from src.agent_project.core.tools.vector_data_base_tools import \
    VECTOR_STORE_TOOLS
from src.agent_project.infrastructure.databases.vector_database import \
    initialize_vector_store

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def func():
    query: str = "I like functional programs more , please change the object orientation to functional code for better readiability"
    MEMORY_SYSTEM_PROMPT: str = get_memory_prompt()

    messages: List[BaseMessage] = [HumanMessage(content=query)]
    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        api_key=SecretStr("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")
    )
    agent = create_react_agent(
        model=llm,
        tools=VECTOR_STORE_TOOLS,
        prompt=MEMORY_SYSTEM_PROMPT
    )

    output = ""
    logger.info("Starting agent stream...")

    for chunk in agent.stream({"messages": messages}):
        logger.debug(f"Chunk received: {chunk}")
        logger.debug(f"CHunk type: {type(chunk)}")
        output += str(chunk)

    logger.info("Agent stream finished")
    logger.info("Final Output Data: %s", output)
    logger.info("Final Output Type: %s", type(output))

def func_inject_info():
    query="Write a python code to fix the bugs in the current process, its quite an object oriented code ,huhh!"
    context_injection_prompt=get_context_injection_prompt()
    
if __name__ == "__main__":
    EMBEDDINGS_MODEL_NAME="sentence-transformers/all-mpnet-base-v2"
    VECTOR_DB_FILE="user_space/trail.db"
    DEVICE="cpu"
    embedding_model = HuggingFaceEmbeddings(
        model_name=EMBEDDINGS_MODEL_NAME, 
        model_kwargs={"device": DEVICE}
    )
    initialize_vector_store(db_file=VECTOR_DB_FILE, embedding_model=embedding_model)
    func()
   
           


