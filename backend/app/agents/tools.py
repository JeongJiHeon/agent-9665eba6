"""
Custom tools for the LangChain calendar agent.
"""
from langchain.tools import BaseTool
from typing import Optional, Type, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import json
from loguru import logger


class CreateEventInput(BaseModel):
    """Input schema for creating calendar events."""
    summary: str = Field(description="제목 또는 이벤트 요약")
    start_time: str = Field(description="시작 시간 (ISO 8601 형식: YYYY-MM-DDTHH:MM:SS)")
    end_time: str = Field(description="종료 시간 (ISO 8601 형식: YYYY-MM-DDTHH:MM:SS)")
    description: Optional[str] = Field(default=None, description="이벤트 설명 (선택사항)")
    location: Optional[str] = Field(default=None, description="위치 (선택사항)")


class ListEventsInput(BaseModel):
    """Input schema for listing calendar events."""
    time_min: Optional[str] = Field(default=None, description="검색 시작 시간 (ISO 8601 형식)")
    time_max: Optional[str] = Field(default=None, description="검색 종료 시간 (ISO 8601 형식)")
    max_results: int = Field(default=10, description="최대 결과 수")


class UpdateEventInput(BaseModel):
    """Input schema for updating calendar events."""
    event_id: str = Field(description="업데이트할 이벤트 ID")
    summary: Optional[str] = Field(default=None, description="새 제목")
    start_time: Optional[str] = Field(default=None, description="새 시작 시간")
    end_time: Optional[str] = Field(default=None, description="새 종료 시간")
    description: Optional[str] = Field(default=None, description="새 설명")
    location: Optional[str] = Field(default=None, description="새 위치")


class DeleteEventInput(BaseModel):
    """Input schema for deleting calendar events."""
    event_id: str = Field(description="삭제할 이벤트 ID")


class CreateCalendarEventTool(BaseTool):
    """Tool for creating Google Calendar events."""
    
    name: str = "create_calendar_event"
    description: str = """
    구글 캘린더에 새 이벤트를 생성합니다.
    사용자가 일정을 추가하고 싶을 때 사용하세요.
    입력: summary (제목), start_time (시작시간), end_time (종료시간), description (설명), location (위치)
    시간은 ISO 8601 형식이어야 합니다 (예: 2024-01-15T14:00:00).
    """
    args_schema: Type[BaseModel] = CreateEventInput
    calendar_service: Any = None
    
    def __init__(self, calendar_service):
        super().__init__()
        self.calendar_service = calendar_service
    
    def _run(
        self,
        summary: str,
        start_time: str,
        end_time: str,
        description: Optional[str] = None,
        location: Optional[str] = None,
    ) -> str:
        """Create a calendar event."""
        try:
            event_data = {
                "summary": summary,
                "start": start_time,
                "end": end_time,
            }
            if description:
                event_data["description"] = description
            if location:
                event_data["location"] = location
            
            result = self.calendar_service.create_event(event_data)
            logger.info(f"Created event: {result}")
            
            return f"이벤트가 성공적으로 생성되었습니다: '{summary}' ({start_time} ~ {end_time})"
        except Exception as e:
            logger.error(f"Error creating event: {e}")
            return f"이벤트 생성 중 오류가 발생했습니다: {str(e)}"
    
    async def _arun(self, *args, **kwargs) -> str:
        """Async version."""
        return self._run(*args, **kwargs)


class ListCalendarEventsTool(BaseTool):
    """Tool for listing Google Calendar events."""
    
    name: str = "list_calendar_events"
    description: str = """
    구글 캘린더의 이벤트 목록을 조회합니다.
    사용자가 일정을 확인하고 싶을 때 사용하세요.
    입력: time_min (시작시간), time_max (종료시간), max_results (최대 결과 수)
    """
    args_schema: Type[BaseModel] = ListEventsInput
    calendar_service: Any = None
    
    def __init__(self, calendar_service):
        super().__init__()
        self.calendar_service = calendar_service
    
    def _run(
        self,
        time_min: Optional[str] = None,
        time_max: Optional[str] = None,
        max_results: int = 10,
    ) -> str:
        """List calendar events."""
        try:
            events = self.calendar_service.list_events(
                time_min=time_min,
                time_max=time_max,
                max_results=max_results
            )
            
            if not events:
                return "해당 기간에 일정이 없습니다."
            
            result = "일정 목록:\n"
            for event in events:
                start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date', ''))
                summary = event.get('summary', '제목 없음')
                event_id = event.get('id', '')
                result += f"- {summary} (시작: {start}) [ID: {event_id}]\n"
            
            return result
        except Exception as e:
            logger.error(f"Error listing events: {e}")
            return f"이벤트 조회 중 오류가 발생했습니다: {str(e)}"
    
    async def _arun(self, *args, **kwargs) -> str:
        """Async version."""
        return self._run(*args, **kwargs)


class UpdateCalendarEventTool(BaseTool):
    """Tool for updating Google Calendar events."""
    
    name: str = "update_calendar_event"
    description: str = """
    구글 캘린더의 기존 이벤트를 수정합니다.
    사용자가 일정을 변경하고 싶을 때 사용하세요.
    입력: event_id (이벤트 ID), summary (제목), start_time (시작시간), end_time (종료시간), description (설명), location (위치)
    """
    args_schema: Type[BaseModel] = UpdateEventInput
    calendar_service: Any = None
    
    def __init__(self, calendar_service):
        super().__init__()
        self.calendar_service = calendar_service
    
    def _run(
        self,
        event_id: str,
        summary: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
    ) -> str:
        """Update a calendar event."""
        try:
            updates = {}
            if summary:
                updates["summary"] = summary
            if start_time:
                updates["start"] = start_time
            if end_time:
                updates["end"] = end_time
            if description:
                updates["description"] = description
            if location:
                updates["location"] = location
            
            result = self.calendar_service.update_event(event_id, updates)
            logger.info(f"Updated event: {result}")
            
            return f"이벤트가 성공적으로 수정되었습니다 (ID: {event_id})"
        except Exception as e:
            logger.error(f"Error updating event: {e}")
            return f"이벤트 수정 중 오류가 발생했습니다: {str(e)}"
    
    async def _arun(self, *args, **kwargs) -> str:
        """Async version."""
        return self._run(*args, **kwargs)


class DeleteCalendarEventTool(BaseTool):
    """Tool for deleting Google Calendar events."""
    
    name: str = "delete_calendar_event"
    description: str = """
    구글 캘린더의 이벤트를 삭제합니다.
    사용자가 일정을 취소하고 싶을 때 사용하세요.
    입력: event_id (삭제할 이벤트 ID)
    """
    args_schema: Type[BaseModel] = DeleteEventInput
    calendar_service: Any = None
    
    def __init__(self, calendar_service):
        super().__init__()
        self.calendar_service = calendar_service
    
    def _run(self, event_id: str) -> str:
        """Delete a calendar event."""
        try:
            self.calendar_service.delete_event(event_id)
            logger.info(f"Deleted event: {event_id}")
            
            return f"이벤트가 성공적으로 삭제되었습니다 (ID: {event_id})"
        except Exception as e:
            logger.error(f"Error deleting event: {e}")
            return f"이벤트 삭제 중 오류가 발생했습니다: {str(e)}"
    
    async def _arun(self, *args, **kwargs) -> str:
        """Async version."""
        return self._run(*args, **kwargs)


class ParseNaturalLanguageDateTool(BaseTool):
    """Tool for parsing natural language dates to ISO format."""
    
    name: str = "parse_date"
    description: str = """
    자연어 날짜를 ISO 8601 형식으로 변환합니다.
    예: "내일 오후 3시" -> "2024-01-16T15:00:00"
    """
    
    def _run(self, natural_language: str) -> str:
        """Parse natural language date."""
        try:
            # Simple parsing logic - in production, use a library like dateparser
            now = datetime.now()
            
            # Handle common Korean date expressions
            if "오늘" in natural_language or "today" in natural_language.lower():
                date = now
            elif "내일" in natural_language or "tomorrow" in natural_language.lower():
                date = now + timedelta(days=1)
            elif "모레" in natural_language:
                date = now + timedelta(days=2)
            else:
                # Default to now if can't parse
                date = now
            
            # Parse time if present
            hour = 9  # default morning
            if "오전" in natural_language or "am" in natural_language.lower():
                hour = 9
            elif "오후" in natural_language or "pm" in natural_language.lower():
                hour = 14
            elif "저녁" in natural_language or "evening" in natural_language.lower():
                hour = 18
            
            # Try to extract hour
            import re
            hour_match = re.search(r'(\d+)시', natural_language)
            if hour_match:
                parsed_hour = int(hour_match.group(1))
                if "오후" in natural_language and parsed_hour < 12:
                    hour = parsed_hour + 12
                else:
                    hour = parsed_hour
            
            result = date.replace(hour=hour, minute=0, second=0, microsecond=0)
            return result.isoformat()
        except Exception as e:
            logger.error(f"Error parsing date: {e}")
            # Return current time as fallback
            return datetime.now().isoformat()
    
    async def _arun(self, *args, **kwargs) -> str:
        """Async version."""
        return self._run(*args, **kwargs)
