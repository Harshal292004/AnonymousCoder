from pydantic import BaseModel
from langchain_core.messages import BaseMessage 
from typing import List 

class AnonymousState(BaseModel):
    messages: List[BaseMessage]