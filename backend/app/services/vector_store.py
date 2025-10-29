"""Vector store service for RAG functionality."""

from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from loguru import logger

from app.config import settings as app_settings


class VectorStoreService:
    """Service for managing vector store (Chroma) for RAG."""
    
    def __init__(self):
        self.client: Optional[chromadb.Client] = None
        self.collection = None
        self.embedding_function = None
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize ChromaDB client and collection."""
        try:
            # Create persistent client
            self.client = chromadb.PersistentClient(
                path=app_settings.CHROMA_PERSIST_DIRECTORY,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                )
            )
            
            # Use sentence transformers for embeddings
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=app_settings.CHROMA_COLLECTION_NAME,
                embedding_function=self.embedding_function,
                metadata={"description": "Calendar events for RAG"}
            )
            
            self.is_initialized = True
            logger.info(f"Vector store initialized with {self.collection.count()} documents")
        
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            self.is_initialized = False
            raise
    
    async def add_event(
        self,
        event_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Add a calendar event to vector store.
        
        Args:
            event_id: Unique event identifier
            text: Event text to embed
            metadata: Additional metadata
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            self.collection.add(
                documents=[text],
                metadatas=[metadata or {}],
                ids=[event_id]
            )
            logger.info(f"Added event to vector store: {event_id}")
        
        except Exception as e:
            logger.error(f"Error adding event to vector store: {e}")
    
    async def search_similar(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar events using vector similarity.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Metadata filters
            
        Returns:
            List of similar events with metadata
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where=filter_metadata,
            )
            
            # Format results
            formatted_results = []
            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        'id': results['ids'][0][i],
                        'document': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None,
                    })
            
            logger.info(f"Found {len(formatted_results)} similar events")
            return formatted_results
        
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    async def delete_event(self, event_id: str):
        """
        Delete an event from vector store.
        
        Args:
            event_id: Event ID to delete
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            self.collection.delete(ids=[event_id])
            logger.info(f"Deleted event from vector store: {event_id}")
        
        except Exception as e:
            logger.error(f"Error deleting event from vector store: {e}")
    
    async def update_event(
        self,
        event_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Update an event in vector store.
        
        Args:
            event_id: Event ID to update
            text: Updated text
            metadata: Updated metadata
        """
        # Delete and re-add (ChromaDB doesn't have direct update)
        await self.delete_event(event_id)
        await self.add_event(event_id, text, metadata)
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store collection.
        
        Returns:
            Dictionary with collection stats
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": app_settings.CHROMA_COLLECTION_NAME,
                "is_initialized": self.is_initialized,
            }
        
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {
                "total_documents": 0,
                "is_initialized": False,
                "error": str(e)
            }
    
    async def clear_collection(self):
        """Clear all documents from the collection."""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Delete collection and recreate
            self.client.delete_collection(app_settings.CHROMA_COLLECTION_NAME)
            self.collection = self.client.create_collection(
                name=app_settings.CHROMA_COLLECTION_NAME,
                embedding_function=self.embedding_function,
            )
            logger.info("Cleared vector store collection")
        
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")


# Global service instance
vector_store_service = VectorStoreService()
