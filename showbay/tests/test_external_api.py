import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from showbay.main import app
from showbay.database.database import get_session
from sqlmodel import Session


@pytest.mark.asyncio
async def test_fetch_external_data_success():
    """Test successful fetching from external API."""
    from showbay.utils.external_api import fetch_external_data
    
    # Mock the httpx response
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 1,
        "title": "Test Post",
        "body": "This is a test post",
        "userId": 1
    }
    
    with patch('showbay.utils.external_api.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        result = await fetch_external_data(1)
        
        assert result["id"] == 1
        assert result["title"] == "Test Post"


@pytest.mark.asyncio
async def test_fetch_external_data_not_found():
    """Test handling of 404 from external API."""
    from showbay.utils.external_api import fetch_external_data
    from showbay.utils.exceptions import ExternalAPIException
    
    # Mock the httpx response with 404
    mock_response = AsyncMock()
    mock_response.status_code = 404
    
    with patch('showbay.utils.external_api.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        with pytest.raises(ExternalAPIException) as exc_info:
            await fetch_external_data(99999)
        
        assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_fetch_external_data_timeout():
    """Test handling of timeout from external API."""
    from showbay.utils.external_api import fetch_external_data
    from showbay.utils.exceptions import ExternalAPIException
    import httpx
    
    with patch('showbay.utils.external_api.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.TimeoutException("Request timed out")
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        with pytest.raises(ExternalAPIException) as exc_info:
            await fetch_external_data(1)
        
        assert exc_info.value.status_code == 408  # Request Timeout


def test_create_task_with_external_api_integration(client):
    """Test creating a task with external API integration."""
    # Mock the external API call
    mock_external_data = {
        "id": 1,
        "title": "External Post Title",
        "body": "External post content",
        "userId": 1
    }
    
    with patch('showbay.api.tasks.fetch_external_data', return_value=AsyncMock(return_value=mock_external_data)):
        task_data = {
            "title": "Task with External Data",
            "description": "This task will fetch external data",
            "status": "pending",
            "priority": "medium",
            "user_id": "user123",
            "external_id": 1  # This should trigger external API call
        }
        
        response = client.post("/api/v1/tasks/", json=task_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Task with External Data"
        assert data["external_id"] == 1


def test_create_task_with_external_api_failure(client):
    """Test creating a task when external API call fails."""
    from showbay.utils.exceptions import ExternalAPIException
    
    # Mock the external API call to raise an exception
    with patch('showbay.api.tasks.fetch_external_data', side_effect=ExternalAPIException("API Error", 500)):
        task_data = {
            "title": "Task with External API Failure",
            "description": "This task will fail to fetch external data",
            "status": "pending", 
            "priority": "medium",
            "user_id": "user456",
            "external_id": 999  # This should trigger external API call that fails
        }
        
        # The task should still be created even if external API fails (graceful degradation)
        response = client.post("/api/v1/tasks/", json=task_data)
        
        # Task should be created successfully despite external API failure
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Task with External API Failure"
        assert data["external_id"] == 999  # External ID should still be set