from pydantic import BaseModel,Field

class AppSettings(BaseModel):
    LANGFUSE_PUBLIC_KEY:str
    VECTOR_DB_FILE: str=Field(default="user_space/memories.db")
    EMBEDDINGS_MODEL_NAME:str= Field(default="sentence-transformers/all-mpnet-base-v2")
    DEVICE:str=Field(default="cpu")
    
    def __init__(self):
        pass