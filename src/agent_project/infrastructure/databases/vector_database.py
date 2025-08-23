import sqlite3
from typing import Optional
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

# Global configuration - shared across all tools
class VectorStoreConfig:
    """Shared configuration for vector store tools."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.db_file = "vector_store.db"
            self.table_name = "embeddings"
            self.embedding_model = None
            self.embedding_dim = None
            self._initialized = True
    
    def initialize(self, db_file: str, embedding_model: HuggingFaceEmbeddings):
        """Initialize the shared configuration."""
        self.db_file = db_file
        self.embedding_model = embedding_model
        self.embedding_dim = None
        self._init_database()
    
    def _get_embedding_dimension(self) -> int:
        """Get the embedding dimension from the model."""
        if self.embedding_dim is None:
            sample_text = "sample"
            sample_embedding = self.embedding_model.embed_query(sample_text)
            self.embedding_dim = len(sample_embedding)
        return self.embedding_dim
    
    def _init_database(self) -> None:
        """Initialize the database and create the vector table."""
        embedding_dim = self._get_embedding_dimension()
        
        with sqlite3.connect(self.db_file) as conn:
            conn.enable_load_extension(True)
            conn.load_extension("vec0")  
            
            conn.execute(f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS {self.table_name} USING vec0(
                    id TEXT PRIMARY KEY,
                    text TEXT,
                    embedding float[{embedding_dim}]
                )
            """)
            
            conn.commit()


# Convenience function to initialize the vector store
def initialize_vector_store(db_file: str = "vector_store.db", embedding_model: Optional[HuggingFaceEmbeddings] = None):
    """Initialize the vector store with shared configuration."""
    if embedding_model is None:
        embedding_model = HuggingFaceEmbeddings()
    
    config = VectorStoreConfig()
    config.initialize(db_file, embedding_model)
    
def _get_config() -> VectorStoreConfig:
    """Get the global configuration instance."""
    return VectorStoreConfig()


