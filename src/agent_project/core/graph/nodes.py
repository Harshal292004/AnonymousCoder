from ..states.AnonymousState import AnonymousState
from prompts.system_prompt import get_system_prompt
from infrastructure.llm_clients.llms import GroqLLM,LLMConfig
from langchain_core.language_models import BaseChatModel
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from prompts.system_prompt import 
def get_memory_node(embeddings_llm:HuggingFaceEmbeddings,llm:BaseChatModel):
    def memory_node(state:AnonymousState):
        query=state.messages[-1]
        llm_with_tools=llm.bind_tools([])
        
        memory_ananlysis_chain=
        
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