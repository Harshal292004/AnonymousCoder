from typing import Any, Dict, List, Optional

from langchain.tools import tool

from ...infrastructure.databases.vector_database import get_vector_store


@tool
def add_texts(texts: List[str], ids: Optional[List[str]] = None, metadata: Optional[List[Dict[str, Any]]] = None) -> str:
    """
    Add texts to the Qdrant vector store with optional IDs and metadata.
    
    Args:
        texts: List of text strings to add
        ids: Optional list of IDs for the texts
        metadata: Optional list of metadata dictionaries for the texts
        
    Returns:
        Success message with count of added texts
    """
    try:
        vector_store = get_vector_store()
        return vector_store.add_texts(texts, ids, metadata)
    except Exception as e:
        return f"❌ Error: {e}"


@tool
def similarity_search(query: str, k: int = 5, filter_metadata: Optional[Dict[str, Any]] = None) -> List[str]:
    """
    Search for similar texts using vector similarity in Qdrant.
    
    Args:
        query: Search query text
        k: Number of results to return
        filter_metadata: Optional metadata filter to apply
        
    Returns:
        List of similar texts with scores
    """
    try:
        vector_store = get_vector_store()
        results = vector_store.similarity_search(query, k, filter_metadata)
        
        if results and "error" not in results[0]:
            formatted_results = []
            for result in results:
                score = result.get("score", 0)
                text = result.get("text", "")
                metadata_str = ""
                if result.get("metadata"):
                    metadata_str = f" (Metadata: {result['metadata']})"
                formatted_results.append(f"Score: {score:.4f} - {text}{metadata_str}")
            return formatted_results
        else:
            return [str(result) for result in results]
            
    except Exception as e:
        return [f"❌ Error during similarity search: {e}"]


@tool
def delete_by_ids(ids: List[str]) -> str:
    """
    Delete texts by their IDs from Qdrant.
    
    Args:
        ids: List of IDs to delete
        
    Returns:
        Success message with count of deleted texts
    """
    try:
        vector_store = get_vector_store()
        return vector_store.delete_by_ids(ids)
    except Exception as e:
        return f"❌ Error: {e}"


@tool
def delete_by_filter(filter_metadata: Dict[str, Any]) -> str:
    """
    Delete texts that match metadata filter from Qdrant.
    
    Args:
        filter_metadata: Metadata filter to match for deletion
        
    Returns:
        Success message with count of deleted texts
    """
    try:
        vector_store = get_vector_store()
        return vector_store.delete_by_filter(filter_metadata)
    except Exception as e:
        return f"❌ Error: {e}"


@tool
def get_all_documents(limit: int = 100) -> List[str]:
    """
    Get all documents in the Qdrant collection.
    
    Args:
        limit: Maximum number of documents to return
        
    Returns:
        List of strings with format "ID: _ TEXT: _ METADATA: _"
    """
    try:
        vector_store = get_vector_store()
        documents = vector_store.get_all_documents(limit)
        
        if documents and "error" not in documents[0]:
            formatted_docs = []
            for doc in documents:
                metadata_str = ""
                if doc.get("metadata"):
                    metadata_str = f" - METADATA: {doc['metadata']}"
                formatted_docs.append(f"ID: {doc['id']} - TEXT: {doc['text']}{metadata_str}")
            return formatted_docs
        else:
            return [str(doc) for doc in documents]
            
    except Exception as e:
        return [f"❌ Error getting documents: {e}"]


@tool
def get_collection_info() -> str:
    """
    Get information about the Qdrant collection.
    
    Returns:
        Collection information as a string
    """
    try:
        vector_store = get_vector_store()
        info = vector_store.get_collection_info()
        
        if "error" not in info:
            return f"Collection: {info['name']}, Vector Size: {info['vector_size']}, Distance: {info['distance']}, Points: {info['points_count']}"
        else:
            return str(info)
            
    except Exception as e:
        return f"❌ Error: {e}"


@tool
def clear_all_documents() -> str:
    """
    Clear all documents from the Qdrant collection.
    
    Returns:
        Success message
    """
    try:
        vector_store = get_vector_store()
        return vector_store.clear_collection()
    except Exception as e:
        return f"❌ Error: {e}"


# List of all available tools for easy import
VECTOR_STORE_TOOLS = [
    add_texts,
    similarity_search,
    delete_by_ids,
    delete_by_filter,
    get_all_documents,
    get_collection_info,
    clear_all_documents
]