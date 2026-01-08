import pytest
from fastapi.testclient import TestClient
from showbay.main import app
from showbay.utils.exceptions import ExternalAPIException


def test_external_api_exception_handler(client):
    """Test handling of ExternalAPIException."""
    # We'll trigger this by mocking an endpoint that raises ExternalAPIException
    from unittest.mock import patch
    from showbay.api.tasks import get_task
    
    # Temporarily replace the get_task function to raise an ExternalAPIException
    original_get_task = get_task
    
    async def mock_get_task(task_id: int, session):
        raise ExternalAPIException("External API is down", status_code=502)
    
    # Patch the function temporarily
    with patch('showbay.api.tasks.get_task', mock_get_task):
        response = client.get("/api/v1/tasks/1")
        
        # Should return 502 status code
        assert response.status_code == 502
        data = response.json()
        assert "detail" in data
        assert data["error_code"] == "EXTERNAL_API_ERROR"


def test_validation_error_handler(client):
    """Test handling of validation errors."""
    # Try to create a task with invalid data (empty title)
    invalid_task_data = {
        "title": "",  # This will fail validation
        "description": "Valid description",
        "status": "pending",
        "priority": "medium",
        "user_id": "user123"
    }
    
    response = client.post("/api/v1/tasks/", json=invalid_task_data)
    
    # Should return 422 status code for validation error
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert data["error_code"] == "VALIDATION_ERROR"


def test_not_found_error(client):
    """Test handling of 404 errors."""
    response = client.get("/api/v1/tasks/999999")  # Non-existent task
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_internal_server_error(client):
    """Test handling of 500 errors."""
    # We'll trigger an internal error by patching a function to raise a generic exception
    from unittest.mock import patch
    from showbay.api.tasks import list_tasks
    
    async def mock_list_tasks(skip, limit, status_filter, priority_filter, session):
        raise Exception("Internal server error")
    
    # Patch the function temporarily
    with patch('showbay.api.tasks.list_tasks', mock_list_tasks):
        response = client.get("/api/v1/tasks/")
        
        # Should return 500 status code
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert data["error_code"] == "INTERNAL_ERROR"


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data