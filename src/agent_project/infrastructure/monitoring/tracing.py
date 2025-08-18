from langfuse.langchain import CallbackHandler

def get_langfuse_handler(LANGFUSE_PUBLIC_KEY):
    langfuse_handler = CallbackHandler(
    public_key=LANGFUSE_PUBLIC_KEY
    )
    
    return langfuse_handler

