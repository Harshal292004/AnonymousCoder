from typing import List

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from ..prompts.system_prompt import get_memory_prompt
from ..states.AnonymousState import AnonymousState
from ..tools.vector_data_base_tools import VECTOR_STORE_TOOLS


def get_memory_node(llm: BaseChatModel):
    def memory_node(state: AnonymousState):
        query = ""
        for msg in reversed(state.messages):
            if isinstance(msg, HumanMessage):
                query = msg.content
                break
            
        memory_prompt = get_memory_prompt()
        prompts: List[BaseMessage] = [SystemMessage(content=memory_prompt), HumanMessage(content=query)]
            
        agent = create_react_agent(
            model=llm,
            tools=VECTOR_STORE_TOOLS
        )
        output = agent.invoke({"messages": prompts})
        print(output)
        
        # Return the state with the original messages
        return {
            "messages": state.messages,            
        }
    return memory_node


def understand_query_node(state: AnonymousState):
    pass


def general_query_node(state: AnonymousState):
    pass


def error_handler_node(state: AnonymousState):
    pass


def index_code_base_node(state: AnonymousState):
    pass


def scaffold_project_node(state: AnonymousState):
    pass