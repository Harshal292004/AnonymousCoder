from typing import List

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from ..prompts.system_prompt import (get_context_injection_prompt,
                                     get_memory_prompt)
from ..states.AnonymousState import AnonymousState
from ..tools.vector_database_tools import VECTOR_STORE_TOOLS


def get_memory_node(llm: BaseChatModel):
    def memory_node(state: AnonymousState):
        
        # get the current user query
        query:str=state.query
        MEMORY_SYSTEM_PROMPT:str=get_memory_prompt()
        
        messages:List[BaseMessage]=[HumanMessage(content=query)]
        
        agent=create_react_agent(
            model=llm,
            tools=VECTOR_STORE_TOOLS,
            prompt=MEMORY_SYSTEM_PROMPT
        )
        
        output=  ""
        for chunk,metadata in agent.stream(
            {"messages":messages}
        ):
            print(chunk)
            output+=chunk.content
            
            
        
        
        
        
        
        
        
        
        




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


def get_understanding_node(llm: BaseChatModel):
    def understanding_node(state: AnonymousState):
        query=
        
    return understanding_node


def get_execution_node(llm: BaseChatModel):
    def execution_node(state: AnonymousState):
        query = ""
        for msg in reversed(state.messages):
            if isinstance(msg, HumanMessage):
                query = msg.content
                break
    return execution_node

def get_scaffolding_node(llm: BaseChatModel):
    def scaffolding_node(state: AnonymousState):
        pass
    return scaffolding_node