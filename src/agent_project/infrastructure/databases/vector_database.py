import sqlite3
import uuid
from typing import Dict, List, Optional
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
        self.embedding_dim = None
        
        self._init_database()
    
    def _serialize_embedding(self, embedding: List[float]) -> bytes:
        """Convert embedding list to bytes for storage."""
        return np.array(embedding, dtype=np.float32).tobytes()
    
    def _deserialize_embedding(self, embedding_bytes: bytes) -> List[float]:
        """Convert bytes back to embedding list."""
        return np.frombuffer(embedding_bytes, dtype=np.float32).tolist()

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
            
            # Create single vector table with metadata
            conn.execute(f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS {self.table_name} USING vec0(
                    id TEXT PRIMARY KEY,
                    text TEXT,
                    embedding float[{embedding_dim}]
                )
            """)
            
            conn.commit()
    
    def _add_texts(self, texts: List[str]) -> List[str]:
        """
        Add texts to the vector store.
        
        Args:
            texts: List of texts to add
            
        Returns:
            List of IDs for the added texts
        """
        # Generate IDs if not provided
        ids = [str(uuid.uuid4()) for _ in texts]
        
        # Generate embeddings
        embeddings = self.embedding_model.embed_documents(texts)
        
        with sqlite3.connect(self.db_file) as conn:
            conn.enable_load_extension(True)
            conn.load_extension("vec0")
            
            for id_val, text, embedding in zip(ids, texts, embeddings):
                # Convert embedding to bytes for sqlite-vec
                embedding_bytes = self._serialize_embedding(embedding=embedding)   
                # Insert into vector table
                conn.execute(f"""
                    INSERT OR REPLACE INTO {self.table_name} 
                    (id, text, embedding) 
                    VALUES (?, ?, ?)
                """, (id_val, text, embedding_bytes))
            
            conn.commit()
        
        return ids
    
    @tool
    def add_texts(self, texts: List[str]) -> str:
        """
        Add texts to the vector store.
        
        Args:
            texts: List of texts to add
        Returns:
            Success or error message
        """
        try:
            ids = self._add_texts(texts)
            return f"Successfully added {len(texts)} texts. IDs: {', '.join(ids[:3])}{'...' if len(ids) > 3 else ''}"
        except Exception as e:
            return f"An error occurred: {e}"
        
    def _similarity_search(self, query: str, k: int = 4, threshold: float = 0.8) -> List[Dict[str, str]]:
        """
        Search for similar documents using sqlite-vec.
        
        Args:
            query: Query text
            k: Number of results to return
            threshold: Similarity threshold (cosine similarity)
            
        Returns:
            List of dictionaries with ID, TEXT, and SIMILARITY_SCORE
        """
        # Generate query embedding
        query_embedding = self.embedding_model.embed_query(query)
        query_embedding_bytes = self._serialize_embedding(query_embedding) 
        
        with sqlite3.connect(self.db_file) as conn:
            conn.enable_load_extension(True)
            conn.load_extension("vec0")
            
            # Use sqlite-vec's vector search capabilities
            cursor = conn.execute(f"""
                SELECT 
                    id,
                    text,
                    distance
                FROM {self.table_name}
                WHERE embedding MATCH ?
                ORDER BY distance ASC
                LIMIT ?
            """, (query_embedding_bytes, k))
            
            results: List[Dict[str, str]] = []
            for row in cursor.fetchall():
                id_val, text, distance = row
                # Convert distance to similarity (sqlite-vec uses L2 distance by default)
                # For cosine similarity, we need to use a different approach
                similarity = 1.0 - distance  # Rough approximation
                
                if similarity >= threshold:
                    results.append({
                        "ID": id_val,
                        "TEXT": text,
                        "SIMILARITY_SCORE": f"{similarity}"
                    })
            
            return results
    
    @tool
    def similarity_search(self, query: str, k: int = 4, threshold: float = 0.6) -> List[str]:
        """
        Search for similar documents.
        
        Args:
            query: Query text
            k: Number of results to return
            threshold: Similarity threshold
            
        Returns:
            List of string with format "ID: _ TEXT: _ SIMILARITY_SCORE: _"
        """
        docs = self._similarity_search(query=query, k=k, threshold=threshold)
        
        results: List[str] = []
        
        for d in docs:
            results.append(f"ID: {d.get('ID')} - TEXT: {d.get('TEXT')} - SIMILARITY_SCORE: {d.get('SIMILARITY_SCORE'):.4f}")
        
        return results
    
    def _delete_by_id(self, id: str) -> bool:
        """
        Delete a document by ID.
        
        Args:
            id: ID of the document to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        with sqlite3.connect(self.db_file) as conn:
            conn.enable_load_extension(True)
            conn.load_extension("vec0")
            
            cursor = conn.execute(f"DELETE FROM {self.table_name} WHERE id = ?", (id,))
            conn.commit()
            
            return cursor.rowcount > 0
    
    @tool
    def delete_by_ids(self, ids: List[str]) -> bool:
        """
        Delete documents by IDs.
        
        Args:
            ids: IDs of the documents to delete
            
        Returns:
            True if all deleted successfully, False otherwise
        """
        result = True
        
        for id_val in ids:
            result = result and self._delete_by_id(id_val)
            
        return result
    
    @tool
    def delete_by_query(self, query: str, k: int = 2, threshold: float = 0.8) -> List[str]:
        """
        Delete k documents that match a query above a certain threshold.
        
        Args:
            query: Query text to match against
            k: Number of documents to delete (max)
            threshold: Similarity threshold for deletion
            
        Returns:
            List of deleted IDs
        """
        # Find similar documents
        similar_docs = self._similarity_search(query, threshold=threshold, k=k)
        
        deleted_ids = []
        with sqlite3.connect(self.db_file) as conn:
            conn.enable_load_extension(True)
            conn.load_extension("vec0")
            
            for doc in similar_docs:
                cursor = conn.execute(f"DELETE FROM {self.table_name} WHERE id = ?", (doc.get("ID"),))
                if cursor.rowcount > 0:
                    deleted_ids.append(doc.get("ID"))
            
            conn.commit()
        
        return deleted_ids
    
    def _update_text(self, id_val: str, new_text: str) -> bool:
        """
        Update text for an existing ID.
        
        Args:
            id_val: ID of the document to update
            new_text: New text content
            
        Returns:
            True if updated successfully, False otherwise
        """
        # Generate new embedding
        new_embedding = self.embedding_model.embed_query(new_text)
        new_embedding_bytes = self._serialize_embedding(new_embedding)
        
        with sqlite3.connect(self.db_file) as conn:
            conn.enable_load_extension(True)
            conn.load_extension("vec0")
            
            cursor = conn.execute(f"""
                UPDATE {self.table_name} 
                SET text = ?, embedding = ? 
                WHERE id = ?
            """, (new_text, new_embedding_bytes, id_val))
            
            conn.commit()
            return cursor.rowcount > 0 
    
    @tool
    def update_texts(self, text_to_update: List[Dict[str, str]]) -> str:
        """
        Update text for existing IDs.
        
        Args:
            text_to_update: List of dictionaries with 'ID' and 'TEXT' keys
            e.g. [{"ID": "123", "TEXT": "new text content"}]
        
        Returns:
            Success message with count of updated documents
        """
        try:
            updated_count = 0
            failed_ids = []
            
            for update_item in text_to_update:
                if isinstance(update_item, dict):
                    id_val = update_item.get('ID')
                    text = update_item.get('TEXT')
                    
                    if id_val and text:
                        if self._update_text(id_val, text):
                            updated_count += 1
                        else:
                            failed_ids.append(id_val)
                    else:
                        failed_ids.append(str(update_item))
                else:
                    failed_ids.append(str(update_item))
            
            result_msg = f"Successfully updated {updated_count} documents."
            if failed_ids:
                result_msg += f" Failed to update: {', '.join(failed_ids[:3])}{'...' if len(failed_ids) > 3 else ''}"
            
            return result_msg
            
        except Exception as e:
            return f"An error occurred during update: {e}"
    
    @tool
    def get_all_documents(self) -> List[str]:
        """
        Get all documents in the vector store.
        
        Returns:
            List of strings with format "ID: _ TEXT: _"
        """
        with sqlite3.connect(self.db_file) as conn:
            conn.enable_load_extension(True)
            conn.load_extension("vec0")
            
            cursor = conn.execute(f"SELECT id, text FROM {self.table_name}")
            
            return [f"ID: {row[0]} - TEXT: {row[1]}" for row in cursor.fetchall()]
    
    @tool
    def get_document_count(self) -> int:
        """
        Get the total number of documents in the vector store.
        
        Returns:
            Number of documents
        """
        with sqlite3.connect(self.db_file) as conn:
            conn.enable_load_extension(True)
            conn.load_extension("vec0")
            
            cursor = conn.execute(f"SELECT COUNT(*) FROM {self.table_name}")
            return cursor.fetchone()[0]
    
    @tool
    def clear_all_documents(self) -> bool:
        """
        Clear all documents from the vector store.
        
        Returns:
            True if successful
        """
        try:
            with sqlite3.connect(self.db_file) as conn:
                conn.enable_load_extension(True)
                conn.load_extension("vec0")
                
                conn.execute(f"DELETE FROM {self.table_name}")
                conn.commit()
                
                return True
        except Exception:
            return False
        
        
if __name__ == "__main__":
    model_name = "sentence-transformers/all-mpnet-base-v2"
    model_kwargs = {"device": "cpu"}

    store = VectorStoreManager(
        db_file="user_space/trail.db",
        embedding_model=HuggingFaceEmbeddings(model_name=model_name, model_kwargs=model_kwargs)
    )

    # Add some texts
    print("\n=== Adding Texts ===")
    result = store.add_texts.invoke({'texts': ["Hello world", "Vector databases are powerful", "LangChain with sqlite-vec"]})
    print(result)

    # # Get all documents
    # print("\n=== All Documents ===")
    # docs = store.get_all_documents.invoke({})
    # for d in docs:
    #     print(d)

    # # Similarity search
    # print("\n=== Similarity Search ===")
    # sims = store.similarity_search.invoke({"query": "What is a vector database?", "k": 2, "threshold": 0.6})
    # for s in sims:
    #     print(s)

    # # Update a document (replace ID with one from `get_all_documents`)
    # if docs:
    #     first_id = docs[0].split(" - ")[0].split(": ")[1]
    #     print("\n=== Updating Document ===")
    #     update_result = store.update_texts.invoke({
    #         "text_to_update": [{"ID": first_id, "TEXT": "Updated content for first document"}]
    #     })
    #     print(update_result)

    # # Count documents
    # print("\n=== Document Count ===")
    # count = store.get_document_count.invoke({})
    # print(f"Total documents: {count}")

    # # Delete by query
    # print("\n=== Delete by Query ===")
    # deleted_ids = store.delete_by_query.invoke({"query": "LangChain", "k": 1, "threshold": 0.6})
    # print("Deleted IDs:", deleted_ids)

    # # Final docs
    # print("\n=== Final Documents ===")
    # final_docs = store.get_all_documents.invoke({})
    # for d in final_docs:
    #     print(d)

    # # Get all documents
    # print("\n=== All Documents ===")
    # docs = store.get_all_documents.invoke({})
    # for d in docs:
    #     print(d)

    # # Similarity search
    # print("\n=== Similarity Search ===")
    # sims = store.similarity_search.invoke({"query": "What is a vector database?", "k": 2, "threshold": 0.6})
    # for s in sims:
    #     print(s)

    # # Update a document (replace ID with one from `get_all_documents`)
    # if docs:
    #     first_id = docs[0].split(" - ")[0].split(": ")[1]
    #     print("\n=== Updating Document ===")
    #     update_result = store.update_texts.invoke({
    #         "text_to_update": [{"ID": first_id, "TEXT": "Updated content for first document"}]
    #     })
    #     print(update_result)

    # # Count documents
    # print("\n=== Document Count ===")
    # count = store.get_document_count.invoke({})
    # print(f"Total documents: {count}")

    # # Delete by query
    # print("\n=== Delete by Query ===")
    # deleted_ids = store.delete_by_query.invoke({"query": "LangChain", "k": 1, "threshold": 0.6})
    # print("Deleted IDs:", deleted_ids)

    # # Final docs
    # print("\n=== Final Documents ===")
    # final_docs = store.get_all_documents.invoke({})
    # for d in final_docs:
    #     print(d)
