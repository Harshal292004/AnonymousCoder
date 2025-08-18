from langgraph.graph import StateGraph
from langgraph.graph import MessagesState
from pydantic import BaseModel
from langchain_core.messages import BaseMessage 
from typing import List ,Optional,TypedDict

class AnonymousState(BaseModel):
    messages: List[BaseMessage]
    error_count: Optional[int] 
builder=StateGraph(AnonymousState)
