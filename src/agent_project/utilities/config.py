from pydantic import BaseModel,Field

class AppSettings(BaseModel):
    LANGFUSE_PUBLIC_KEY:str
    VECTOR_DB_FILE:str
    EMBEDDINGS_MODEL_NAME:str
    DEVICE:str
    
    def __init__(self,LANGFUSE_PUBLIC_KEY:str="",VECTOR_DB_FILE:str=Field(default="user_space/memories.db"),EMBEDDINGS_MODEL_NAME:str= Field(default="sentence-transformers/all-mpnet-base-v2"),DEVICE:str=Field(default="cpu")):
        self.LANGFUSE_PUBLIC_KEY=LANGFUSE_PUBLIC_KEY 
        self.VECTOR_DB_FILE=VECTOR_DB_FILE
        self.EMBEDDINGS_MODEL_NAME=EMBEDDINGS_MODEL_NAME