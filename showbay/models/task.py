from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid


class TaskBase(SQLModel):
    """
    Base model for Task with common fields.
    """
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: str = Field(default="pending", max_length=50)
    priority: str = Field(default="medium", max_length=20)  # low, medium, high
    external_api_data: Optional[str] = Field(default=None)  # JSON string from external API


class Task(TaskBase, table=True):
    """
    Task model representing a task in the database.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    external_id: Optional[int] = Field(default=None)  # ID from external API
    user_id: Optional[str] = Field(default=None, max_length=100)  # User identifier
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)
    

class TaskCreate(TaskBase):
    """
    Model for creating a new task.
    """
    user_id: Optional[str] = Field(default=None, max_length=100)


class TaskUpdate(SQLModel):
    """
    Model for updating an existing task.
    """
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: Optional[str] = Field(default=None, max_length=50)
    priority: Optional[str] = Field(default=None, max_length=20)
    external_api_data: Optional[str] = Field(default=None)


class TaskPublic(TaskBase):
    """
    Public model for task response without sensitive internal fields.
    """
    id: int
    external_id: Optional[int]
    user_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]