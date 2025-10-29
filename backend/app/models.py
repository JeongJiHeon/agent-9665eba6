"""Data models for the application."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """Message role in conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Chat message model."""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ConversationRequest(BaseModel):
    """Request model for conversation endpoint."""
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = "default_user"


class ConversationResponse(BaseModel):
    """Response model for conversation endpoint."""
    message: str
    session_id: str
    events_created: List[Dict[str, Any]] = []
    suggestions: List[str] = []


class CalendarEvent(BaseModel):
    """Google Calendar event model."""
    summary: str = Field(..., description="Event title/summary")
    description: Optional[str] = Field(None, description="Event description")
    start_time: datetime = Field(..., description="Event start time")
    end_time: datetime = Field(..., description="Event end time")
    location: Optional[str] = Field(None, description="Event location")
    attendees: List[str] = Field(default_factory=list, description="List of attendee emails")
    reminders: List[int] = Field(default_factory=lambda: [10], description="Reminder minutes before event")


class EventCreationResult(BaseModel):
    """Result of calendar event creation."""
    success: bool
    event_id: Optional[str] = None
    event_link: Optional[str] = None
    error: Optional[str] = None
    event_details: Optional[Dict[str, Any]] = None


class HealthCheck(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.now)
    services: Dict[str, bool] = {}


class AuthCallbackRequest(BaseModel):
    """OAuth callback request."""
    code: str
    state: Optional[str] = None


class SearchQuery(BaseModel):
    """Vector search query."""
    query: str
    top_k: int = 5
    user_id: str = "default_user"
