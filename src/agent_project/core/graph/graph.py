from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from ..states.AnonymousState import AnonymousState
from .nodes import get_memory_node


def create_graph(llm: BaseChatModel):
    builder = StateGraph(AnonymousState)
    memory_node = get_memory_node(llm=llm)
    builder.add_edge(START, "memory_node")
    builder.add_node("memory_node", memory_node)
    # builder.add_node("understand_query_node",understand_query_node)
    # builder.add_node("error_handler_node",error_handler_node)
    # builder.add_node("general_query_node",general_query_node)
    # builder.add_node("index_code_base",index_code_base_node)
    # builder.add_node("scaffold_project",scaffold_project_node)
    checkpointer = InMemorySaver()
    builder.add_edge("memory_node", END)
    code_graph = builder.compile(checkpointer=checkpointer)
    return code_graph