from typing import List, Literal

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel

from ..prompts.system_prompt import (get_context_injection_prompt,
                                     get_execution_prompt, get_memory_prompt,
                                     get_summarization_prompt,
                                     get_understanding_prompt)
from ..states.AnonymousState import AnonymousState
from ..tools import FILE_SYS_TOOLS
from ..tools.vector_database_tools import VECTOR_STORE_TOOLS, similarity_search


class TypeOutput(BaseModel):
    """Type of query
    """
    type_of_query:Literal['execution_node','scaffolding_node','scaffolding_node']

def get_memory_node(llm: BaseChatModel):
    def memory_node(state: AnonymousState):
        
        # get the current user query
        query:str=state.query
        MEMORY_SYSTEM_PROMPT:str=get_memory_prompt()
        CONTEXT_INJEXT_PROMPT:str=get_context_injection_prompt()
        
        agent=create_react_agent(
            model=llm,
            tools=VECTOR_STORE_TOOLS,
            prompt=MEMORY_SYSTEM_PROMPT
        )
        
        output=agent.invoke({"messages":[HumanMessage(content=query)]})
        
        
        agent=create_react_agent(
            model=llm,
            tools=[similarity_search],
            prompt=CONTEXT_INJEXT_PROMPT
        )    
        

        output=agent.invoke({"messages":[HumanMessage(content=query)]})
        query+=str(output.get("content"))
         
        return {
            "query":query,
            "messages": state.messages ,            
        }

    return memory_node

def get_summarization_node(llm:BaseChatModel):
    def summarization_node(state:AnonymousState):        
        messages=state.messages
        SUMMARIZATION_PROMPT:str=get_summarization_prompt()
        
        if(len(messages)>=4 and isinstance(messages[3],SystemMessage)):
            # discard very old summaries
            del messages[1:3]
        elif(len(messages) >=8):
            # create summaries
            messages_to_summarize:List[BaseMessage]=[SystemMessage(content=SUMMARIZATION_PROMPT)]+messages[1:9]
            result=llm.invoke(messages_to_summarize)
            messages[1:9]=[SystemMessage(content=result.content)]
                    
        return{
            "messages":messages
        }
    return summarization_node

def get_understanding_node(llm: BaseChatModel):
    def understanding_node(state: AnonymousState):
        query= state.query
        UNDERSTANDING_SYSTEM_PROMPT:str=get_understanding_prompt()
        messages=ChatPromptTemplate(state.messages+[SystemMessage(content=UNDERSTANDING_SYSTEM_PROMPT),HumanMessage(content=query)])
        understanding_chain= messages|llm.with_structured_output(schema=TypeOutput)
        result=understanding_chain.invoke({})
        return{
            "type":result.type_of_query,
        }
    return understanding_node


def get_execution_node(llm: BaseChatModel):
    def execution_node(state: AnonymousState):
        query=state.query
        EXECUTION_SYSTEM_PROMPT:str=get_execution_prompt()
        
        agent=create_react_agent(
            model=llm,
            tools=FILE_SYS_TOOLS,
        )
        messages=state.messages+[SystemMessage(content=EXECUTION_SYSTEM_PROMPT),HumanMessage(content=query)]
        
        
        agent.invoke(messages)
        
        
        return {
            
        }
    return execution_node

def get_scaffolding_node(llm: BaseChatModel):
    def scaffolding_node(state: AnonymousState):
        pass
    return scaffolding_node