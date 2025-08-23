from pydantic import BaseModel,Field

class AppSettings(BaseModel):
    """Complete configuration settings for the app to run

    Args:
        BaseModel (_type_): _description_
    """
    LANGFUSE_PUBLIC_KEY:str
    VECTOR_DB_FILE:str
    EMBEDDINGS_MODEL_NAME:str
    DEVICE:str
    GROQ_API_KEY:str
    
    def __init__(self,GROQ_API_KEY:str,LANGFUSE_PUBLIC_KEY:str,LANGFUSE_SECRET_KEY:str,LANGFUSE_HOST:str,VECTOR_DB_FILE:str=Field(default="user_space/memories.db"),EMBEDDINGS_MODEL_NAME:str= Field(default="sentence-transformers/all-mpnet-base-v2"),DEVICE:str=Field(default="cpu")):
        self.LANGFUSE_PUBLIC_KEY=LANGFUSE_PUBLIC_KEY
        self.LANGFUSE_SECRET_KEY=LANGFUSE_SECRET_KEY
        self.LANGFUSE_HOST=LANGFUSE_HOST 
        self.VECTOR_DB_FILE=VECTOR_DB_FILE
        self.EMBEDDINGS_MODEL_NAME=EMBEDDINGS_MODEL_NAME
        self.GROQ_API_KEY=GROQ_API_KEY
        self.DEVICE=DEVICE