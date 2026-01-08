import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from showbay.models.task import Task
from showbay.schemas.task import TaskCreate, TaskUpdate


def test_create_task(client):
    """Test creating a new task."""
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "status": "pending",
        "priority": "medium",
        "user_id": "user123"
    }
    
    response = client.post("/api/v1/tasks/", json=task_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert data["status"] == "pending"
    assert data["priority"] == "medium"
    assert data["user_id"] == "user123"
    assert "id" in data
    assert "created_at" in data


def test_get_task(client):
    """Test retrieving a specific task."""
    # First create a task
    task_data = {
        "title": "Get Test Task",
        "description": "Get Test Description",
        "status": "in_progress",
        "priority": "high",
        "user_id": "user456"
    }
    
    create_response = client.post("/api/v1/tasks/", json=task_data)
    created_task = create_response.json()
    task_id = created_task["id"]
    
    # Then retrieve it
    response = client.get(f"/api/v1/tasks/{task_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Get Test Task"
    assert data["status"] == "in_progress"


def test_get_nonexistent_task(client):
    """Test retrieving a task that doesn't exist."""
    response = client.get("/api/v1/tasks/99999")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_update_task(client):
    """Test updating an existing task."""
    # First create a task
    task_data = {
        "title": "Original Task",
        "description": "Original Description",
        "status": "pending",
        "priority": "low",
        "user_id": "user789"
    }
    
    create_response = client.post("/api/v1/tasks/", json=task_data)
    created_task = create_response.json()
    task_id = created_task["id"]
    
    # Then update it
    update_data = {
        "title": "Updated Task Title",
        "status": "completed",
        "priority": "high"
    }
    
    response = client.put(f"/api/v1/tasks/{task_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Updated Task Title"
    assert data["status"] == "completed"
    assert data["priority"] == "high"


def test_delete_task(client):
    """Test deleting a task."""
    # First create a task
    task_data = {
        "title": "Delete Test Task",
        "description": "Delete Test Description",
        "status": "pending",
        "priority": "medium",
        "user_id": "user999"
    }
    
    create_response = client.post("/api/v1/tasks/", json=task_data)
    created_task = create_response.json()
    task_id = created_task["id"]
    
    # Then delete it
    response = client.delete(f"/api/v1/tasks/{task_id}")
    
    assert response.status_code == 204
    
    # Verify the task is gone
    get_response = client.get(f"/api/v1/tasks/{task_id}")
    assert get_response.status_code == 404


def test_list_tasks(client):
    """Test listing all tasks."""
    # Create a few tasks first
    tasks_data = [
        {
            "title": "List Task 1",
            "description": "First list task",
            "status": "pending",
            "priority": "low",
            "user_id": "user111"
        },
        {
            "title": "List Task 2", 
            "description": "Second list task",
            "status": "in_progress",
            "priority": "medium",
            "user_id": "user222"
        }
    ]
    
    for task_data in tasks_data:
        client.post("/api/v1/tasks/", json=task_data)
    
    # Get the list
    response = client.get("/api/v1/tasks/")
    
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert "total" in data
    assert len(data["tasks"]) >= 2  # At least the 2 we created


def test_validation_errors(client):
    """Test validation error handling."""
    # Try to create a task with an empty title (should fail validation)
    invalid_task_data = {
        "title": "",  # Empty title should fail min_length validation
        "description": "Test Description",
        "status": "pending",
        "priority": "medium",
        "user_id": "user333"
    }
    
    response = client.post("/api/v1/tasks/", json=invalid_task_data)
    
    assert response.status_code == 422  # Unprocessable Entity
    data = response.json()
    assert "detail" in data