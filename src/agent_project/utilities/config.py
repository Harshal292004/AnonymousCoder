from pydantic import BaseModel

class AppSettings(BaseModel):
    LANGFUSE_PUBLIC_KEY:str
    def __init__(self):
        pass

settings=AppSettings(
    
)