"""Test AI agent functionality"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from app.agent.calendar_agent import CalendarAgent
from app.agent.tools import CreateCalendarEventTool
from app.services.google_calendar import GoogleCalendarService


@pytest.fixture
def mock_calendar_service():
    """Mock Google Calendar service"""
    service = Mock(spec=GoogleCalendarService)
    service.create_event.return_value = {
        'id': 'test_event_123',
        'summary': 'Test Event',
        'start': {'dateTime': '2024-01-01T10:00:00Z'},
        'end': {'dateTime': '2024-01-01T11:00:00Z'}
    }
    return service


def test_create_event_tool(mock_calendar_service):
    """Test calendar event creation tool"""
    tool = CreateCalendarEventTool(calendar_service=mock_calendar_service)
    
    result = tool._run(
        title="Test Meeting",
        start_time="2024-01-01 10:00:00",
        end_time="2024-01-01 11:00:00",
        description="Test description"
    )
    
    assert "성공적으로 생성되었습니다" in result
    mock_calendar_service.create_event.assert_called_once()


def test_create_event_tool_error(mock_calendar_service):
    """Test calendar event creation tool error handling"""
    mock_calendar_service.create_event.side_effect = Exception("API Error")
    
    tool = CreateCalendarEventTool(calendar_service=mock_calendar_service)
    
    result = tool._run(
        title="Test Meeting",
        start_time="2024-01-01 10:00:00",
        end_time="2024-01-01 11:00:00"
    )
    
    assert "오류가 발생했습니다" in result


@patch('app.agent.calendar_agent.ChatOpenAI')
def test_agent_initialization(mock_llm, db, test_user):
    """Test agent initialization"""
    # Add Google tokens to test user
    test_user.google_access_token = "test_token"
    test_user.google_refresh_token = "test_refresh"
    db.commit()
    
    with patch('app.agent.calendar_agent.GoogleCalendarService'):
        agent = CalendarAgent(db=db, user=test_user)
        
        assert agent.user == test_user
        assert agent.session_id is not None
        assert len(agent.tools) > 0


def test_chat_endpoint_without_google_auth(client, auth_headers):
    """Test chat endpoint without Google Calendar authentication"""
    response = client.post(
        "/api/v1/agent/chat",
        headers=auth_headers,
        json={
            "message": "내일 오후 3시 회의 일정 잡아줘"
        }
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Google Calendar" in response.json()["detail"]
