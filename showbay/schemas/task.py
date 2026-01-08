from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TaskBase(BaseModel):
    """
    Base schema for Task with common fields.
    """
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(default=None, max_length=1000, description="Task description")
    status: str = Field(default="pending", max_length=50, description="Task status")
    priority: str = Field(default="medium", max_length=20, description="Task priority: low, medium, high")


class TaskCreate(TaskBase):
    """
    Schema for creating a new task.
    """
    user_id: Optional[str] = Field(default=None, max_length=100, description="User identifier")
    external_id: Optional[int] = Field(default=None, description="ID from external API")


class TaskUpdate(BaseModel):
    """
    Schema for updating an existing task.
    """
    title: Optional[str] = Field(default=None, min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(default=None, max_length=1000, description="Task description")
    status: Optional[str] = Field(default=None, max_length=50, description="Task status")
    priority: Optional[str] = Field(default=None, max_length=20, description="Task priority: low, medium, high")
    user_id: Optional[str] = Field(default=None, max_length=100, description="User identifier")


class TaskResponse(TaskBase):
    """
    Schema for task response.
    """
    id: int
    external_id: Optional[int]
    user_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class TaskListResponse(BaseModel):
    """
    Schema for task list response.
    """
    tasks: list[TaskResponse]
    total: int
    page: int = 1
    size: int = 10