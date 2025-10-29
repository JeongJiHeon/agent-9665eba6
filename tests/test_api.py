"""Test API endpoints"""

import pytest
from fastapi import status


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert data["status"] == "running"


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"


def test_get_events_unauthorized(client):
    """Test getting events without authentication"""
    response = client.get("/api/v1/events/")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_events_authorized(client, auth_headers):
    """Test getting events with authentication"""
    response = client.get(
        "/api/v1/events/",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
