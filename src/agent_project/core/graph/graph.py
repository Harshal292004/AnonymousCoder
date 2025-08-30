from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from ..states.AnonymousState import AnonymousState
from .edges import route_edge
from .nodes import (get_execution_node, get_memory_node, get_scaffolding_node,
                    get_understanding_node)


def create_graph(llm: BaseChatModel):
    builder = StateGraph(AnonymousState)
    memory_node = get_memory_node(llm=llm)
    understanding_node=get_understanding_node(llm=llm)
    execution_node=get_execution_node(llm=llm)
    scaffolding_node=get_scaffolding_node(llm=llm)
    
    builder.add_edge(START, "memory_node")
    builder.add_node("memory_node", memory_node)
    builder.add_node("understand_query_node",understanding_node)
    builder.add_node("execution_node",execution_node)
    builder.add_node("scaffolding_node",scaffolding_node)
    
    builder.add_edge(START,"memory_node")
    builder.add_edge("memory_node","understanding_node")
    builder.add_conditional_edges("understanding_node",route_edge)
      
    checkpointer = InMemorySaver()
    builder.add_edge("memory_node", END)
    code_graph = builder.compile(checkpointer=checkpointer)
    return code_graph