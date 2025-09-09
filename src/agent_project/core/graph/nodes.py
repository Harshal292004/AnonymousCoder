from typing import List, Literal

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage,AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel

from ..prompts.system_prompt import (
    get_context_injection_prompt,
    get_execution_prompt,
    get_memory_prompt,
    get_summarization_prompt,
    get_understanding_prompt,
    get_scaffolding_prompt
)
from ..states.AnonymousState import AnonymousState
from ..tools import FILE_SYS_TOOLS,ask_user_tool,get_current_directory,get_framework_context
from ..tools.vector_database_tools import VECTOR_STORE_TOOLS, similarity_search


class TypeOutput(BaseModel):
    """Type of query"""

    type_of_query: Literal["execution_node", "scaffolding_node", "scaffolding_node"]


def get_memory_node(llm: BaseChatModel):
    def memory_node(state: AnonymousState):

        # get the current user query
        query: str = state.query
        MEMORY_SYSTEM_PROMPT: str = get_memory_prompt()
        CONTEXT_INJEXT_PROMPT: str = get_context_injection_prompt()

        agent = create_react_agent(
            model=llm, tools=VECTOR_STORE_TOOLS, prompt=MEMORY_SYSTEM_PROMPT
        )

        output = agent.invoke({"messages": [HumanMessage(content=query)]})

        agent = create_react_agent(
            model=llm, tools=[similarity_search], prompt=CONTEXT_INJEXT_PROMPT
        )

        output = agent.invoke({"messages": [HumanMessage(content=query)]})
        query += str(output.get("content"))

        return {
            "query": query,
            "messages": state.messages,
        }

    return memory_node


def get_summarization_node(llm: BaseChatModel):
    def summarization_node(state: AnonymousState):
        messages = state.messages
        SUMMARIZATION_PROMPT: str = get_summarization_prompt()

        if len(messages) >= 4 and isinstance(messages[3], SystemMessage):
            # discard very old summaries
            del messages[1:3]
        elif len(messages) >= 8:
            # create summaries
            messages_to_summarize: List[BaseMessage] = [
                SystemMessage(content=SUMMARIZATION_PROMPT)
            ] + messages[1:9]
            result = llm.invoke(messages_to_summarize)
            messages[1:9] = [SystemMessage(content=result.content)]

        return {"messages": messages}

    return summarization_node


def get_understanding_node(llm: BaseChatModel):
    def understanding_node(state: AnonymousState):
        query = state.query
        UNDERSTANDING_SYSTEM_PROMPT: str = get_understanding_prompt()
        messages = ChatPromptTemplate(
            state.messages
            + [
                SystemMessage(content=UNDERSTANDING_SYSTEM_PROMPT),
                HumanMessage(content=query),
            ]
        )
        understanding_chain = messages | llm.with_structured_output(schema=TypeOutput)
        result = understanding_chain.invoke({})
        return {
            "type": result.type_of_query,
        }

    return understanding_node


def get_execution_node(llm: BaseChatModel):
    def execution_node(state: AnonymousState):
        query = state.query
        EXECUTION_SYSTEM_PROMPT: str = get_execution_prompt()

        agent = create_react_agent(
            model=llm,
            tools=FILE_SYS_TOOLS,
        )
        messages = state.messages + [
            SystemMessage(content=EXECUTION_SYSTEM_PROMPT),
            HumanMessage(content=query),
        ]

        output = agent.invoke(messages)

        output = output.get("messages")
        if isinstance(output[-1], AIMessage):
            return {"messages": messages + []}
        else:
            return {"messages": messages + []}

    return execution_node


class Framework(BaseModel):
    framework:Literal['NONE']
def get_scaffolding_node(llm: BaseChatModel):
    def scaffolding_node(state: AnonymousState):
        # take the current user prompt out
        query=state.query
        # current state of messages  must be System,Human,AI,Human,AI.....
        messages=state.messages
        # Or  enchance the prompt with undestanding the needs
        # you need to uderstand what the user exactly wants
        PLAN_SYSTEM_PROMPT:str=get_plan_system_prompt()
        
        # provided the ask user tool as you need to understand and plan accordin 
        agent=create_react_agent(model=llm,tools=[ask_user_tool,get_framework_context])
        output=agent.invoke({"messages":messages+[SystemMessage(content=PLAN_SYSTEM_PROMPT),HumanMessage(content=query)]})
        # assuming the llm provides us with the plan to proceed
        # now append the plan with the SCAFOLDING PROMPT AND  THE new message with the injected steps if present
        AI_PROMPT:AIMessage=output.get("messages")[-1]
        SCAFOLDING_SYSTEM_PROMPT:SystemMessage= SystemMessage(content=get_scaffolding_prompt())
        
        # framework injection
        messages.extend([SCAFOLDING_SYSTEM_PROMPT,HumanMessage(content=query),AI_PROMPT])
        # use this messages to prompt the llm    
        # add all tools
        agent=create_react_agent(model=llm,tools=[])
        output=agent.invoke({"messages":messages})
        updated_messages=output.get("messages")
        # append the latest ai_message to the messages in the state
        state.messages.extend([HumanMessage(content=query),updated_messages[-1]])
        return
    return scaffolding_node