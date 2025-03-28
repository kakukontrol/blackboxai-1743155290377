import logging
from typing import List, Dict, Any
from app.storage.vector_store import VectorStoreInterface
from app.core.embeddings import EmbeddingGenerator

async def perform_rag_search(
    query: str,
    vector_store: VectorStoreInterface,
    embed_generator: EmbeddingGenerator,
    collection_name: str = "default_documents",
    top_k: int = 3
) -> str:
    """Perform a RAG search using the provided query."""
    logging.info(f"Performing RAG search for query: {query}")
    
    try:
        # Generate the query embedding
        query_embedding = embed_generator.generate_single_embedding(query)
        
        # Perform the search
        results = await vector_store.search(collection_name, query_embedding, top_k)
        
        if not results:
            return ""
        
        # Format the retrieved DocumentChunk contents
        context_parts = []
        for chunk, score in results:
            context_parts.append(
                f"Source: {chunk.metadata.get('source', 'Unknown')} (Score: {score:.2f})\nContent: {chunk.content}"
            )
        context_str = "\n---\n".join(context_parts)
        return context_str
    
    except Exception as e:
        logging.error(f"Error during RAG search: {str(e)}")
        return ""