"""Pytest configuration and fixtures."""

import pytest
import asyncio
from typing import Generator
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_session_id() -> str:
    """Mock session ID for testing."""
    return "test_session_123"


@pytest.fixture
def mock_user_id() -> str:
    """Mock user ID for testing."""
    return "test_user"


@pytest.fixture
def sample_event_data():
    """Sample event data for testing."""
    return {
        "summary": "팀 미팅",
        "description": "주간 팀 회의",
        "start_time": "2025-10-30T10:00:00",
        "end_time": "2025-10-30T11:00:00",
        "location": "회의실 A",
        "attendees": ["test@example.com"],
    }
