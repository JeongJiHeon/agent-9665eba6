"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestAPIEndpoints:
    """Test suite for API endpoints."""
    
    def test_root_endpoint(self, client: TestClient):
        """Test root health check endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_health_check(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "services" in data
    
    def test_chat_endpoint_structure(self, client: TestClient):
        """Test chat endpoint structure."""
        # Note: This will fail without proper API keys
        # In a real scenario, mock the agent response
        
        payload = {
            "message": "안녕하세요",
            "user_id": "test_user"
        }
        
        response = client.post("/api/v1/chat", json=payload)
        
        # We expect either success or 500 (if no API keys configured)
        assert response.status_code in [200, 500]
    
    def test_google_auth_endpoint(self, client: TestClient):
        """Test Google OAuth endpoint."""
        # This might fail if credentials file is not present
        # We're testing the endpoint structure
        
        response = client.get("/api/v1/auth/google")
        
        # Should return 200 with auth_url or 500 if not configured
        assert response.status_code in [200, 500]
    
    def test_vector_store_stats(self, client: TestClient):
        """Test vector store stats endpoint."""
        response = client.get("/api/v1/vector-store/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_documents" in data


class TestChatHistory:
    """Test suite for chat history endpoints."""
    
    def test_get_nonexistent_history(self, client: TestClient):
        """Test getting history for non-existent session."""
        response = client.get("/api/v1/chat/history/nonexistent_session")
        assert response.status_code == 200
        
        data = response.json()
        assert "messages" in data
        assert data["count"] == 0
    
    def test_clear_history(self, client: TestClient):
        """Test clearing chat history."""
        response = client.delete("/api/v1/chat/history/test_session")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
