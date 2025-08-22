import sqlite3
import json
import uuid
from typing import List, Optional, Dict, Any, Tuple
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_core.tools import tool
import numpy as np

class VectorStoreManager:
    """Direct vector store management using sqlite-vec."""
    
    def __init__(
        self,
        db_file: str = "vector_store.db",
        table_name: str = "embeddings",
        embedding_model: Optional[HuggingFaceEmbeddings] = None
    ):
        """
        Initialize the vector store manager.
        
        Args:
            db_file: Path to SQLite database file
            table_name: Name of the table to store embeddings
            embedding_model: Embedding model instance
        """
        self.db_file = db_file
        self.table_name = table_name
        self.embedding_model = embedding_model or HuggingFaceEmbeddings()
        
        # Initialize database and create table
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize the database and create the embeddings table."""
        with sqlite3.connect(self.db_file) as conn:
            # Enable sqlite-vec extension
            conn.enable_load_extension(True)
            conn.load_extension("vec0")  # Load sqlite-vec extension
            
            # Get embedding dimension
            sample_text = "sample"
            sample_embedding = self.embedding_model.embed_query(sample_text)
            embedding_dim = len(sample_embedding)
            
            # Create table with vector column
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id TEXT PRIMARY KEY,
                    text TEXT NOT NULL,
                    metadata TEXT,
                    embedding BLOB
                )
            """)
            
            # Create vector index
            conn.execute(f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS {self.table_name}_vec USING vec0(
                    embedding float[{embedding_dim}]
                )
            """)
            
            conn.commit()
    
    def _serialize_embedding(self, embedding: List[float]) -> bytes:
        """Convert embedding list to bytes for storage."""
        return np.array(embedding, dtype=np.float32).tobytes()
    
    def _deserialize_embedding(self, embedding_bytes: bytes) -> List[float]:
        """Convert bytes back to embedding list."""
        return np.frombuffer(embedding_bytes, dtype=np.float32).tolist()
    
    
    def _add_texts(
        self,
        texts:List[str],
        metadatas: Optional[List[Dict[str,Any]]]=None,
    ):
        """
        Add texts to the vector store.
        
        Args:.
            texts: List of texts to add
            metadatas: Optional list of metadata dictionaries
            ids: Optional list of IDs (will generate UUIDs if not provided)
            
        Returns:
            List of document IDs
        """
        if not texts:
            return []
        
        # Generate IDs if not provided
        ids = [str(uuid.uuid4()) for _ in texts]
        
        # Ensure metadatas list matches texts length
        if metadatas is None:
            metadatas = [{}] * len(texts)
        elif len(metadatas) != len(texts):
            raise ValueError("Length of metadatas must match length of texts")
        
        # Generate embeddings
        embeddings = self.embedding_model.embed_documents(texts)
        
        with sqlite3.connect(self.db_file) as conn:
            conn.enable_load_extension(True)
            conn.load_extension("vec0")
            
            for i, (doc_id, text, metadata, embedding) in enumerate(zip(ids, texts, metadatas, embeddings)):
                # Store in main table
                conn.execute(f"""
                    INSERT OR REPLACE INTO {self.table_name} 
                    (id, text, metadata, embedding) 
                    VALUES (?, ?, ?, ?)
                """, (doc_id, text, json.dumps(metadata), self._serialize_embedding(embedding)))
                
                # Store in vector index
                conn.execute(f"""
                    INSERT OR REPLACE INTO {self.table_name}_vec 
                    (rowid, embedding) 
                    VALUES (?, vec_f32(?))
                """, (hash(doc_id) & 0x7FFFFFFF, embedding))  # Use hash of ID as rowid
            
            conn.commit()
        
    
    @tool
    def add_texts(
        self, 
        texts: List[str], 
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) :
       self._add_texts(texts,metadatas)
       
    
    # def similarity_search_function(
    #             self, 
    #     query: str, 
    #     k: int = 4,
    #     filter_metadata: Optional[Dict[str, Any]] = None
    # )-> List[Dict[str, Any]]:
    #       """
    #     Search for similar documents.
        
    #     Args:
    #         query: Query text
    #         k: Number of results to return
    #         filter_metadata: Optional metadata filter
            
    #     Returns:
    #         List of documents with similarity scores
    #     """
    #     # Generate query embedding
    #     query_embedding = self.embedding_model.embed_query(query)
        
    #     with sqlite3.connect(self.db_file) as conn:
    #         conn.enable_load_extension(True)
    #         conn.load_extension("vec0")
            
    #         # Build query with optional metadata filtering
    #         base_query = f"""
    #             SELECT 
    #                 e.id,
    #                 e.text,
    #                 e.metadata,
    #                 vec_distance_cosine(v.embedding, vec_f32(?)) as distance
    #             FROM {self.table_name} e
    #             JOIN {self.table_name}_vec v ON v.rowid = (? & 0x7FFFFFFF)
    #             WHERE v.embedding MATCH vec_f32(?)
    #         """
            
    #         params = [query_embedding]
            
    #         if filter_metadata:
    #             # Add metadata filtering
    #             conditions = []
    #             for key, value in filter_metadata.items():
    #                 conditions.append(f"json_extract(e.metadata, '$.{key}') = ?")
    #                 params.append(value)
                
    #             if conditions:
    #                 base_query += " AND " + " AND ".join(conditions)
            
    #         base_query += " ORDER BY distance ASC LIMIT ?"
    #         params.append(k)
            
    #         # Note: This is a simplified version. For proper vector search,
    #         # you'd use the vec0 virtual table's MATCH operator
    #         cursor = conn.execute(f"""
    #             SELECT 
    #                 e.id,
    #                 e.text,
    #                 e.metadata
    #             FROM {self.table_name} e
    #             ORDER BY RANDOM()
    #             LIMIT ?
    #         """, (k,))
            
    #         results = []
    #         for row in cursor.fetchall():
    #             doc_id, text, metadata_json = row
    #             metadata = json.loads(metadata_json) if metadata_json else {}
    #             results.append({
    #                 'id': doc_id,
    #                 'text': text,
    #                 'metadata': metadata,
    #                 'page_content': text  # For LangChain compatibility
    #             })
            
    #         return results
        
    # @tool
    # def similarity_search(
    #     self, 
    #     query: str, 
    #     k: int = 4,
    #     filter_metadata: Optional[Dict[str, Any]] = None
    # ) -> List[Dict[str, Any]]:
      
    
    # @tool
    # def delete_by_ids(self, ids: List[str]) -> int:
    #     """
    #     Delete documents by their IDs.
        
    #     Args:
    #         ids: List of document IDs to delete
            
    #     Returns:
    #         Number of documents deleted
    #     """
    #     if not ids:
    #         return 0
        
    #     with sqlite3.connect(self.db_file) as conn:
    #         conn.enable_load_extension(True)
    #         conn.load_extension("vec0")
            
    #         placeholders = ','.join(['?'] * len(ids))
            
    #         # Delete from main table
    #         cursor = conn.execute(f"""
    #             DELETE FROM {self.table_name} 
    #             WHERE id IN ({placeholders})
    #         """, ids)
            
    #         deleted_count = cursor.rowcount
            
    #         # Delete from vector index
    #         for doc_id in ids:
    #             conn.execute(f"""
    #                 DELETE FROM {self.table_name}_vec 
    #                 WHERE rowid = ?
    #             """, (hash(doc_id) & 0x7FFFFFFF,))
            
    #         conn.commit()
    #         return deleted_count
    
    # @tool
    # def delete_by_query(self, query: str, k: int = 4) -> int:
    #     """
    #     Delete documents similar to query.
        
    #     Args:
    #         query: Query text to find similar documents
    #         k: Number of similar documents to delete
            
    #     Returns:
    #         Number of documents deleted
    #     """
    #     # Find similar documents
    #     similar_docs = self.similarity_search(query, k)
        
    #     if not similar_docs:
    #         return 0
        
    #     # Extract IDs and delete
    #     ids_to_delete = [doc['id'] for doc in similar_docs]
    #     return self.delete_by_ids(ids_to_delete)
    
    # @tool
    # def update_document(
    #     self, 
    #     doc_id: str, 
    #     text: Optional[str] = None, 
    #     metadata: Optional[Dict[str, Any]] = None
    # ) -> bool:
    #     """
    #     Update a document's text and/or metadata.
        
    #     Args:
    #         doc_id: Document ID to update
    #         text: New text content (if provided)
    #         metadata: New metadata (if provided)
            
    #     Returns:
    #         True if document was updated, False if not found
    #     """
    #     with sqlite3.connect(self.db_file) as conn:
    #         conn.enable_load_extension(True)
    #         conn.load_extension("vec0")
            
    #         # Check if document exists
    #         cursor = conn.execute(f"""
    #             SELECT text, metadata FROM {self.table_name} WHERE id = ?
    #         """, (doc_id,))
            
    #         result = cursor.fetchone()
    #         if not result:
    #             return False
            
    #         current_text, current_metadata_json = result
    #         current_metadata = json.loads(current_metadata_json) if current_metadata_json else {}
            
    #         # Use current values if new ones not provided
    #         new_text = text if text is not None else current_text
    #         new_metadata = metadata if metadata is not None else current_metadata
            
    #         # Generate new embedding if text changed
    #         if text is not None:
    #             new_embedding = self.embedding_model.embed_query(new_text)
                
    #             # Update main table
    #             conn.execute(f"""
    #                 UPDATE {self.table_name} 
    #                 SET text = ?, metadata = ?, embedding = ?
    #                 WHERE id = ?
    #             """, (new_text, json.dumps(new_metadata), self._serialize_embedding(new_embedding), doc_id))
                
    #             # Update vector index
    #             conn.execute(f"""
    #                 UPDATE {self.table_name}_vec 
    #                 SET embedding = vec_f32(?)
    #                 WHERE rowid = ?
    #             """, (new_embedding, hash(doc_id) & 0x7FFFFFFF))
    #         else:
    #             # Only update metadata
    #             conn.execute(f"""
    #                 UPDATE {self.table_name} 
    #                 SET metadata = ?
    #                 WHERE id = ?
    #             """, (json.dumps(new_metadata), doc_id))
            
    #         conn.commit()
    #         return True
    
    # def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
    #     """
    #     Retrieve a document by its ID.
        
    #     Args:
    #         doc_id: Document ID
            
    #     Returns:
    #         Document dict or None if not found
    #     """
    #     with sqlite3.connect(self.db_file) as conn:
    #         cursor = conn.execute(f"""
    #             SELECT id, text, metadata FROM {self.table_name} WHERE id = ?
    #         """, (doc_id,))
            
    #         result = cursor.fetchone()
    #         if result:
    #             doc_id, text, metadata_json = result
    #             metadata = json.loads(metadata_json) if metadata_json else {}
    #             return {
    #                 'id': doc_id,
    #                 'text': text,
    #                 'metadata': metadata,
    #                 'page_content': text
    #             }
    #         return None
    
    # def list_all_documents(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    #     """
    #     List all documents in the store.
        
    #     Args:
    #         limit: Optional limit on number of documents
            
    #     Returns:
    #         List of all documents
    #     """
    #     with sqlite3.connect(self.db_file) as conn:
    #         query = f"SELECT id, text, metadata FROM {self.table_name}"
    #         params = []
            
    #         if limit:
    #             query += " LIMIT ?"
    #             params.append(limit)
            
    #         cursor = conn.execute(query, params)
            
    #         results = []
    #         for row in cursor.fetchall():
    #             doc_id, text, metadata_json = row
    #             metadata = json.loads(metadata_json) if metadata_json else {}
    #             results.append({
    #                 'id': doc_id,
    #                 'text': text,
    #                 'metadata': metadata,
    #                 'page_content': text
    #             })
            
    #         return results
    
    # def get_stats(self) -> Dict[str, Any]:
    #     """Get statistics about the vector store."""
    #     with sqlite3.connect(self.db_file) as conn:
    #         cursor = conn.execute(f"SELECT COUNT(*) FROM {self.table_name}")
    #         count = cursor.fetchone()[0]
            
    #         return {
    #             'total_documents': count,
    #             'table_name': self.table_name,
    #             'db_file': self.db_file
    #         }
    
    
if __name__=="__main__":
    model_kwargs = {"device": "cpu"}
    encode_kwargs = {"normalize_embeddings": False}
    store=VectorStoreManager(db_file="user_space/trail.db",embedding_model=HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2", model_kwargs=model_kwargs, encode_kwargs=encode_kwargs))