from ..states.AnonymousState import AnonymousState
from prompts.system_prompt import get_system_prompt
from infrastructure.llm_clients.llms import GroqLLM,LLMConfig

def get_memory_node():
        
def memory_node(state:AnonymousState):
    query=state.messages[-1]
    GroqLLM().create_llm(config=LLMConfig(provider="groq"))
    
    
    pass

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