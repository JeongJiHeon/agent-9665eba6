"""Calendar event schemas"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class CalendarEventBase(BaseModel):
    """Base calendar event schema"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    attendees: Optional[List[str]] = None


class CalendarEventCreate(CalendarEventBase):
    """Schema for creating calendar event"""
    original_input: str


class CalendarEventUpdate(BaseModel):
    """Schema for updating calendar event"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    attendees: Optional[List[str]] = None


class CalendarEvent(CalendarEventBase):
    """Calendar event schema for responses"""
    id: int
    user_id: int
    google_event_id: str
    original_input: str
    agent_response: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
