"""Tests for Google Calendar service."""

import pytest
from datetime import datetime, timedelta
from app.services.google_calendar import calendar_service
from app.models import EventCreationResult


class TestGoogleCalendarService:
    """Test suite for Google Calendar service."""
    
    def test_service_initialization(self):
        """Test service initialization."""
        assert calendar_service is not None
    
    @pytest.mark.asyncio
    async def test_create_event_structure(self, sample_event_data):
        """Test event creation structure (without actual API call)."""
        # This test would require mocking Google Calendar API
        # For now, we test the data structure
        
        assert "summary" in sample_event_data
        assert "start_time" in sample_event_data
        assert "end_time" in sample_event_data
    
    def test_event_creation_result_model(self):
        """Test EventCreationResult model."""
        result = EventCreationResult(
            success=True,
            event_id="test_123",
            event_link="https://calendar.google.com/event?eid=test_123",
        )
        
        assert result.success is True
        assert result.event_id == "test_123"
        assert result.event_link is not None


class TestVectorStore:
    """Test suite for vector store service."""
    
    @pytest.mark.asyncio
    async def test_vector_store_initialization(self):
        """Test vector store initialization."""
        from app.services.vector_store import vector_store_service
        
        await vector_store_service.initialize()
        assert vector_store_service.is_initialized is True
    
    @pytest.mark.asyncio
    async def test_add_and_search_event(self):
        """Test adding and searching events in vector store."""
        from app.services.vector_store import vector_store_service
        
        await vector_store_service.initialize()
        
        # Add test event
        await vector_store_service.add_event(
            event_id="test_event_1",
            text="팀 미팅 주간 회의",
            metadata={"summary": "팀 미팅", "location": "회의실 A"}
        )
        
        # Search for similar
        results = await vector_store_service.search_similar(
            query="미팅",
            top_k=5
        )
        
        assert len(results) > 0
    
    @pytest.mark.asyncio
    async def test_get_collection_stats(self):
        """Test getting collection statistics."""
        from app.services.vector_store import vector_store_service
        
        await vector_store_service.initialize()
        stats = await vector_store_service.get_collection_stats()
        
        assert "total_documents" in stats
        assert "is_initialized" in stats
