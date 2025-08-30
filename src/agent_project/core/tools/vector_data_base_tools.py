import sqlite3
from typing import List, Optional

from langchain.tools import tool

from ...infrastructure.databases.vector_database import _get_config


def _serialize_embedding(embedding: List[float]) -> bytes:
    """Serialize embedding list to bytes for storage."""
    import struct
    return struct.pack(f'<{len(embedding)}f', *embedding)


def _deserialize_embedding(embedding_bytes: bytes) -> List[float]:
    """Deserialize bytes back to embedding list."""
    import struct
    return list(struct.unpack(f'<{len(embedding_bytes)//4}f', embedding_bytes))


@tool
def add_texts(texts: List[str], ids: Optional[List[str]] = None) -> str:
    """
    Add texts to the vector store with optional IDs.
    
    Args:
        texts: List of text strings to add
        ids: Optional list of IDs for the texts
        
    Returns:
        Success message with count of added texts
    """
    try:
        config = _get_config()
        
        if not config.embedding_model:
            return "❌ Error: Vector store not initialized. Please initialize the vector store first."
        
        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in texts]
        
        if len(texts) != len(ids):
            return "❌ Error: Number of texts and IDs must match"
        
        added_count = 0
        
        with sqlite3.connect(config.db_file) as conn:
            try:
                # Try to use vec0 extension
                conn.enable_load_extension(True)
                conn.load_extension("vec0")
                
                for text, id_val in zip(texts, ids):
                    embedding = config.embedding_model.embed_query(text)
                    embedding_bytes = _serialize_embedding(embedding)
                    
                    conn.execute(f"""
                        INSERT OR REPLACE INTO {config.table_name} (id, text, embedding)
                        VALUES (?, ?, ?)
                    """, (id_val, text, embedding_bytes))
                    
                    added_count += 1
                
                conn.commit()
                return f"✅ Successfully added {added_count} texts to vector store"
                
            except Exception as e:
                # Fallback to basic storage without vec0
                print(f"⚠️  Warning: vec0 extension not available, using fallback storage: {e}")
                
                for text, id_val in zip(texts, ids):
                    embedding = config.embedding_model.embed_query(text)
                    embedding_bytes = _serialize_embedding(embedding)
                    
                    conn.execute(f"""
                        INSERT OR REPLACE INTO {config.table_name} (id, text, embedding_data)
                        VALUES (?, ?, ?)
                    """, (id_val, text, embedding_bytes))
                    
                    added_count += 1
                
                conn.commit()
                return f"✅ Successfully added {added_count} texts to vector store (fallback mode)"
                
    except Exception as e:
        return f"❌ Error adding texts: {e}"


@tool
def similarity_search(query: str, k: int = 5) -> List[str]:
    """
    Search for similar texts using vector similarity.
    
    Args:
        query: Search query text
        k: Number of results to return
        
    Returns:
        List of similar texts
    """
    try:
        config = _get_config()
        
        if not config.embedding_model:
            return ["❌ Error: Vector store not initialized. Please initialize the vector store first."]
        
        query_embedding = config.embedding_model.embed_query(query)
        
        with sqlite3.connect(config.db_file) as conn:
            try:
                # Try to use vec0 extension for similarity search
                conn.enable_load_extension(True)
                conn.load_extension("vec0")
                
                cursor = conn.execute(f"""
                    SELECT text, embedding <-> ? as distance
                    FROM {config.table_name}
                    ORDER BY distance
                    LIMIT ?
                """, (query_embedding, k))
                
                results = [f"Text: {row[0]} (Distance: {row[1]:.4f})" for row in cursor.fetchall()]
                return results if results else ["No similar texts found"]
                
            except Exception as e:
                # Fallback to basic search without vec0
                print(f"⚠️  Warning: vec0 extension not available, using fallback search: {e}")
                
                # Simple text-based search as fallback
                cursor = conn.execute(f"""
                    SELECT text FROM {config.table_name}
                    WHERE text LIKE ?
                    LIMIT ?
                """, (f"%{query}%", k))
                
                results = [f"Text: {row[0]}" for row in cursor.fetchall()]
                return results if results else ["No similar texts found (fallback mode)"]
                
    except Exception as e:
        return [f"❌ Error during similarity search: {e}"]


@tool
def delete_by_ids(ids: List[str]) -> str:
    """
    Delete texts by their IDs.
    
    Args:
        ids: List of IDs to delete
        
    Returns:
        Success message with count of deleted texts
    """
    try:
        config = _get_config()
        
        with sqlite3.connect(config.db_file) as conn:
            deleted_count = 0
            
            for id_val in ids:
                cursor = conn.execute(f"DELETE FROM {config.table_name} WHERE id = ?", (id_val,))
                if cursor.rowcount > 0:
                    deleted_count += 1
            
            conn.commit()
            return f"✅ Successfully deleted {deleted_count} texts"
            
    except Exception as e:
        return f"❌ Error deleting texts: {e}"


@tool
def delete_by_query(query: str) -> str:
    """
    Delete texts that match a query.
    
    Args:
        query: Text query to match for deletion
        
    Returns:
        Success message with count of deleted texts
    """
    try:
        config = _get_config()
        
        with sqlite3.connect(config.db_file) as conn:
            cursor = conn.execute(f"DELETE FROM {config.table_name} WHERE text LIKE ?", (f"%{query}%",))
            deleted_count = cursor.rowcount
            
            conn.commit()
            return f"✅ Successfully deleted {deleted_count} texts matching query"
            
    except Exception as e:
        return f"❌ Error deleting texts by query: {e}"


@tool
def update_texts(updates: List[dict]) -> str:
    """
    Update existing texts in the vector store.
    
    Args:
        updates: List of dictionaries with 'id' and 'text' keys
        
    Returns:
        Success message with count of updated texts
    """
    try:
        config = _get_config()
        
        if not config.embedding_model:
            return "❌ Error: Vector store not initialized. Please initialize the vector store first."
        
        updated_count = 0
        failed_ids = []
        
        with sqlite3.connect(config.db_file) as conn:
            try:
                # Try to use vec0 extension
                conn.enable_load_extension(True)
                conn.load_extension("vec0")
                
                for update_item in updates:
                    if isinstance(update_item, dict) and 'id' in update_item and 'text' in update_item:
                        id_val = update_item['id']
                        text = update_item['text']
                        
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
                
            except Exception as e:
                # Fallback to basic storage without vec0
                print(f"⚠️  Warning: vec0 extension not available, using fallback update: {e}")
                
                for update_item in updates:
                    if isinstance(update_item, dict) and 'id' in update_item and 'text' in update_item:
                        id_val = update_item['id']
                        text = update_item['text']
                        
                        if id_val and text:
                            # Generate new embedding
                            new_embedding = config.embedding_model.embed_query(text)
                            new_embedding_bytes = _serialize_embedding(new_embedding)
                            
                            cursor = conn.execute(f"""
                                UPDATE {config.table_name} 
                                SET text = ?, embedding_data = ? 
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
    try:
        config = _get_config()
        
        with sqlite3.connect(config.db_file) as conn:
            cursor = conn.execute(f"SELECT id, text FROM {config.table_name}")
            
            return [f"ID: {row[0]} - TEXT: {row[1]}" for row in cursor.fetchall()]
    except Exception as e:
        return [f"❌ Error getting documents: {e}"]


@tool
def get_document_count() -> int:
    """
    Get the total number of documents in the vector store.
    
    Returns:
        Number of documents
    """
    try:
        config = _get_config()
        
        with sqlite3.connect(config.db_file) as conn:
            cursor = conn.execute(f"SELECT COUNT(*) FROM {config.table_name}")
            return cursor.fetchone()[0]
    except Exception as e:
        print(f"❌ Error getting document count: {e}")
        return 0


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
            conn.execute(f"DELETE FROM {config.table_name}")
            conn.commit()
            
            return True
    except Exception as e:
        print(f"❌ Error clearing documents: {e}")
        return False


# List of all available tools for easy import
VECTOR_STORE_TOOLS = [
    add_texts,
    similarity_search,
    delete_by_ids,
    delete_by_query,
    update_texts,
    get_all_documents,
    clear_all_documents
]