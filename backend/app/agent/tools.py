"""LangChain tools for the calendar agent."""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from langchain.tools import Tool, StructuredTool
from langchain.pydantic_v1 import BaseModel, Field
from loguru import logger
import re
from dateutil import parser as date_parser

from app.services.google_calendar import calendar_service
from app.services.vector_store import vector_store_service


class CreateEventInput(BaseModel):
    """Input schema for create_calendar_event tool."""
    summary: str = Field(..., description="이벤트 제목")
    start_time: str = Field(..., description="시작 시간 (ISO 8601 형식 또는 'YYYY-MM-DD HH:MM')")
    end_time: str = Field(..., description="종료 시간 (ISO 8601 형식 또는 'YYYY-MM-DD HH:MM')")
    description: Optional[str] = Field(None, description="이벤트 설명")
    location: Optional[str] = Field(None, description="이벤트 장소")
    attendees: Optional[List[str]] = Field(default_factory=list, description="참석자 이메일 목록")


class SearchEventsInput(BaseModel):
    """Input schema for search_calendar_events tool."""
    query: str = Field(..., description="검색 쿼리")
    time_min: Optional[str] = Field(None, description="검색 시작 날짜")
    time_max: Optional[str] = Field(None, description="검색 종료 날짜")
    max_results: int = Field(10, description="최대 결과 수")


class ParseDateTimeInput(BaseModel):
    """Input schema for parse_datetime tool."""
    text: str = Field(..., description="파싱할 자연어 텍스트")
    reference_date: Optional[str] = Field(None, description="기준 날짜 (기본: 현재)")


def parse_natural_datetime(text: str, reference_date: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Parse natural language datetime expressions.
    
    Examples:
    - "내일 오후 3시"
    - "다음주 월요일 10시"
    - "12월 25일 오전 9시"
    """
    if reference_date is None:
        reference_date = datetime.now()
    
    result = {
        "start_time": None,
        "end_time": None,
        "success": False,
        "error": None
    }
    
    text = text.lower().strip()
    
    try:
        # Simple patterns
        if "내일" in text:
            base_date = reference_date + timedelta(days=1)
        elif "모레" in text:
            base_date = reference_date + timedelta(days=2)
        elif "오늘" in text:
            base_date = reference_date
        else:
            # Try to parse with dateutil
            try:
                base_date = date_parser.parse(text, fuzzy=True)
            except:
                base_date = reference_date
        
        # Extract time
        hour = 9  # Default hour
        minute = 0
        
        # Pattern: "오전/오후 숫자시"
        time_pattern = r'(오전|오후|am|pm)?\s*(\d{1,2})\s*시?\s*(\d{1,2})?\s*분?'
        time_match = re.search(time_pattern, text)
        
        if time_match:
            period = time_match.group(1)
            hour = int(time_match.group(2))
            minute = int(time_match.group(3)) if time_match.group(3) else 0
            
            if period in ["오후", "pm"] and hour < 12:
                hour += 12
            elif period in ["오전", "am"] and hour == 12:
                hour = 0
        
        # Construct start_time
        start_time = base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Default duration: 1 hour
        end_time = start_time + timedelta(hours=1)
        
        result["start_time"] = start_time.isoformat()
        result["end_time"] = end_time.isoformat()
        result["success"] = True
        
    except Exception as e:
        logger.error(f"Failed to parse datetime: {e}")
        result["error"] = str(e)
    
    return result


async def create_calendar_event_tool(
    summary: str,
    start_time: str,
    end_time: str,
    description: Optional[str] = None,
    location: Optional[str] = None,
    attendees: Optional[List[str]] = None,
) -> str:
    """구글 캘린더에 이벤트를 생성합니다."""
    try:
        # Parse datetime strings
        start_dt = date_parser.parse(start_time)
        end_dt = date_parser.parse(end_time)
        
        # Create event
        result = await calendar_service.create_event(
            summary=summary,
            start_time=start_dt,
            end_time=end_dt,
            description=description,
            location=location,
            attendees=attendees or []
        )
        
        if result.success:
            # Store in vector database for RAG
            event_text = f"{summary} {description or ''} {location or ''}"
            await vector_store_service.add_event(
                event_id=result.event_id,
                text=event_text,
                metadata={
                    "summary": summary,
                    "start_time": start_time,
                    "end_time": end_time,
                    "location": location,
                }
            )
            
            return f"✅ 일정이 생성되었습니다!\n제목: {summary}\n시작: {start_time}\n종료: {end_time}\n링크: {result.event_link}"
        else:
            return f"❌ 일정 생성 실패: {result.error}"
    
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        return f"❌ 오류 발생: {str(e)}"


async def search_calendar_events_tool(
    query: str,
    time_min: Optional[str] = None,
    time_max: Optional[str] = None,
    max_results: int = 10
) -> str:
    """구글 캘린더에서 이벤트를 검색합니다."""
    try:
        time_min_dt = date_parser.parse(time_min) if time_min else datetime.now()
        time_max_dt = date_parser.parse(time_max) if time_max else None
        
        events = await calendar_service.search_events(
            query=query,
            time_min=time_min_dt,
            time_max=time_max_dt,
            max_results=max_results
        )
        
        if not events:
            return "검색 결과가 없습니다."
        
        result = f"📅 {len(events)}개의 일정을 찾았습니다:\n\n"
        for event in events:
            result += f"• {event.get('summary', 'No title')}\n"
            result += f"  시작: {event.get('start', {}).get('dateTime', 'N/A')}\n"
            result += f"  종료: {event.get('end', {}).get('dateTime', 'N/A')}\n\n"
        
        return result
    
    except Exception as e:
        logger.error(f"Error searching events: {e}")
        return f"❌ 검색 오류: {str(e)}"


async def parse_datetime_tool(text: str, reference_date: Optional[str] = None) -> str:
    """자연어를 날짜/시간으로 변환합니다."""
    try:
        ref_date = date_parser.parse(reference_date) if reference_date else None
        result = parse_natural_datetime(text, ref_date)
        
        if result["success"]:
            return f"시작: {result['start_time']}\n종료: {result['end_time']}"
        else:
            return f"❌ 날짜 파싱 실패: {result.get('error', 'Unknown error')}"
    
    except Exception as e:
        logger.error(f"Error parsing datetime: {e}")
        return f"❌ 오류: {str(e)}"


async def search_similar_events_tool(query: str, top_k: int = 5) -> str:
    """과거 유사한 이벤트를 검색합니다 (RAG)."""
    try:
        results = await vector_store_service.search_similar(query, top_k=top_k)
        
        if not results:
            return "유사한 이벤트를 찾을 수 없습니다."
        
        response = f"🔍 유사한 과거 이벤트 {len(results)}개:\n\n"
        for i, result in enumerate(results, 1):
            metadata = result.get("metadata", {})
            response += f"{i}. {metadata.get('summary', 'N/A')}\n"
            response += f"   시간: {metadata.get('start_time', 'N/A')}\n"
            if metadata.get('location'):
                response += f"   장소: {metadata['location']}\n"
            response += "\n"
        
        return response
    
    except Exception as e:
        logger.error(f"Error searching similar events: {e}")
        return f"❌ 검색 오류: {str(e)}"


# Define tools
def get_calendar_tools() -> List[Tool]:
    """Get all calendar-related tools."""
    
    return [
        StructuredTool.from_function(
            coroutine=create_calendar_event_tool,
            name="create_calendar_event",
            description="구글 캘린더에 새 이벤트를 생성합니다. 제목, 시작시간, 종료시간이 필요합니다.",
            args_schema=CreateEventInput,
        ),
        StructuredTool.from_function(
            coroutine=search_calendar_events_tool,
            name="search_calendar_events",
            description="구글 캘린더에서 이벤트를 검색합니다.",
            args_schema=SearchEventsInput,
        ),
        StructuredTool.from_function(
            coroutine=parse_datetime_tool,
            name="parse_datetime",
            description="자연어로 표현된 날짜/시간을 ISO 형식으로 변환합니다.",
            args_schema=ParseDateTimeInput,
        ),
        StructuredTool.from_function(
            coroutine=search_similar_events_tool,
            name="search_similar_events",
            description="벡터 검색을 사용하여 유사한 과거 이벤트를 찾습니다.",
        ),
    ]
