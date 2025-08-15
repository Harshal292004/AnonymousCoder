from typing import List, Optional, Dict, Any
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import SQLiteVec
from sqlite_vec import Connection
from langchain.schema import Document


class VectorStoreManager:
    """Simple vector store management using SQLiteVec."""
    
    def __init__(
        self,
        db_file: str = "vector_store.db",
        table_name: str = "embeddings",
        embedding_model: Optional[OpenAIEmbeddings] = None
    ):
        """
        Initialize the vector store manager.
        
        Args:
            db_file: Path to SQLite database file
            table_name: Name of the table to store embeddings
            embedding_model: Embedding model instance (defaults to OpenAI)
        """
        self.db_file = db_file
        self.table_name = table_name
        self.embedding_model = embedding_model or OpenAIEmbeddings()
        
        # Initialize the vector store
        self.vector_store = SQLiteVec(
            table=self.table_name,
            connection=Connection(
                database=f"sqlite:///{self.db_file}"
            ),
            embedding=self.embedding_model,
            db_file=self.db_file
        )
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the vector store."""
        self.vector_store.add_documents(documents)
    
    def add_texts(
        self, 
        texts: List[str], 
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """Add texts to the vector store."""
        self.vector_store.add_texts(texts, metadatas=metadatas)
    
    def similarity_search(
        self, 
        query: str, 
        k: int = 4
    ) -> List[Document]:
        """Search for similar documents."""
        return self.vector_store.similarity_search(query, k=k)
    
    def similarity_search_with_score(
        self, 
        query: str, 
        k: int = 4
    ) -> List[tuple[Document, float]]:
        """Search for similar documents with scores."""
        return self.vector_store.similarity_search_with_score(query, k=k)
    
    def similarity_search_by_vector(
        self, 
        embedding: List[float], 
        k: int = 4
    ) -> List[Document]:
        """Search for similar documents by vector."""
        return self.vector_store.similarity_search_by_vector(embedding, k=k)
    
    def delete(self, ids: List[str]) -> None:
        """Delete documents by IDs."""
        self.vector_store.delete(ids)
    
    def get_vector_store(self):
        """Get the underlying vector store instance for LangGraph compatibility."""
        return self.vector_store