"""Tests for calendar agent."""

import pytest
from app.agent.calendar_agent import calendar_agent
from app.agent.tools import parse_natural_datetime
from datetime import datetime


class TestCalendarAgent:
    """Test suite for CalendarAgent."""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test agent initialization."""
        calendar_agent.initialize()
        assert calendar_agent._initialized is True
        assert calendar_agent.llm is not None
        assert calendar_agent.agent_executor is not None
    
    @pytest.mark.asyncio
    async def test_process_simple_message(self, mock_session_id, mock_user_id):
        """Test processing a simple message."""
        calendar_agent.initialize()
        
        result = await calendar_agent.process_message(
            message="안녕하세요",
            session_id=mock_session_id,
            user_id=mock_user_id,
        )
        
        assert result["success"] is True
        assert "response" in result
        assert result["session_id"] == mock_session_id
    
    @pytest.mark.asyncio
    async def test_parse_natural_datetime_tomorrow(self):
        """Test parsing 'tomorrow' in Korean."""
        result = parse_natural_datetime("내일 오후 3시")
        
        assert result["success"] is True
        assert result["start_time"] is not None
        assert result["end_time"] is not None
    
    @pytest.mark.asyncio
    async def test_parse_natural_datetime_today(self):
        """Test parsing 'today' in Korean."""
        result = parse_natural_datetime("오늘 오전 9시")
        
        assert result["success"] is True
        assert result["start_time"] is not None


class TestAgentMemory:
    """Test suite for agent memory."""
    
    @pytest.mark.asyncio
    async def test_memory_persistence(self, mock_session_id):
        """Test that messages are stored in memory."""
        from app.agent.memory import memory_manager
        
        await memory_manager.add_message(mock_session_id, "Test message", is_user=True)
        await memory_manager.add_message(mock_session_id, "Test response", is_user=False)
        
        history = await memory_manager.get_history(mock_session_id)
        
        assert len(history) >= 2
    
    @pytest.mark.asyncio
    async def test_clear_memory(self, mock_session_id):
        """Test clearing conversation memory."""
        from app.agent.memory import memory_manager
        
        await memory_manager.add_message(mock_session_id, "Test", is_user=True)
        await memory_manager.clear_history(mock_session_id)
        
        history = await memory_manager.get_history(mock_session_id)
        assert len(history) == 0
