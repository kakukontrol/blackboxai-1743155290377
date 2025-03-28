import uuid
import asyncio
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from pydantic import BaseModel
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from app.plugins.base import BasePlugin
from app.storage.vector_store import VectorStoreInterface, DocumentChunk
from app.core.embeddings import EmbeddingGenerator
import logging

class RAGPlugin(BasePlugin):
    """Plugin for Retrieval-Augmented Generation functionality."""
    
    def __init__(self):
        super().__init__()
        self.vector_store = None
        self.embedding_generator = None
        self.text_splitter = None
        self.default_collection = "personachat_docs"
        
    def get_name(self) -> str:
        return "RAG Plugin"
        
    def get_description(self) -> str:
        return "Provides retrieval-augmented generation capabilities with document upload"
        
    def initialize(self, context):
        self.vector_store = context.vector_store
        self.embedding_generator = context.embedding_generator
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        # Ensure default collection exists
        asyncio.create_task(
            self.vector_store.ensure_collection(
                self.default_collection,
                self.embedding_generator.dimension
            )
        )
        
    def register_api_routes(self) -> APIRouter:
        router = APIRouter()
        router.add_api_route(
            "/upload",
            self.upload_document,
            methods=["POST"],
            response_model=Dict[str, str]
        )
        return router
        
    async def perform_rag_search(
        self,
        query: str,
        collection_name: Optional[str] = None,
        top_k: int = 3
    ) -> str:
        """Perform RAG search and format results."""
        collection = collection_name or self.default_collection
        try:
            query_embedding = self.embedding_generator.generate_single_embedding(query)
            results = await self.vector_store.search(collection, query_embedding, top_k)
            
            if not results:
                return ""
                
            context_parts = []
            for chunk, score in results:
                context_parts.append(
                    f"Source: {chunk.metadata.get('source', 'Unknown')} (Score: {score:.2f})\n"
                    f"Content: {chunk.content}"
                )
            return "\n---\n".join(context_parts)
        except Exception as e:
            logging.error(f"RAG search failed: {str(e)}")
            return ""
            
    async def process_input(self, text: str, context: Dict[str, Any]) -> Optional[str]:
        """Process RAG commands."""
        if text.strip().lower().startswith("/rag "):
            query = text.strip()[len("/rag "):]
            if query:
                context['system_prompt_prefix'] = await self.perform_rag_search(query)
            return None
        return None
        
    async def upload_document(
        self,
        file: UploadFile = File(...),
        collection: Optional[str] = None
    ) -> Dict[str, str]:
        """Upload and process a document for RAG."""
        target_collection = collection or self.default_collection
        try:
            # Read and parse file content
            if file.content_type == "application/pdf":
                reader = PdfReader(file.file)
                text = "\n".join([page.extract_text() for page in reader.pages])
            else:
                text = (await file.read()).decode("utf-8")
                
            # Split into chunks
            chunks = self.text_splitter.split_text(text)
            document_chunks = [
                DocumentChunk(
                    id=str(uuid.uuid4()),
                    content=chunk,
                    metadata={"source": file.filename}
                )
                for chunk in chunks
            ]
            
            # Generate embeddings and upsert
            vectors = self.embedding_generator.generate_embeddings(
                [chunk.content for chunk in document_chunks]
            )
            await self.vector_store.upsert_vectors(
                target_collection,
                document_chunks,
                vectors
            )
            
            return {"status": "success", "message": f"Uploaded {file.filename}"}
            
        except Exception as e:
            logging.error(f"Document upload failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))