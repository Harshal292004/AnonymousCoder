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

from langchain_core.messages import (AIMessage, BaseMessage, HumanMessage,
                                     SystemMessage)
from typing_extensions import List

msgs:List[BaseMessage]=[HumanMessage(content="sjongklsdg")]


print(msgs)


print(msgs+[HumanMessage("ksnjkdsbgs")])



