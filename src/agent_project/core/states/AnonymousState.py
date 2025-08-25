from typing import List

from langchain_core.messages import BaseMessage
from pydantic import BaseModel


class AnonymousState(BaseModel):
    messages: List[BaseMessage]