"""Calendar events endpoints"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.calendar_event import CalendarEvent
from app.core.deps import get_current_active_user
from app.schemas.calendar_event import (
    CalendarEvent as CalendarEventSchema,
    CalendarEventCreate,
    CalendarEventUpdate
)
from app.services.google_calendar import GoogleCalendarService

router = APIRouter()


@router.get("/", response_model=List[CalendarEventSchema])
def get_user_events(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get user's calendar events"""
    events = (
        db.query(CalendarEvent)
        .filter(CalendarEvent.user_id == current_user.id)
        .order_by(CalendarEvent.start_time.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return events


@router.get("/{event_id}", response_model=CalendarEventSchema)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get a specific calendar event"""
    event = (
        db.query(CalendarEvent)
        .filter(
            CalendarEvent.id == event_id,
            CalendarEvent.user_id == current_user.id
        )
        .first()
    )
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return event


@router.delete("/{event_id}")
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Delete a calendar event"""
    event = (
        db.query(CalendarEvent)
        .filter(
            CalendarEvent.id == event_id,
            CalendarEvent.user_id == current_user.id
        )
        .first()
    )
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Delete from Google Calendar
    try:
        calendar_service = GoogleCalendarService(current_user)
        calendar_service.delete_event(event.google_event_id)
    except Exception as e:
        # Log error but continue with database deletion
        print(f"Failed to delete from Google Calendar: {str(e)}")
    
    # Delete from database
    db.delete(event)
    db.commit()
    
    return {"message": "Event deleted successfully"}


@router.get("/google/sync")
def sync_google_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Sync events from Google Calendar"""
    if not current_user.google_access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google Calendar not connected"
        )
    
    try:
        calendar_service = GoogleCalendarService(current_user)
        google_events = calendar_service.list_events(max_results=50)
        
        synced_count = 0
        for g_event in google_events:
            # Check if event already exists
            existing_event = (
                db.query(CalendarEvent)
                .filter(CalendarEvent.google_event_id == g_event['id'])
                .first()
            )
            
            if not existing_event:
                # Create new event record
                start_time = g_event['start'].get('dateTime', g_event['start'].get('date'))
                end_time = g_event['end'].get('dateTime', g_event['end'].get('date'))
                
                event = CalendarEvent(
                    user_id=current_user.id,
                    google_event_id=g_event['id'],
                    title=g_event.get('summary', 'No Title'),
                    description=g_event.get('description'),
                    start_time=start_time,
                    end_time=end_time,
                    location=g_event.get('location'),
                    original_input="Synced from Google Calendar"
                )
                
                db.add(event)
                synced_count += 1
        
        db.commit()
        
        return {
            "message": f"Synced {synced_count} new events from Google Calendar",
            "synced_count": synced_count
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync failed: {str(e)}"
        )
