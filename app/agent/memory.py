"""Memory management for the AI agent"""

from typing import List, Dict, Any
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.user import User
from app.config import settings


class DatabaseChatMemory:
    """Custom memory that stores conversations in database"""
    
    def __init__(self, db: Session, user: User, session_id: str):
        """Initialize database chat memory"""
        self.db = db
        self.user = user
        self.session_id = session_id
        self.memory_key = "chat_history"
    
    def load_memory_variables(self) -> Dict[str, Any]:
        """Load conversation history from database"""
        conversations = (
            self.db.query(Conversation)
            .filter(
                Conversation.user_id == self.user.id,
                Conversation.session_id == self.session_id
            )
            .order_by(Conversation.created_at)
            .limit(20)  # Load last 20 messages
            .all()
        )
        
        messages = []
        for conv in conversations:
            if conv.role == "user":
                messages.append(HumanMessage(content=conv.content))
            elif conv.role == "assistant":
                messages.append(AIMessage(content=conv.content))
        
        return {self.memory_key: messages}
    
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save conversation to database"""
        # Save user message
        user_message = Conversation(
            user_id=self.user.id,
            session_id=self.session_id,
            role="user",
            content=inputs.get("input", "")
        )
        self.db.add(user_message)
        
        # Save assistant message
        assistant_message = Conversation(
            user_id=self.user.id,
            session_id=self.session_id,
            role="assistant",
            content=outputs.get("output", "")
        )
        self.db.add(assistant_message)
        
        self.db.commit()
    
    def clear(self) -> None:
        """Clear conversation history"""
        self.db.query(Conversation).filter(
            Conversation.user_id == self.user.id,
            Conversation.session_id == self.session_id
        ).delete()
        self.db.commit()


class HybridMemory:
    """Hybrid memory combining buffer and summary"""
    
    def __init__(self, llm: ChatOpenAI):
        """Initialize hybrid memory"""
        self.buffer_memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="output"
        )
        
        self.summary_memory = ConversationSummaryMemory(
            llm=llm,
            memory_key="conversation_summary",
            output_key="output"
        )
    
    def load_memory_variables(self) -> Dict[str, Any]:
        """Load memory variables"""
        buffer_vars = self.buffer_memory.load_memory_variables({})
        summary_vars = self.summary_memory.load_memory_variables({})
        return {**buffer_vars, **summary_vars}
    
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context to both memories"""
        self.buffer_memory.save_context(inputs, outputs)
        self.summary_memory.save_context(inputs, outputs)
    
    def clear(self) -> None:
        """Clear both memories"""
        self.buffer_memory.clear()
        self.summary_memory.clear()
