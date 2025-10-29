"""Memory management for conversation history."""

from typing import Optional, List, Dict, Any
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain_openai import ChatOpenAI
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from loguru import logger
import redis.asyncio as aioredis

from app.config import settings


class ConversationMemoryManager:
    """Manages conversation memory with Redis backend."""
    
    def __init__(self):
        self.redis_client: Optional[aioredis.Redis] = None
        self.memory_cache: Dict[str, ConversationBufferMemory] = {}
    
    async def initialize(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = await aioredis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                encoding="utf-8",
                decode_responses=True,
            )
            await self.redis_client.ping()
            logger.info("Redis connection established for memory management")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
    
    def get_memory(self, session_id: str) -> ConversationBufferMemory:
        """
        Get or create conversation memory for a session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            ConversationBufferMemory instance
        """
        if session_id in self.memory_cache:
            return self.memory_cache[session_id]
        
        # Create new memory with Redis backend if available
        if self.redis_client:
            message_history = RedisChatMessageHistory(
                session_id=session_id,
                url=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
                key_prefix="calendar_agent:",
            )
        else:
            message_history = None
        
        memory = ConversationBufferMemory(
            memory_key=settings.MEMORY_KEY,
            return_messages=True,
            chat_memory=message_history,
            max_token_limit=settings.MEMORY_MAX_TOKEN_LIMIT,
        )
        
        self.memory_cache[session_id] = memory
        return memory
    
    async def add_message(
        self,
        session_id: str,
        message: str,
        is_user: bool = True
    ):
        """
        Add a message to conversation history.
        
        Args:
            session_id: Session identifier
            message: Message content
            is_user: True if user message, False if AI message
        """
        memory = self.get_memory(session_id)
        
        if is_user:
            memory.chat_memory.add_user_message(message)
        else:
            memory.chat_memory.add_ai_message(message)
    
    async def get_history(self, session_id: str) -> List[BaseMessage]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of messages
        """
        memory = self.get_memory(session_id)
        return memory.chat_memory.messages
    
    async def clear_history(self, session_id: str):
        """
        Clear conversation history for a session.
        
        Args:
            session_id: Session identifier
        """
        if session_id in self.memory_cache:
            memory = self.memory_cache[session_id]
            memory.chat_memory.clear()
            del self.memory_cache[session_id]
        
        # Also clear from Redis
        if self.redis_client:
            await self.redis_client.delete(f"calendar_agent:{session_id}")
    
    async def get_summary(self, session_id: str) -> Optional[str]:
        """
        Get a summary of the conversation.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Summary string or None
        """
        try:
            messages = await self.get_history(session_id)
            if not messages:
                return None
            
            # Create summary using LLM
            llm = ChatOpenAI(
                model=settings.LLM_MODEL,
                temperature=0.3,
            )
            
            summary_memory = ConversationSummaryMemory(
                llm=llm,
                memory_key=settings.MEMORY_KEY,
            )
            
            # Add messages to summary memory
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    summary_memory.chat_memory.add_user_message(msg.content)
                elif isinstance(msg, AIMessage):
                    summary_memory.chat_memory.add_ai_message(msg.content)
            
            return summary_memory.buffer
        
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return None
    
    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()


# Global memory manager instance
memory_manager = ConversationMemoryManager()
