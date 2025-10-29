"""
Pytest configuration and fixtures.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, MagicMock

from app.main import app
from app.services.calendar_service import GoogleCalendarService


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


@pytest.fixture
def mock_calendar_service():
    """Mock calendar service fixture."""
    service = Mock(spec=GoogleCalendarService)
    service.is_authenticated.return_value = True
    service.create_event.return_value = {
        "id": "test_event_id",
        "summary": "Test Event",
        "start": {"dateTime": "2024-01-15T14:00:00"},
        "end": {"dateTime": "2024-01-15T15:00:00"}
    }
    service.list_events.return_value = [
        {
            "id": "event1",
            "summary": "Event 1",
            "start": {"dateTime": "2024-01-15T14:00:00"}
        }
    ]
    return service


@pytest.fixture
def mock_agent():
    """Mock agent fixture."""
    agent = MagicMock()
    agent.process_message.return_value = {
        "success": True,
        "message": "Test response",
        "intermediate_steps": []
    }
    return agent
