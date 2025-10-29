"""
Google Calendar API integration service.
"""
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json
import os
from loguru import logger

from ..config import settings


class GoogleCalendarService:
    """Service for interacting with Google Calendar API."""
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self, user_id: str, credentials: Optional[Dict[str, Any]] = None):
        """
        Initialize Google Calendar service.
        
        Args:
            user_id: User identifier
            credentials: Google OAuth2 credentials dict
        """
        self.user_id = user_id
        self.credentials = self._load_credentials(credentials)
        self.service = None
        
        if self.credentials:
            self._build_service()
    
    def _load_credentials(self, credentials_dict: Optional[Dict[str, Any]] = None) -> Optional[Credentials]:
        """Load credentials from dict or file."""
        try:
            if credentials_dict:
                creds = Credentials.from_authorized_user_info(
                    credentials_dict,
                    self.SCOPES
                )
                return creds
            
            # Try to load from token file
            token_file = f"./tokens/token_{self.user_id}.json"
            if os.path.exists(token_file):
                with open(token_file, 'r') as token:
                    creds = Credentials.from_authorized_user_info(
                        json.load(token),
                        self.SCOPES
                    )
                    return creds
            
            return None
        except Exception as e:
            logger.error(f"Error loading credentials: {e}")
            return None
    
    def _build_service(self):
        """Build Google Calendar service."""
        try:
            # Refresh token if expired
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
                self._save_credentials()
            
            self.service = build('calendar', 'v3', credentials=self.credentials)
            logger.info(f"Built Google Calendar service for user {self.user_id}")
        except Exception as e:
            logger.error(f"Error building service: {e}")
            raise
    
    def _save_credentials(self):
        """Save credentials to file."""
        try:
            os.makedirs("./tokens", exist_ok=True)
            token_file = f"./tokens/token_{self.user_id}.json"
            
            with open(token_file, 'w') as token:
                token.write(self.credentials.to_json())
            
            logger.info(f"Saved credentials for user {self.user_id}")
        except Exception as e:
            logger.error(f"Error saving credentials: {e}")
    
    def set_credentials(self, credentials_dict: Dict[str, Any]):
        """Set credentials from dict."""
        self.credentials = Credentials.from_authorized_user_info(
            credentials_dict,
            self.SCOPES
        )
        self._save_credentials()
        self._build_service()
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.credentials is not None and self.service is not None
    
    def get_authorization_url(self) -> str:
        """Get OAuth2 authorization URL."""
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                    }
                },
                scopes=self.SCOPES,
                redirect_uri=settings.GOOGLE_REDIRECT_URI
            )
            
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
            
            return auth_url
        except Exception as e:
            logger.error(f"Error getting authorization URL: {e}")
            raise
    
    def create_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a calendar event.
        
        Args:
            event_data: Event data containing summary, start, end, etc.
            
        Returns:
            Created event data
        """
        if not self.is_authenticated():
            raise Exception("User not authenticated")
        
        try:
            # Format event body
            event = {
                'summary': event_data.get('summary'),
                'location': event_data.get('location', ''),
                'description': event_data.get('description', ''),
                'start': {
                    'dateTime': event_data.get('start'),
                    'timeZone': 'Asia/Seoul',
                },
                'end': {
                    'dateTime': event_data.get('end'),
                    'timeZone': 'Asia/Seoul',
                },
            }
            
            # Add optional fields
            if 'attendees' in event_data:
                event['attendees'] = event_data['attendees']
            
            if 'reminders' in event_data:
                event['reminders'] = event_data['reminders']
            else:
                event['reminders'] = {
                    'useDefault': True
                }
            
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            logger.info(f"Created event: {created_event.get('id')}")
            return created_event
            
        except HttpError as error:
            logger.error(f"Google Calendar API error: {error}")
            raise
        except Exception as e:
            logger.error(f"Error creating event: {e}")
            raise
    
    def list_events(
        self,
        time_min: Optional[str] = None,
        time_max: Optional[str] = None,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        List calendar events.
        
        Args:
            time_min: Start time for event search
            time_max: End time for event search
            max_results: Maximum number of results
            
        Returns:
            List of events
        """
        if not self.is_authenticated():
            raise Exception("User not authenticated")
        
        try:
            # Default to today if not specified
            if not time_min:
                time_min = datetime.utcnow().isoformat() + 'Z'
            
            if not time_max:
                time_max = (datetime.utcnow() + timedelta(days=30)).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            logger.info(f"Retrieved {len(events)} events")
            
            return events
            
        except HttpError as error:
            logger.error(f"Google Calendar API error: {error}")
            raise
        except Exception as e:
            logger.error(f"Error listing events: {e}")
            raise
    
    def get_event(self, event_id: str) -> Dict[str, Any]:
        """
        Get a specific event.
        
        Args:
            event_id: Event identifier
            
        Returns:
            Event data
        """
        if not self.is_authenticated():
            raise Exception("User not authenticated")
        
        try:
            event = self.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            return event
            
        except HttpError as error:
            logger.error(f"Google Calendar API error: {error}")
            raise
        except Exception as e:
            logger.error(f"Error getting event: {e}")
            raise
    
    def update_event(self, event_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a calendar event.
        
        Args:
            event_id: Event identifier
            updates: Fields to update
            
        Returns:
            Updated event data
        """
        if not self.is_authenticated():
            raise Exception("User not authenticated")
        
        try:
            # Get existing event
            event = self.get_event(event_id)
            
            # Update fields
            if 'summary' in updates:
                event['summary'] = updates['summary']
            
            if 'start' in updates:
                event['start'] = {
                    'dateTime': updates['start'],
                    'timeZone': 'Asia/Seoul',
                }
            
            if 'end' in updates:
                event['end'] = {
                    'dateTime': updates['end'],
                    'timeZone': 'Asia/Seoul',
                }
            
            if 'description' in updates:
                event['description'] = updates['description']
            
            if 'location' in updates:
                event['location'] = updates['location']
            
            # Update event
            updated_event = self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()
            
            logger.info(f"Updated event: {event_id}")
            return updated_event
            
        except HttpError as error:
            logger.error(f"Google Calendar API error: {error}")
            raise
        except Exception as e:
            logger.error(f"Error updating event: {e}")
            raise
    
    def delete_event(self, event_id: str):
        """
        Delete a calendar event.
        
        Args:
            event_id: Event identifier
        """
        if not self.is_authenticated():
            raise Exception("User not authenticated")
        
        try:
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            logger.info(f"Deleted event: {event_id}")
            
        except HttpError as error:
            logger.error(f"Google Calendar API error: {error}")
            raise
        except Exception as e:
            logger.error(f"Error deleting event: {e}")
            raise


class CalendarServiceManager:
    """Manage calendar service instances for multiple users."""
    
    def __init__(self):
        self.services: Dict[str, GoogleCalendarService] = {}
    
    def get_service(self, user_id: str, credentials: Optional[Dict[str, Any]] = None) -> GoogleCalendarService:
        """Get or create calendar service for user."""
        if user_id not in self.services:
            self.services[user_id] = GoogleCalendarService(user_id, credentials)
        return self.services[user_id]
    
    def remove_service(self, user_id: str):
        """Remove calendar service for user."""
        if user_id in self.services:
            del self.services[user_id]


# Global service manager instance
calendar_service_manager = CalendarServiceManager()
