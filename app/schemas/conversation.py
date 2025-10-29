"""Conversation and agent schemas"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ConversationBase(BaseModel):
    """Base conversation schema"""
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str


class ConversationCreate(ConversationBase):
    """Schema for creating conversation"""
    session_id: str
    metadata: Optional[Dict[str, Any]] = None


class Conversation(ConversationBase):
    """Conversation schema for responses"""
    id: int
    user_id: int
    session_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class AgentRequest(BaseModel):
    """Schema for agent request"""
    message: str = Field(..., min_length=1)
    session_id: Optional[str] = None
    stream: bool = False


class AgentResponse(BaseModel):
    """Schema for agent response"""
    message: str
    session_id: str
    calendar_event_created: bool = False
    event_details: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
