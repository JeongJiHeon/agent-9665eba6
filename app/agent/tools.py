"""LangChain tools for calendar operations"""

import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from app.services.google_calendar import GoogleCalendarService


class CreateEventInput(BaseModel):
    """Input schema for create_calendar_event tool"""
    title: str = Field(description="이벤트 제목")
    start_time: str = Field(description="시작 시간 (ISO 8601 형식: YYYY-MM-DD HH:MM:SS)")
    end_time: str = Field(description="종료 시간 (ISO 8601 형식: YYYY-MM-DD HH:MM:SS)")
    description: Optional[str] = Field(None, description="이벤트 설명")
    location: Optional[str] = Field(None, description="장소")
    attendees: Optional[List[str]] = Field(None, description="참석자 이메일 리스트")


class UpdateEventInput(BaseModel):
    """Input schema for update_calendar_event tool"""
    event_id: str = Field(description="업데이트할 이벤트 ID")
    title: Optional[str] = Field(None, description="새 제목")
    start_time: Optional[str] = Field(None, description="새 시작 시간")
    end_time: Optional[str] = Field(None, description="새 종료 시간")
    description: Optional[str] = Field(None, description="새 설명")
    location: Optional[str] = Field(None, description="새 장소")


class DeleteEventInput(BaseModel):
    """Input schema for delete_calendar_event tool"""
    event_id: str = Field(description="삭제할 이벤트 ID")


class ListEventsInput(BaseModel):
    """Input schema for list_calendar_events tool"""
    max_results: int = Field(10, description="최대 결과 개수")
    days_ahead: int = Field(7, description="몇 일 앞까지 조회할지")


class CreateCalendarEventTool(BaseTool):
    """Tool for creating calendar events"""
    
    name: str = "create_calendar_event"
    description: str = """구글 캘린더에 새 이벤트를 생성합니다.
    필수: title, start_time, end_time
    선택: description, location, attendees
    시간 형식: YYYY-MM-DD HH:MM:SS"""
    args_schema: type[BaseModel] = CreateEventInput
    calendar_service: GoogleCalendarService
    
    def __init__(self, calendar_service: GoogleCalendarService):
        super().__init__(calendar_service=calendar_service)
    
    def _run(
        self,
        title: str,
        start_time: str,
        end_time: str,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None
    ) -> str:
        """Create a calendar event"""
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            event = self.calendar_service.create_event(
                title=title,
                start_time=start_dt,
                end_time=end_dt,
                description=description,
                location=location,
                attendees=attendees,
                timezone='Asia/Seoul'
            )
            
            return f"✅ 일정이 성공적으로 생성되었습니다!\n\n" \
                   f"제목: {title}\n" \
                   f"시작: {start_time}\n" \
                   f"종료: {end_time}\n" \
                   f"이벤트 ID: {event['id']}"
        except Exception as e:
            return f"❌ 일정 생성 중 오류가 발생했습니다: {str(e)}"
    
    async def _arun(self, *args, **kwargs) -> str:
        """Async version"""
        return self._run(*args, **kwargs)


class ListCalendarEventsTool(BaseTool):
    """Tool for listing calendar events"""
    
    name: str = "list_calendar_events"
    description: str = "구글 캘린더의 예정된 이벤트 목록을 조회합니다."
    args_schema: type[BaseModel] = ListEventsInput
    calendar_service: GoogleCalendarService
    
    def __init__(self, calendar_service: GoogleCalendarService):
        super().__init__(calendar_service=calendar_service)
    
    def _run(self, max_results: int = 10, days_ahead: int = 7) -> str:
        """List calendar events"""
        try:
            time_min = datetime.utcnow()
            time_max = time_min + timedelta(days=days_ahead)
            
            events = self.calendar_service.list_events(
                max_results=max_results,
                time_min=time_min,
                time_max=time_max
            )
            
            if not events:
                return "📅 예정된 일정이 없습니다."
            
            result = f"📅 다가오는 일정 ({len(events)}개):\n\n"
            for i, event in enumerate(events, 1):
                start = event['start'].get('dateTime', event['start'].get('date'))
                result += f"{i}. {event['summary']}\n"
                result += f"   시작: {start}\n"
                result += f"   ID: {event['id']}\n\n"
            
            return result
        except Exception as e:
            return f"❌ 일정 조회 중 오류가 발생했습니다: {str(e)}"
    
    async def _arun(self, *args, **kwargs) -> str:
        """Async version"""
        return self._run(*args, **kwargs)


class UpdateCalendarEventTool(BaseTool):
    """Tool for updating calendar events"""
    
    name: str = "update_calendar_event"
    description: str = "기존 캘린더 이벤트를 수정합니다."
    args_schema: type[BaseModel] = UpdateEventInput
    calendar_service: GoogleCalendarService
    
    def __init__(self, calendar_service: GoogleCalendarService):
        super().__init__(calendar_service=calendar_service)
    
    def _run(
        self,
        event_id: str,
        title: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None
    ) -> str:
        """Update a calendar event"""
        try:
            start_dt = datetime.fromisoformat(start_time) if start_time else None
            end_dt = datetime.fromisoformat(end_time) if end_time else None
            
            event = self.calendar_service.update_event(
                event_id=event_id,
                title=title,
                start_time=start_dt,
                end_time=end_dt,
                description=description,
                location=location,
                timezone='Asia/Seoul'
            )
            
            return f"✅ 일정이 성공적으로 수정되었습니다!\n이벤트 ID: {event['id']}"
        except Exception as e:
            return f"❌ 일정 수정 중 오류가 발생했습니다: {str(e)}"
    
    async def _arun(self, *args, **kwargs) -> str:
        """Async version"""
        return self._run(*args, **kwargs)


class DeleteCalendarEventTool(BaseTool):
    """Tool for deleting calendar events"""
    
    name: str = "delete_calendar_event"
    description: str = "캘린더 이벤트를 삭제합니다."
    args_schema: type[BaseModel] = DeleteEventInput
    calendar_service: GoogleCalendarService
    
    def __init__(self, calendar_service: GoogleCalendarService):
        super().__init__(calendar_service=calendar_service)
    
    def _run(self, event_id: str) -> str:
        """Delete a calendar event"""
        try:
            self.calendar_service.delete_event(event_id)
            return f"✅ 일정이 성공적으로 삭제되었습니다!\n이벤트 ID: {event_id}"
        except Exception as e:
            return f"❌ 일정 삭제 중 오류가 발생했습니다: {str(e)}"
    
    async def _arun(self, *args, **kwargs) -> str:
        """Async version"""
        return self._run(*args, **kwargs)


def get_calendar_tools(calendar_service: GoogleCalendarService) -> List[BaseTool]:
    """Get all calendar tools"""
    return [
        CreateCalendarEventTool(calendar_service=calendar_service),
        ListCalendarEventsTool(calendar_service=calendar_service),
        UpdateCalendarEventTool(calendar_service=calendar_service),
        DeleteCalendarEventTool(calendar_service=calendar_service),
    ]
