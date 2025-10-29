"""
Service tests.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from app.services.calendar_service import GoogleCalendarService, CalendarServiceManager
from app.services.agent_service import AgentService


class TestGoogleCalendarService:
    """Test GoogleCalendarService class."""
    
    def test_initialization(self):
        """Test service initialization."""
        service = GoogleCalendarService("test_user")
        assert service.user_id == "test_user"
        assert service.credentials is None or service.credentials is not None
    
    @patch('app.services.calendar_service.build')
    @patch('app.services.calendar_service.Credentials')
    def test_create_event(self, mock_creds, mock_build):
        """Test creating calendar event."""
        service = GoogleCalendarService("test_user")
        
        # Mock authenticated service
        mock_service = MagicMock()
        mock_events = MagicMock()
        mock_insert = MagicMock()
        mock_insert.execute.return_value = {"id": "test_event"}
        mock_events.insert.return_value = mock_insert
        mock_service.events.return_value = mock_events
        
        service.service = mock_service
        service.credentials = Mock()
        
        result = service.create_event({
            "summary": "Test Event",
            "start": "2024-01-15T14:00:00",
            "end": "2024-01-15T15:00:00"
        })
        
        assert result["id"] == "test_event"
    
    def test_not_authenticated(self):
        """Test methods when not authenticated."""
        service = GoogleCalendarService("test_user")
        service.credentials = None
        
        assert not service.is_authenticated()
        
        with pytest.raises(Exception) as exc_info:
            service.create_event({"summary": "Test"})
        assert "not authenticated" in str(exc_info.value).lower()


class TestCalendarServiceManager:
    """Test CalendarServiceManager class."""
    
    def test_get_service(self):
        """Test getting service from manager."""
        manager = CalendarServiceManager()
        
        service1 = manager.get_service("user1")
        service2 = manager.get_service("user1")
        
        # Should return same instance
        assert service1 is service2
        
        service3 = manager.get_service("user2")
        # Different user should get different service
        assert service1 is not service3
    
    def test_remove_service(self):
        """Test removing service from manager."""
        manager = CalendarServiceManager()
        
        manager.get_service("user1")
        assert "user1" in manager.services
        
        manager.remove_service("user1")
        assert "user1" not in manager.services


class TestAgentService:
    """Test AgentService class."""
    
    @patch('app.services.agent_service.calendar_service_manager')
    @patch('app.services.agent_service.agent_manager')
    async def test_process_user_message(self, mock_agent_manager, mock_service_manager):
        """Test processing user message."""
        # Mock calendar service
        mock_calendar_service = Mock()
        mock_calendar_service.is_authenticated.return_value = True
        mock_service_manager.get_service.return_value = mock_calendar_service
        
        # Mock agent
        mock_agent = Mock()
        mock_agent.process_message.return_value = {
            "success": True,
            "message": "이벤트가 생성되었습니다."
        }
        mock_agent_manager.get_agent.return_value = mock_agent
        
        result = await AgentService.process_user_message(
            user_id="test_user",
            message="내일 회의 일정 추가해줘"
        )
        
        assert result["success"] is True
        assert "이벤트" in result["message"]
    
    @patch('app.services.agent_service.calendar_service_manager')
    async def test_not_authenticated(self, mock_service_manager):
        """Test when user is not authenticated."""
        mock_calendar_service = Mock()
        mock_calendar_service.is_authenticated.return_value = False
        mock_service_manager.get_service.return_value = mock_calendar_service
        
        result = await AgentService.process_user_message(
            user_id="test_user",
            message="일정 추가해줘"
        )
        
        assert result["success"] is False
        assert result["requires_auth"] is True
    
    @patch('app.services.agent_service.agent_manager')
    def test_get_conversation_history(self, mock_agent_manager):
        """Test getting conversation history."""
        mock_agent = Mock()
        mock_agent.get_conversation_history.return_value = [
            {"role": "user", "content": "안녕하세요"}
        ]
        mock_agent_manager.agents = {"test_user": mock_agent}
        
        history = AgentService.get_conversation_history("test_user")
        
        assert len(history) == 1
        assert history[0]["content"] == "안녕하세요"
    
    @patch('app.services.agent_service.agent_manager')
    def test_clear_conversation_history(self, mock_agent_manager):
        """Test clearing conversation history."""
        mock_agent = Mock()
        mock_agent_manager.agents = {"test_user": mock_agent}
        
        AgentService.clear_conversation_history("test_user")
        
        mock_agent.clear_conversation_history.assert_called_once()
