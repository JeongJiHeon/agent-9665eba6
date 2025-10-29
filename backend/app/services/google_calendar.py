"""Google Calendar API integration."""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from loguru import logger
import os
import pickle

from app.config import settings
from app.models import CalendarEvent, EventCreationResult


class GoogleCalendarService:
    """Service for interacting with Google Calendar API."""
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self):
        self.creds: Optional[Credentials] = None
        self.service = None
        self._token_file = "token.pickle"
    
    def _get_credentials(self) -> Optional[Credentials]:
        """Get or refresh credentials."""
        creds = None
        
        # Load credentials from file
        if os.path.exists(self._token_file):
            try:
                with open(self._token_file, 'rb') as token:
                    creds = pickle.load(token)
            except Exception as e:
                logger.error(f"Error loading credentials: {e}")
        
        # Refresh if expired
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                self._save_credentials(creds)
            except Exception as e:
                logger.error(f"Error refreshing credentials: {e}")
                creds = None
        
        return creds
    
    def _save_credentials(self, creds: Credentials):
        """Save credentials to file."""
        try:
            with open(self._token_file, 'wb') as token:
                pickle.dump(creds, token)
            logger.info("Credentials saved successfully")
        except Exception as e:
            logger.error(f"Error saving credentials: {e}")
    
    def initialize_oauth_flow(self, redirect_uri: str) -> Flow:
        """
        Initialize OAuth flow for user authentication.
        
        Args:
            redirect_uri: OAuth redirect URI
            
        Returns:
            OAuth Flow instance
        """
        try:
            flow = Flow.from_client_secrets_file(
                settings.GOOGLE_CREDENTIALS_FILE,
                scopes=self.SCOPES,
                redirect_uri=redirect_uri
            )
            return flow
        except Exception as e:
            logger.error(f"Error initializing OAuth flow: {e}")
            raise
    
    def get_authorization_url(self, redirect_uri: str) -> str:
        """
        Get OAuth authorization URL.
        
        Args:
            redirect_uri: OAuth redirect URI
            
        Returns:
            Authorization URL
        """
        flow = self.initialize_oauth_flow(redirect_uri)
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        return auth_url
    
    async def handle_oauth_callback(self, code: str, redirect_uri: str) -> bool:
        """
        Handle OAuth callback and save credentials.
        
        Args:
            code: Authorization code from callback
            redirect_uri: OAuth redirect URI
            
        Returns:
            True if successful
        """
        try:
            flow = self.initialize_oauth_flow(redirect_uri)
            flow.fetch_token(code=code)
            
            creds = flow.credentials
            self._save_credentials(creds)
            self.creds = creds
            self.service = build('calendar', 'v3', credentials=creds)
            
            logger.info("OAuth authentication successful")
            return True
        
        except Exception as e:
            logger.error(f"OAuth callback error: {e}")
            return False
    
    def _ensure_service(self):
        """Ensure calendar service is initialized."""
        if not self.service:
            self.creds = self._get_credentials()
            if self.creds:
                self.service = build('calendar', 'v3', credentials=self.creds)
            else:
                raise ValueError("No valid credentials. Please authenticate first.")
    
    async def create_event(
        self,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        reminders: Optional[List[int]] = None,
    ) -> EventCreationResult:
        """
        Create a calendar event.
        
        Args:
            summary: Event title
            start_time: Event start datetime
            end_time: Event end datetime
            description: Event description
            location: Event location
            attendees: List of attendee emails
            reminders: List of reminder minutes before event
            
        Returns:
            EventCreationResult
        """
        try:
            self._ensure_service()
            
            # Build event body
            event_body = {
                'summary': summary,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'Asia/Seoul',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'Asia/Seoul',
                },
            }
            
            if description:
                event_body['description'] = description
            
            if location:
                event_body['location'] = location
            
            if attendees:
                event_body['attendees'] = [{'email': email} for email in attendees]
            
            if reminders:
                event_body['reminders'] = {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': minutes}
                        for minutes in reminders
                    ],
                }
            
            # Create event
            event = self.service.events().insert(
                calendarId='primary',
                body=event_body
            ).execute()
            
            logger.info(f"Event created: {event.get('id')}")
            
            return EventCreationResult(
                success=True,
                event_id=event.get('id'),
                event_link=event.get('htmlLink'),
                event_details=event,
            )
        
        except HttpError as e:
            logger.error(f"HTTP error creating event: {e}")
            return EventCreationResult(
                success=False,
                error=f"Google Calendar API error: {e.resp.status}"
            )
        
        except Exception as e:
            logger.error(f"Error creating event: {e}")
            return EventCreationResult(
                success=False,
                error=str(e)
            )
    
    async def search_events(
        self,
        query: Optional[str] = None,
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search calendar events.
        
        Args:
            query: Search query
            time_min: Minimum time filter
            time_max: Maximum time filter
            max_results: Maximum number of results
            
        Returns:
            List of events
        """
        try:
            self._ensure_service()
            
            # Default time range: next 30 days
            if not time_min:
                time_min = datetime.now()
            if not time_max:
                time_max = time_min + timedelta(days=30)
            
            # Build request
            request_params = {
                'calendarId': 'primary',
                'timeMin': time_min.isoformat() + 'Z',
                'timeMax': time_max.isoformat() + 'Z',
                'maxResults': max_results,
                'singleEvents': True,
                'orderBy': 'startTime',
            }
            
            if query:
                request_params['q'] = query
            
            # Execute search
            events_result = self.service.events().list(**request_params).execute()
            events = events_result.get('items', [])
            
            logger.info(f"Found {len(events)} events")
            return events
        
        except Exception as e:
            logger.error(f"Error searching events: {e}")
            return []
    
    async def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific event by ID.
        
        Args:
            event_id: Event ID
            
        Returns:
            Event dict or None
        """
        try:
            self._ensure_service()
            event = self.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            return event
        
        except Exception as e:
            logger.error(f"Error getting event: {e}")
            return None
    
    async def update_event(
        self,
        event_id: str,
        **updates
    ) -> EventCreationResult:
        """
        Update an existing event.
        
        Args:
            event_id: Event ID to update
            **updates: Fields to update
            
        Returns:
            EventCreationResult
        """
        try:
            self._ensure_service()
            
            # Get existing event
            event = await self.get_event(event_id)
            if not event:
                return EventCreationResult(
                    success=False,
                    error="Event not found"
                )
            
            # Update fields
            event.update(updates)
            
            # Update event
            updated_event = self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()
            
            logger.info(f"Event updated: {event_id}")
            
            return EventCreationResult(
                success=True,
                event_id=updated_event.get('id'),
                event_link=updated_event.get('htmlLink'),
                event_details=updated_event,
            )
        
        except Exception as e:
            logger.error(f"Error updating event: {e}")
            return EventCreationResult(
                success=False,
                error=str(e)
            )
    
    async def delete_event(self, event_id: str) -> bool:
        """
        Delete an event.
        
        Args:
            event_id: Event ID to delete
            
        Returns:
            True if successful
        """
        try:
            self._ensure_service()
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            logger.info(f"Event deleted: {event_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting event: {e}")
            return False


# Global service instance
calendar_service = GoogleCalendarService()
