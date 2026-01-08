import pytest
from showbay.models.task import Task, TaskCreate, TaskUpdate
from datetime import datetime


def test_task_creation():
    """Test creating a Task instance."""
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "status": "pending",
        "priority": "medium"
    }
    
    task = Task(**task_data)
    
    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.status == "pending"
    assert task.priority == "medium"


def test_task_create_schema():
    """Test TaskCreate schema validation."""
    task_create_data = {
        "title": "New Task",
        "description": "New Description",
        "status": "pending",
        "priority": "high",
        "user_id": "user123"
    }
    
    task_create = TaskCreate(**task_create_data)
    
    assert task_create.title == "New Task"
    assert task_create.priority == "high"
    assert task_create.user_id == "user123"


def test_task_update_schema():
    """Test TaskUpdate schema partial updates."""
    task_update_data = {
        "title": "Updated Task Title",
        "status": "completed"
    }
    
    task_update = TaskUpdate(**task_update_data)
    
    assert task_update.title == "Updated Task Title"
    assert task_update.status == "completed"
    assert task_update.description is None  # Optional field should be None


def test_task_validation():
    """Test validation constraints."""
    # Test title min length validation
    with pytest.raises(ValueError):
        TaskCreate(title="", description="Test", status="pending", priority="low")
    
    # Test title max length validation (over 255 characters)
    long_title = "a" * 256
    with pytest.raises(ValueError):
        TaskCreate(title=long_title, description="Test", status="pending", priority="low")