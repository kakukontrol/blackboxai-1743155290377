import abc
import uuid
from typing import List, Dict, Any, Optional, Tuple, NamedTuple
import numpy as np
import qdrant_client
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter
from app.core.config import ConfigManager

class DocumentChunk(NamedTuple):
    """Represents a chunk of a document with metadata for vector storage."""
    id: str
    content: str
    metadata: Dict[str, Any]

class VectorStoreInterface(abc.ABC):
    """Abstract base class defining the vector store interface."""
    
    @abc.abstractmethod
    async def initialize(self, config_manager: ConfigManager) -> None:
        """Initialize the vector store connection."""
        pass
    
    @abc.abstractmethod
    async def upsert_vectors(
        self, 
        collection_name: str, 
        chunks: List[DocumentChunk], 
        vectors: List[List[float]]
    ) -> None:
        """Upsert vectors into the store."""
        pass
    
    @abc.abstractmethod
    async def search(
        self,
        collection_name: str,
        query_vector: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict] = None
    ) -> List[Tuple[DocumentChunk, float]]:
        """Search for similar vectors."""
        pass
    
    @abc.abstractmethod
    async def delete_collection(self, collection_name: str) -> None:
        """Delete a collection."""
        pass
    
    @abc.abstractmethod
    async def ensure_collection(self, collection_name: str, vector_size: int) -> None:
        """Ensure a collection exists with the correct vector size."""
        pass

class QdrantVectorStore(VectorStoreInterface):
    """Qdrant implementation of the vector store interface."""
    
    def __init__(self):
        self.client = None
    
    async def initialize(self, config_manager: ConfigManager) -> None:
        """Initialize Qdrant client connection."""
        qdrant_url = config_manager.get_setting("QDRANT_URL")
        qdrant_api_key = config_manager.get_setting("QDRANT_API_KEY")
        
        if not qdrant_url:
            raise ValueError("QDRANT_URL is not configured")
        
        try:
            self.client = qdrant_client.AsyncQdrantClient(
                url=qdrant_url,
                api_key=qdrant_api_key,
                timeout=30
            )
            # Test connection
            await self.client.get_collections()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Qdrant: {str(e)}")
    
    async def ensure_collection(self, collection_name: str, vector_size: int) -> None:
        """Ensure collection exists with proper configuration."""
        if not self.client:
            raise RuntimeError("Qdrant client not initialized")
        
        collections = await self.client.get_collections()
        collection_names = {col.name for col in collections.collections}
        
        if collection_name not in collection_names:
            await self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
    
    async def upsert_vectors(
        self,
        collection_name: str,
        chunks: List[DocumentChunk],
        vectors: List[List[float]]
    ) -> None:
        """Upsert document chunks with their vectors."""
        if not self.client:
            raise RuntimeError("Qdrant client not initialized")
        
        if len(chunks) != len(vectors):
            raise ValueError("Chunks and vectors must have same length")
        
        points = [
            PointStruct(
                id=chunk.id or str(uuid.uuid4()),
                vector=vector,
                payload={
                    "content": chunk.content,
                    "metadata": chunk.metadata
                }
            )
            for chunk, vector in zip(chunks, vectors)
        ]
        
        try:
            await self.client.upsert(
                collection_name=collection_name,
                points=points,
                wait=True
            )
        except Exception as e:
            raise RuntimeError(f"Failed to upsert vectors: {str(e)}")
    
    async def search(
        self,
        collection_name: str,
        query_vector: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict] = None
    ) -> List[Tuple[DocumentChunk, float]]:
        """Search for similar vectors."""
        if not self.client:
            raise RuntimeError("Qdrant client not initialized")
        
        query_filter = Filter(**filter_dict) if filter_dict else None
        
        try:
            results = await self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=top_k
            )
            
            return [
                (
                    DocumentChunk(
                        id=result.id,
                        content=result.payload["content"],
                        metadata=result.payload.get("metadata", {})
                    ),
                    result.score
                )
                for result in results
            ]
        except Exception as e:
            raise RuntimeError(f"Search failed: {str(e)}")
    
    async def delete_collection(self, collection_name: str) -> None:
        """Delete a collection."""
        if not self.client:
            raise RuntimeError("Qdrant client not initialized")
        
        try:
            await self.client.delete_collection(collection_name)
        except Exception as e:
            raise RuntimeError(f"Failed to delete collection: {str(e)}")