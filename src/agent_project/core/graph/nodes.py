from typing import List

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (AIMessage, BaseMessage, HumanMessage,
                                     SystemMessage)
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent

from ..prompts.system_prompt import (get_execution_prompt, get_memory_prompt,
                                     get_plan_prompt, get_scaffolding_prompt,
                                     get_summarization_prompt,
                                     get_understanding_prompt)
from ..states.AppStates import AppState, TypeOutput
from ..tools import (FILE_SYS_TOOLS, MEMORY_TOOLS, POWERSHELL_TOOLS,
                     SHELL_TOOLS, ask_user_tool, get_framework_context)


def get_memory_node(llm: BaseChatModel):
    def memory_node(state: AppState):
        # get the current user query
        query: str = state.query
        MEMORY_SYSTEM_PROMPT: str = get_memory_prompt()
    
        agent = create_react_agent(
            model=llm, tools=MEMORY_TOOLS, prompt=MEMORY_SYSTEM_PROMPT
        )

        output = agent.invoke({"messages": [HumanMessage(content=query)]})
        print(output.get("content"))
        return {
            "query": query,
            "messages": state.messages,
        }
    return memory_node


def get_summarization_node(llm: BaseChatModel):
    def summarization_node(state: AppState):
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
    def understanding_node(state: AppState):
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
            "type": result.type,
        }

    return understanding_node


def get_execution_node(llm: BaseChatModel):
    def execution_node(state: AppState):
        query = state.query
        EXECUTION_SYSTEM_PROMPT: str = get_execution_prompt()
        
        agent = create_react_agent(
            model=llm,
            tools=FILE_SYS_TOOLS + SHELL_TOOLS + POWERSHELL_TOOLS + MEMORY_TOOLS,
        )
        messages = state.messages + [
            SystemMessage(content=EXECUTION_SYSTEM_PROMPT),
            HumanMessage(content=query),
        ]
        
        output=agent.invoke({'messages':messages})

        result:List[BaseMessage] = output.get("messages",[])
        if isinstance(result[-1], AIMessage):
            return {"messages": state.messages + [HumanMessage(content=query),result[-1]]}
        else:
            return {"messages": messages+[HumanMessage(content=query)]}

    return execution_node

def get_scaffolding_node(llm: BaseChatModel):
    def scaffolding_node(state: AppState):
        # take the current user prompt out
        query=state.query
        # current state of messages  must be System,Human,AI,Human,AI.....
        messages=state.messages
        # Or  enchance the prompt with undestanding the needs
        # you need to uderstand what the user exactly wants
        PLAN_SYSTEM_PROMPT:str=get_plan_prompt()
        agent=create_react_agent(model=llm,tools=[ask_user_tool,get_framework_context])
        output=agent.invoke({"messages":messages+[SystemMessage(content=PLAN_SYSTEM_PROMPT),HumanMessage(content=query)]})
        # assuming the llm provides us with the plan to proceed
        # now append the plan with the SCAFOLDING PROMPT AND  THE new message with the injected steps if present
        AI_MESSAGE:AIMessage=output.get("messages")[-1]
        SCAFOLDING_SYSTEM_PROMPT:SystemMessage= SystemMessage(content=get_scaffolding_prompt())
        
        # framework injection
        messages.extend([SCAFOLDING_SYSTEM_PROMPT,HumanMessage(content=query),AI_MESSAGE])
        # use this messages to prompt the llm    
        # add all tools
        agent=create_react_agent(model=llm,tools=FILE_SYS_TOOLS+SHELL_TOOLS+POWERSHELL_TOOLS)
        output=agent.invoke({"messages":messages})
        updated_messages:List[BaseMessage]=output.get("messages")
        # append the latest ai_message to the messages in the state
        return {
            "messages":state.messages+[HumanMessage(content=query),updated_messages[-1]]
        }
    return scaffolding_node