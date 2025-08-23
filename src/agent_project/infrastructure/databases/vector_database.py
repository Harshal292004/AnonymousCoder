import sqlite3
import uuid
from typing import Dict, List, Optional
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_core.tools import tool
import numpy as np

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

# Utility functions
def _serialize_embedding(embedding: List[float]) -> bytes:
    """Convert embedding list to bytes for storage."""
    return np.array(embedding, dtype=np.float32).tobytes()

def _deserialize_embedding(embedding_bytes: bytes) -> List[float]:
    """Convert bytes back to embedding list."""
    return np.frombuffer(embedding_bytes, dtype=np.float32).tolist()

def _get_config() -> VectorStoreConfig:
    """Get the global configuration instance."""
    return VectorStoreConfig()

# Standalone tool functions
@tool
def add_texts(texts: List[str]) -> str:
    """
    Add texts to the vector store.
    
    Args:
        texts: List of texts to add
    Returns:
        Success or error message
    """
    try:
        config = _get_config()
        
        # Generate IDs
        ids = [str(uuid.uuid4()) for _ in texts]
        
        # Generate embeddings
        embeddings = config.embedding_model.embed_documents(texts)
        
        with sqlite3.connect(config.db_file) as conn:
            conn.enable_load_extension(True)
            conn.load_extension("vec0")
            
            for id_val, text, embedding in zip(ids, texts, embeddings):
                embedding_bytes = _serialize_embedding(embedding)   
                conn.execute(f"""
                    INSERT OR REPLACE INTO {config.table_name} 
                    (id, text, embedding) 
                    VALUES (?, ?, ?)
                """, (id_val, text, embedding_bytes))
            
            conn.commit()
        
        return f"Successfully added {len(texts)} texts. IDs: {', '.join(ids[:3])}{'...' if len(ids) > 3 else ''}"
    except Exception as e:
        return f"An error occurred: {e}"

@tool
def similarity_search(query: str, k: int = 4, threshold: float = 0.6) -> List[str]:
    """
    Search for similar documents.
    
    Args:
        query: Query text
        k: Number of results to return
        threshold: Similarity threshold
        
    Returns:
        List of strings with format "ID: _ TEXT: _ SIMILARITY_SCORE: _"
    """
    config = _get_config()
    
    # Generate query embedding
    query_embedding = config.embedding_model.embed_query(query)
    query_embedding_bytes = _serialize_embedding(query_embedding) 
    
    with sqlite3.connect(config.db_file) as conn:
        conn.enable_load_extension(True)
        conn.load_extension("vec0")
        
        cursor = conn.execute(f"""
            SELECT 
                id,
                text,
                distance
            FROM {config.table_name}
            WHERE embedding MATCH ?
            ORDER BY distance ASC
            LIMIT ?
        """, (query_embedding_bytes, k))
        
        results = []
        for row in cursor.fetchall():
            id_val, text, distance = row
            similarity = 1.0 - distance
            
            if similarity >= threshold:
                results.append(f"ID: {id_val} - TEXT: {text} - SIMILARITY_SCORE: {similarity:.4f}")
        
        return results

@tool
def delete_by_ids(ids: List[str]) -> bool:
    """
    Delete documents by IDs.
    
    Args:
        ids: IDs of the documents to delete
        
    Returns:
        True if all deleted successfully, False otherwise
    """
    config = _get_config()
    result = True
    
    with sqlite3.connect(config.db_file) as conn:
        conn.enable_load_extension(True)
        conn.load_extension("vec0")
        
        for id_val in ids:
            cursor = conn.execute(f"DELETE FROM {config.table_name} WHERE id = ?", (id_val,))
            result = result and cursor.rowcount > 0
        
        conn.commit()
    
    return result

@tool
def delete_by_query(query: str, k: int = 2, threshold: float = 0.8) -> List[str]:
    """
    Delete k documents that match a query above a certain threshold.
    
    Args:
        query: Query text to match against
        k: Number of documents to delete (max)
        threshold: Similarity threshold for deletion
        
    Returns:
        List of deleted IDs
    """
    config = _get_config()
    
    # First find similar documents
    query_embedding = config.embedding_model.embed_query(query)
    query_embedding_bytes = _serialize_embedding(query_embedding)
    
    with sqlite3.connect(config.db_file) as conn:
        conn.enable_load_extension(True)
        conn.load_extension("vec0")
        
        # Find similar documents
        cursor = conn.execute(f"""
            SELECT id, distance
            FROM {config.table_name}
            WHERE embedding MATCH ?
            ORDER BY distance ASC
            LIMIT ?
        """, (query_embedding_bytes, k))
        
        deleted_ids = []
        for row in cursor.fetchall():
            id_val, distance = row
            similarity = 1.0 - distance
            
            if similarity >= threshold:
                delete_cursor = conn.execute(f"DELETE FROM {config.table_name} WHERE id = ?", (id_val,))
                if delete_cursor.rowcount > 0:
                    deleted_ids.append(id_val)
        
        conn.commit()
    
    return deleted_ids

@tool
def update_texts(text_to_update: List[Dict[str, str]]) -> str:
    """
    Update text for existing IDs.
    
    Args:
        text_to_update: List of dictionaries with 'ID' and 'TEXT' keys
        e.g. [{"ID": "123", "TEXT": "new text content"}]
    
    Returns:
        Success message with count of updated documents
    """
    try:
        config = _get_config()
        updated_count = 0
        failed_ids = []
        
        with sqlite3.connect(config.db_file) as conn:
            conn.enable_load_extension(True)
            conn.load_extension("vec0")
            
            for update_item in text_to_update:
                if isinstance(update_item, dict):
                    id_val = update_item.get('ID')
                    text = update_item.get('TEXT')
                    
                    if id_val and text:
                        # Generate new embedding
                        new_embedding = config.embedding_model.embed_query(text)
                        new_embedding_bytes = _serialize_embedding(new_embedding)
                        
                        cursor = conn.execute(f"""
                            UPDATE {config.table_name} 
                            SET text = ?, embedding = ? 
                            WHERE id = ?
                        """, (text, new_embedding_bytes, id_val))
                        
                        if cursor.rowcount > 0:
                            updated_count += 1
                        else:
                            failed_ids.append(id_val)
                    else:
                        failed_ids.append(str(update_item))
                else:
                    failed_ids.append(str(update_item))
            
            conn.commit()
        
        result_msg = f"Successfully updated {updated_count} documents."
        if failed_ids:
            result_msg += f" Failed to update: {', '.join(failed_ids[:3])}{'...' if len(failed_ids) > 3 else ''}"
        
        return result_msg
        
    except Exception as e:
        return f"An error occurred during update: {e}"

@tool
def get_all_documents() -> List[str]:
    """
    Get all documents in the vector store.
    
    Returns:
        List of strings with format "ID: _ TEXT: _"
    """
    config = _get_config()
    
    with sqlite3.connect(config.db_file) as conn:
        conn.enable_load_extension(True)
        conn.load_extension("vec0")
        
        cursor = conn.execute(f"SELECT id, text FROM {config.table_name}")
        
        return [f"ID: {row[0]} - TEXT: {row[1]}" for row in cursor.fetchall()]

@tool
def get_document_count() -> int:
    """
    Get the total number of documents in the vector store.
    
    Returns:
        Number of documents
    """
    config = _get_config()
    
    with sqlite3.connect(config.db_file) as conn:
        conn.enable_load_extension(True)
        conn.load_extension("vec0")
        
        cursor = conn.execute(f"SELECT COUNT(*) FROM {config.table_name}")
        return cursor.fetchone()[0]

@tool
def clear_all_documents() -> bool:
    """
    Clear all documents from the vector store.
    
    Returns:
        True if successful
    """
    try:
        config = _get_config()
        
        with sqlite3.connect(config.db_file) as conn:
            conn.enable_load_extension(True)
            conn.load_extension("vec0")
            
            conn.execute(f"DELETE FROM {config.table_name}")
            conn.commit()
            
            return True
    except Exception:
        return False

# Convenience function to initialize the vector store
def initialize_vector_store(db_file: str = "vector_store.db", embedding_model: Optional[HuggingFaceEmbeddings] = None):
    """Initialize the vector store with shared configuration."""
    if embedding_model is None:
        embedding_model = HuggingFaceEmbeddings()
    
    config = VectorStoreConfig()
    config.initialize(db_file, embedding_model)

# List of all available tools for easy import
VECTOR_STORE_TOOLS = [
    add_texts,
    similarity_search,
    delete_by_ids,
    delete_by_query,
    update_texts,
    get_all_documents,
    get_document_count,
    clear_all_documents
]

if __name__ == "__main__":
    # Initialize the vector store
    model_name = "sentence-transformers/all-mpnet-base-v2"
    model_kwargs = {"device": "cpu"}
    
    initialize_vector_store(
        db_file="user_space/trail.db",
        embedding_model=HuggingFaceEmbeddings(model_name=model_name, model_kwargs=model_kwargs)
    )

    # Add some texts
    print("\n=== Adding Texts ===")
    result = add_texts.invoke({'texts': ["Hello world", "Vector databases are powerful", "LangChain with sqlite-vec"]})
    print(result)

    # Get all documents
    print("\n=== All Documents ===")
    docs = get_all_documents.invoke({})
    for d in docs:
        print(d)

    # Similarity search
    print("\n=== Similarity Search ===")
    sims = similarity_search.invoke({"query": "What is a vector database?", "k": 2, "threshold": 0.6})
    for s in sims:
        print(s)

    # Update a document (replace ID with one from `get_all_documents`)
    if docs:
        first_id = docs[0].split(" - ")[0].split(": ")[1]
        print("\n=== Updating Document ===")
        update_result = update_texts.invoke({
            "text_to_update": [{"ID": first_id, "TEXT": "Updated content for first document"}]
        })
        print(update_result)

    # Count documents
    print("\n=== Document Count ===")
    count = get_document_count.invoke({})
    print(f"Total documents: {count}")

    # Delete by query
    print("\n=== Delete by Query ===")
    deleted_ids = delete_by_query.invoke({"query": "LangChain", "k": 1, "threshold": 0.6})
    print("Deleted IDs:", deleted_ids)

    # Final docs
    print("\n=== Final Documents ===")
    final_docs = get_all_documents.invoke({})
    for d in final_docs:
        print(d)