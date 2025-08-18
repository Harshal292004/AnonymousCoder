from pydantic import BaseModel
from ..utilities.config import AppSettings
class Application(BaseModel):
    
    def __init__(self,settings:AppSettings):
        self.settings=settings
        pass
    
    def invoke(self):
        pass
    
    
    def _chat(self):
        pass 
    