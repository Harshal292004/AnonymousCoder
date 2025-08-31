import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import (Distance, FieldCondition, Filter, MatchValue,
                                  PointStruct, VectorParams)

# Load environment variables
load_dotenv()

class QdrantVectorStore:
    """Qdrant-based vector store implementation."""
    
    def __init__(self, collection_name: str = "documents"):
        self.collection_name = collection_name
        self.client = QdrantClient(
            url=os.getenv("QDRANT_HOST"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        self.embedding_model = None
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """Ensure the collection exists with proper configuration."""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                # Create collection with default parameters
                # We'll update the vector size when we have an embedding model
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=768, distance=Distance.COSINE)
                )
                print(f"✅ Created Qdrant collection: {self.collection_name}")
            else:
                print(f"✅ Using existing Qdrant collection: {self.collection_name}")
                
        except Exception as e:
            print(f"❌ Error ensuring collection exists: {e}")
            raise
    
    def set_embedding_model(self, embedding_model: HuggingFaceEmbeddings):
        """Set the embedding model and update collection if needed."""
        self.embedding_model = embedding_model
        
        # Get embedding dimension
        sample_text = "sample"
        sample_embedding = self.embedding_model.embed_query(sample_text)
        embedding_dim = len(sample_embedding)
        
        # Check if we need to recreate the collection with correct vector size
        try:
            collection_info = self.client.get_collection(self.collection_name)
            current_size = collection_info.config.params.vectors.size
            
            if current_size != embedding_dim:
                print(f"⚠️  Vector size mismatch. Current: {current_size}, Required: {embedding_dim}")
                print("⚠️  Please manually recreate the collection with correct vector size")
                print(f"⚠️  Or use collection name that matches dimension {embedding_dim}")
        except Exception as e:
            print(f"⚠️  Could not verify collection configuration: {e}")
    
    def add_texts(self, texts: List[str], ids: Optional[List[str]] = None, metadata: Optional[List[Dict[str, Any]]] = None) -> str:
        """Add texts to the vector store."""
        if not self.embedding_model:
            return "❌ Error: Embedding model not set. Call set_embedding_model() first."
        
        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in texts]
        
        if metadata is None:
            metadata = [{} for _ in texts]
        
        if len(texts) != len(ids) or len(texts) != len(metadata):
            return "❌ Error: Number of texts, IDs, and metadata must match"
        
        try:
            points = []
            for text, id_val, meta in zip(texts, ids, metadata):
                embedding = self.embedding_model.embed_query(text)
                
                point = PointStruct(
                    id=id_val,
                    vector=embedding,
                    payload={
                        "text": text,
                        **meta
                    }
                )
                points.append(point)
            
            # Upsert points
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            return f"✅ Successfully added {len(texts)} texts to Qdrant"
            
        except Exception as e:
            return f"❌ Error adding texts: {e}"
    
    def similarity_search(self, query: str, k: int = 5, filter_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for similar texts using vector similarity."""
        if not self.embedding_model:
            return [{"error": "Embedding model not set"}]
        
        try:
            query_embedding = self.embedding_model.embed_query(query)
            
            # Build filter if metadata filter is provided
            search_filter = None
            if filter_metadata:
                conditions = []
                for key, value in filter_metadata.items():
                    conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
                search_filter = Filter(must=conditions)
            
            # Search
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=k,
                query_filter=search_filter
            )
            
            results = []
            for scored_point in search_result:
                results.append({
                    "id": scored_point.id,
                    "text": scored_point.payload.get("text", ""),
                    "score": scored_point.score,
                    "metadata": {k: v for k, v in scored_point.payload.items() if k != "text"}
                })
            
            return results
            
        except Exception as e:
            return [{"error": f"Search error: {e}"}]
    
    def delete_by_ids(self, ids: List[str]) -> str:
        """Delete texts by their IDs."""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=ids
            )
            return f"✅ Successfully deleted {len(ids)} texts"
        except Exception as e:
            return f"❌ Error deleting texts: {e}"
    
    def delete_by_filter(self, filter_metadata: Dict[str, Any]) -> str:
        """Delete texts that match metadata filter."""
        try:
            conditions = []
            for key, value in filter_metadata.items():
                conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
            
            filter_obj = Filter(must=conditions)
            
            # First, find matching points
            search_result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=filter_obj,
                limit=1000  # Adjust as needed
            )
            
            if search_result[0]:  # Points found
                ids_to_delete = [point.id for point in search_result[0]]
                if ids_to_delete:
                    self.client.delete(
                        collection_name=self.collection_name,
                        points_selector=ids_to_delete
                    )
                    return f"✅ Successfully deleted {len(ids_to_delete)} texts matching filter"
                else:
                    return "ℹ️  No texts found matching filter"
            else:
                return "ℹ️  No texts found matching filter"
                
        except Exception as e:
            return f"❌ Error deleting texts by filter: {e}"
    
    def get_all_documents(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get all documents in the collection."""
        try:
            scroll_result = self.client.scroll(
                collection_name=self.collection_name,
                limit=limit
            )
            
            documents = []
            for point in scroll_result[0]:
                documents.append({
                    "id": point.id,
                    "text": point.payload.get("text", ""),
                    "metadata": {k: v for k, v in point.payload.items() if k != "text"}
                })
            
            return documents
            
        except Exception as e:
            return [{"error": f"Error getting documents: {e}"}]
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": info.name,
                "vector_size": info.config.params.vectors.size,
                "distance": info.config.params.vectors.distance,
                "points_count": info.points_count
            }
        except Exception as e:
            return {"error": f"Error getting collection info: {e}"}
    
    def clear_collection(self) -> str:
        """Clear all documents from the collection."""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector="*"
            )
            return "✅ Successfully cleared all documents"
        except Exception as e:
            return f"❌ Error clearing collection: {e}"


# Global instance
_vector_store = None

def initialize_vector_store(collection_name: str = "documents", embedding_model: Optional[HuggingFaceEmbeddings] = None) -> QdrantVectorStore:
    """Initialize the Qdrant vector store."""
    global _vector_store
    _vector_store = QdrantVectorStore(collection_name)
    
    if embedding_model:
        _vector_store.set_embedding_model(embedding_model)
    
    return _vector_store

def get_vector_store() -> QdrantVectorStore:
    """Get the global vector store instance."""
    global _vector_store
    if _vector_store is None:
        raise RuntimeError("Vector store not initialized. Call initialize_vector_store() first.")
    return _vector_store


