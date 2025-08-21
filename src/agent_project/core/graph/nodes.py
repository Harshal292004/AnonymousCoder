from ..states.AnonymousState import AnonymousState
from prompts.system_prompt import get_system_prompt
from infrastructure.llm_clients.llms import GroqLLM,LLMConfig
from langchain_core.language_models import BaseChatModel
def get_memory_node(llm:BaseChatModel):
    def memory_node(state:AnonymousState):
        query=state.messages[-1]
        llm.invoke([query])
        
        pass

    return memory_node

def understand_query_node(state:AnonymousState):
    
    pass

def general_query_node(state:AnonymousState):
    pass

def error_handler_node(state:AnonymousState):
    pass

def index_code_base_node(state:AnonymousState):
    pass

def scaffold_project_node(state:AnonymousState):
    pass