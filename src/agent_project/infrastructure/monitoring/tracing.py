from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

def get_langfuse_handler(LANGFUSE_SECRET_KEY:str,LANGFUSE_HOST:str,LANGFUSE_PUBLIC_KEY:str):    
    Langfuse(
        public_key=LANGFUSE_PUBLIC_KEY,
        secret_key=LANGFUSE_SECRET_KEY,
        host=LANGFUSE_HOST
    )
    langfuse_handler = CallbackHandler()
    return langfuse_handler
