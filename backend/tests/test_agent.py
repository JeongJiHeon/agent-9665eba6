"""
Agent tests.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch

from app.agents.calendar_agent import CalendarAgent, AgentManager
from app.agents.tools import (
    CreateCalendarEventTool,
    ListCalendarEventsTool,
    ParseNaturalLanguageDateTool
)


class TestCalendarAgent:
    """Test CalendarAgent class."""
    
    @patch('app.agents.calendar_agent.ChatOpenAI')
    def test_agent_initialization(self, mock_llm):
        """Test agent initialization."""
        mock_service = Mock()
        mock_service.is_authenticated.return_value = True
        
        agent = CalendarAgent(mock_service, "test_user")
        
        assert agent.user_id == "test_user"
        assert agent.calendar_service == mock_service
        assert len(agent.tools) > 0
        assert agent.memory is not None
    
    @patch('app.agents.calendar_agent.ChatOpenAI')
    async def test_process_message(self, mock_llm):
        """Test message processing."""
        mock_service = Mock()
        mock_service.is_authenticated.return_value = True
        
        agent = CalendarAgent(mock_service, "test_user")
        
        # Mock agent executor
        with patch.object(agent.agent_executor, 'ainvoke') as mock_invoke:
            mock_invoke.return_value = {
                "output": "이벤트가 생성되었습니다.",
                "intermediate_steps": []
            }
            
            response = await agent.process_message("내일 회의 일정 추가해줘")
            
            assert response["success"] is True
            assert "이벤트" in response["message"]
    
    @patch('app.agents.calendar_agent.ChatOpenAI')
    def test_conversation_history(self, mock_llm):
        """Test conversation history management."""
        mock_service = Mock()
        mock_service.is_authenticated.return_value = True
        
        agent = CalendarAgent(mock_service, "test_user")
        
        # Initially empty
        history = agent.get_conversation_history()
        assert len(history) == 0
        
        # Clear history
        agent.clear_conversation_history()
        history = agent.get_conversation_history()
        assert len(history) == 0


class TestAgentManager:
    """Test AgentManager class."""
    
    @patch('app.agents.calendar_agent.CalendarAgent')
    def test_get_agent(self, mock_agent_class):
        """Test getting agent from manager."""
        manager = AgentManager()
        mock_service = Mock()
        
        agent1 = manager.get_agent("user1", mock_service)
        agent2 = manager.get_agent("user1", mock_service)
        
        # Should return same instance
        assert agent1 is agent2
        
        agent3 = manager.get_agent("user2", mock_service)
        # Different user should get different agent
        assert agent1 is not agent3
    
    def test_remove_agent(self):
        """Test removing agent from manager."""
        manager = AgentManager()
        mock_service = Mock()
        
        manager.get_agent("user1", mock_service)
        assert "user1" in manager.agents
        
        manager.remove_agent("user1")
        assert "user1" not in manager.agents


class TestAgentTools:
    """Test agent tools."""
    
    def test_create_event_tool(self):
        """Test CreateCalendarEventTool."""
        mock_service = Mock()
        mock_service.create_event.return_value = {
            "id": "test_id",
            "summary": "Test Event"
        }
        
        tool = CreateCalendarEventTool(mock_service)
        result = tool._run(
            summary="Test Event",
            start_time="2024-01-15T14:00:00",
            end_time="2024-01-15T15:00:00"
        )
        
        assert "성공적으로 생성" in result
        mock_service.create_event.assert_called_once()
    
    def test_list_events_tool(self):
        """Test ListCalendarEventsTool."""
        mock_service = Mock()
        mock_service.list_events.return_value = [
            {
                "id": "event1",
                "summary": "Event 1",
                "start": {"dateTime": "2024-01-15T14:00:00"}
            }
        ]
        
        tool = ListCalendarEventsTool(mock_service)
        result = tool._run(max_results=10)
        
        assert "Event 1" in result
        mock_service.list_events.assert_called_once()
    
    def test_parse_date_tool(self):
        """Test ParseNaturalLanguageDateTool."""
        tool = ParseNaturalLanguageDateTool()
        
        result = tool._run("오늘 오후 3시")
        assert "T" in result  # ISO format
        
        result = tool._run("내일 오전 9시")
        assert "T" in result
