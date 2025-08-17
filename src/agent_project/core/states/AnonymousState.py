from pydantic import BaseModel
from langchain_core.messages import BaseMessage 
from typing import List ,Optional

class AnonymousState(BaseModel):
    messages: List[BaseMessage]
    error:Optional[Exception]
    error_count: Optional[int] 