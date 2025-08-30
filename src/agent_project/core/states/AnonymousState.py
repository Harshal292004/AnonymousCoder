from typing import List, Literal

from langchain_core.messages import BaseMessage
from pydantic import BaseModel


class AnonymousState(BaseModel):
    query:str
    messages: List[BaseMessage]
    type: Literal["execution_node","scaffolding_node"]