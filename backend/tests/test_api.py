"""
API endpoint tests.
"""
import pytest
from unittest.mock import patch, MagicMock


class TestAgentAPI:
    """Test agent API endpoints."""
    
    def test_chat_endpoint(self, client):
        """Test chat endpoint."""
        with patch('app.routes.agent.AgentService.process_user_message') as mock_process:
            mock_process.return_value = {
                "success": True,
                "message": "이벤트가 성공적으로 생성되었습니다."
            }
            
            response = client.post(
                "/api/v1/agent/chat",
                json={
                    "message": "내일 오후 3시에 회의 일정 추가해줘",
                    "user_id": "test_user"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "이벤트가 성공적으로 생성되었습니다" in data["message"]
    
    def test_chat_endpoint_error(self, client):
        """Test chat endpoint with error."""
        with patch('app.routes.agent.AgentService.process_user_message') as mock_process:
            mock_process.return_value = {
                "success": False,
                "message": "인증이 필요합니다.",
                "requires_auth": True
            }
            
            response = client.post(
                "/api/v1/agent/chat",
                json={
                    "message": "일정 추가해줘",
                    "user_id": "test_user"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert data["requires_auth"] is True
    
    def test_get_conversation_history(self, client):
        """Test get conversation history endpoint."""
        with patch('app.routes.agent.AgentService.get_conversation_history') as mock_history:
            mock_history.return_value = [
                {"role": "user", "content": "안녕하세요"},
                {"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요?"}
            ]
            
            response = client.get("/api/v1/agent/history/test_user")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["history"]) == 2
    
    def test_clear_conversation_history(self, client):
        """Test clear conversation history endpoint."""
        with patch('app.routes.agent.AgentService.clear_conversation_history') as mock_clear:
            mock_clear.return_value = None
            
            response = client.delete("/api/v1/agent/history/test_user")
            
            assert response.status_code == 200
            data = response.json()
            assert "삭제" in data["message"]


class TestCalendarAPI:
    """Test calendar API endpoints."""
    
    def test_create_event(self, client, mock_calendar_service):
        """Test create event endpoint."""
        with patch('app.routes.calendar.calendar_service_manager.get_service') as mock_get_service:
            mock_get_service.return_value = mock_calendar_service
            
            response = client.post(
                "/api/v1/calendar/events",
                json={
                    "user_id": "test_user",
                    "summary": "Test Meeting",
                    "start": "2024-01-15T14:00:00",
                    "end": "2024-01-15T15:00:00",
                    "description": "Test description"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "event" in data
    
    def test_list_events(self, client, mock_calendar_service):
        """Test list events endpoint."""
        with patch('app.routes.calendar.calendar_service_manager.get_service') as mock_get_service:
            mock_get_service.return_value = mock_calendar_service
            
            response = client.post(
                "/api/v1/calendar/events/list",
                json={
                    "user_id": "test_user",
                    "max_results": 10
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["events"]) > 0
    
    def test_get_auth_url(self, client):
        """Test get auth URL endpoint."""
        with patch('app.routes.calendar.calendar_service_manager.get_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.get_authorization_url.return_value = "https://accounts.google.com/o/oauth2/auth?..."
            mock_get_service.return_value = mock_service
            
            response = client.get("/api/v1/calendar/auth/url/test_user")
            
            assert response.status_code == 200
            data = response.json()
            assert "auth_url" in data
            assert data["auth_url"].startswith("https://")


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["status"] == "running"
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
