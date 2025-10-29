"""
Calendar API routes.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from loguru import logger

from ..services.calendar_service import calendar_service_manager

router = APIRouter(prefix="/calendar", tags=["calendar"])


class EventCreateRequest(BaseModel):
    """Event creation request."""
    user_id: str
    summary: str
    start: str
    end: str
    description: Optional[str] = None
    location: Optional[str] = None


class EventUpdateRequest(BaseModel):
    """Event update request."""
    user_id: str
    event_id: str
    summary: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None


class EventListRequest(BaseModel):
    """Event list request."""
    user_id: str
    time_min: Optional[str] = None
    time_max: Optional[str] = None
    max_results: int = 10


@router.post("/events")
async def create_event(request: EventCreateRequest):
    """
    Create a calendar event.
    
    Args:
        request: Event creation request
        
    Returns:
        Created event data
    """
    try:
        service = calendar_service_manager.get_service(request.user_id)
        
        if not service.is_authenticated():
            raise HTTPException(
                status_code=401,
                detail="User not authenticated with Google Calendar"
            )
        
        event = service.create_event({
            "summary": request.summary,
            "start": request.start,
            "end": request.end,
            "description": request.description,
            "location": request.location,
        })
        
        return {"success": True, "event": event}
        
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/events/list")
async def list_events(request: EventListRequest):
    """
    List calendar events.
    
    Args:
        request: Event list request
        
    Returns:
        List of events
    """
    try:
        service = calendar_service_manager.get_service(request.user_id)
        
        if not service.is_authenticated():
            raise HTTPException(
                status_code=401,
                detail="User not authenticated with Google Calendar"
            )
        
        events = service.list_events(
            time_min=request.time_min,
            time_max=request.time_max,
            max_results=request.max_results
        )
        
        return {"success": True, "events": events}
        
    except Exception as e:
        logger.error(f"Error listing events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/events")
async def update_event(request: EventUpdateRequest):
    """
    Update a calendar event.
    
    Args:
        request: Event update request
        
    Returns:
        Updated event data
    """
    try:
        service = calendar_service_manager.get_service(request.user_id)
        
        if not service.is_authenticated():
            raise HTTPException(
                status_code=401,
                detail="User not authenticated with Google Calendar"
            )
        
        updates = {}
        if request.summary:
            updates["summary"] = request.summary
        if request.start:
            updates["start"] = request.start
        if request.end:
            updates["end"] = request.end
        if request.description:
            updates["description"] = request.description
        if request.location:
            updates["location"] = request.location
        
        event = service.update_event(request.event_id, updates)
        
        return {"success": True, "event": event}
        
    except Exception as e:
        logger.error(f"Error updating event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/events/{user_id}/{event_id}")
async def delete_event(user_id: str, event_id: str):
    """
    Delete a calendar event.
    
    Args:
        user_id: User identifier
        event_id: Event identifier
        
    Returns:
        Success message
    """
    try:
        service = calendar_service_manager.get_service(user_id)
        
        if not service.is_authenticated():
            raise HTTPException(
                status_code=401,
                detail="User not authenticated with Google Calendar"
            )
        
        service.delete_event(event_id)
        
        return {"success": True, "message": "Event deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auth/url/{user_id}")
async def get_auth_url(user_id: str):
    """
    Get Google OAuth authorization URL.
    
    Args:
        user_id: User identifier
        
    Returns:
        Authorization URL
    """
    try:
        service = calendar_service_manager.get_service(user_id)
        auth_url = service.get_authorization_url()
        
        return {"auth_url": auth_url}
        
    except Exception as e:
        logger.error(f"Error getting auth URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))
