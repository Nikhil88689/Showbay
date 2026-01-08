from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List
import logging

from showbay.database.database import get_session
from showbay.models.task import Task, TaskCreate, TaskUpdate, TaskPublic
from showbay.schemas.task import TaskCreate as TaskCreateSchema, TaskUpdate as TaskUpdateSchema, TaskResponse, TaskListResponse
from showbay.utils.external_api import fetch_external_data
from showbay.utils.exceptions import ExternalAPIException

router = APIRouter(prefix="/tasks", tags=["tasks"])

# Set up logging
logger = logging.getLogger(__name__)


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreateSchema,
    session: Session = Depends(get_session)
) -> TaskResponse:
    """
    Create a new task.
    
    Args:
        task_data: Task creation data
        session: Database session
        
    Returns:
        TaskResponse: Created task data
    """
    try:
        # Create task object from schema
        db_task = Task.model_validate(task_data)
        
        # If external_id is provided, fetch external data
        if db_task.external_id:
            try:
                external_data = await fetch_external_data(db_task.external_id)
                db_task.external_api_data = str(external_data)
            except ExternalAPIException as e:
                logger.warning(f"Failed to fetch external data for task {db_task.external_id}: {e}")
        
        # Add to database
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        
        logger.info(f"Created task with ID: {db_task.id}")
        
        # Convert to response model
        return TaskResponse(
            id=db_task.id,
            title=db_task.title,
            description=db_task.description,
            status=db_task.status,
            priority=db_task.priority,
            external_id=db_task.external_id,
            user_id=db_task.user_id,
            created_at=db_task.created_at,
            updated_at=db_task.updated_at,
            completed_at=db_task.completed_at
        )
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the task"
        )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    session: Session = Depends(get_session)
) -> TaskResponse:
    """
    Get a specific task by ID.
    
    Args:
        task_id: Task identifier
        session: Database session
        
    Returns:
        TaskResponse: Task data
    """
    try:
        # Query task from database
        task = session.get(Task, task_id)
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )
        
        logger.info(f"Retrieved task with ID: {task.id}")
        
        # Convert to response model
        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            external_id=task.external_id,
            user_id=task.user_id,
            created_at=task.created_at,
            updated_at=task.updated_at,
            completed_at=task.completed_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the task"
        )


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdateSchema,
    session: Session = Depends(get_session)
) -> TaskResponse:
    """
    Update an existing task.
    
    Args:
        task_id: Task identifier
        task_data: Task update data
        session: Database session
        
    Returns:
        TaskResponse: Updated task data
    """
    try:
        # Get existing task
        db_task = session.get(Task, task_id)
        
        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )
        
        # Update task fields
        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)
        
        # Update timestamps
        db_task.updated_at = db_task.updated_at.__class__()  # Update to current time
        
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        
        logger.info(f"Updated task with ID: {db_task.id}")
        
        # Convert to response model
        return TaskResponse(
            id=db_task.id,
            title=db_task.title,
            description=db_task.description,
            status=db_task.status,
            priority=db_task.priority,
            external_id=db_task.external_id,
            user_id=db_task.user_id,
            created_at=db_task.created_at,
            updated_at=db_task.updated_at,
            completed_at=db_task.completed_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the task"
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    session: Session = Depends(get_session)
) -> None:
    """
    Delete a task by ID.
    
    Args:
        task_id: Task identifier
        session: Database session
    """
    try:
        # Get task
        db_task = session.get(Task, task_id)
        
        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )
        
        # Delete task
        session.delete(db_task)
        session.commit()
        
        logger.info(f"Deleted task with ID: {task_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the task"
        )


@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    status_filter: str = Query(None, description="Filter by status"),
    priority_filter: str = Query(None, description="Filter by priority"),
    session: Session = Depends(get_session)
) -> TaskListResponse:
    """
    List all tasks with optional filtering and pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        status_filter: Filter by status
        priority_filter: Filter by priority
        session: Database session
        
    Returns:
        TaskListResponse: Paginated list of tasks
    """
    try:
        # Build query
        query = select(Task)
        
        # Apply filters if provided
        if status_filter:
            query = query.where(Task.status == status_filter)
        if priority_filter:
            query = query.where(Task.priority == priority_filter)
        
        # Get total count
        total_query = select(Task)
        if status_filter:
            total_query = total_query.where(Task.status == status_filter)
        if priority_filter:
            total_query = total_query.where(Task.priority == priority_filter)
        
        total = len(session.exec(total_query).all())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        tasks = session.exec(query).all()
        
        # Convert to response models
        task_responses = [
            TaskResponse(
                id=task.id,
                title=task.title,
                description=task.description,
                status=task.status,
                priority=task.priority,
                external_id=task.external_id,
                user_id=task.user_id,
                created_at=task.created_at,
                updated_at=task.updated_at,
                completed_at=task.completed_at
            )
            for task in tasks
        ]
        
        logger.info(f"Retrieved {len(task_responses)} tasks")
        
        return TaskListResponse(
            tasks=task_responses,
            total=total,
            page=(skip // limit) + 1,
            size=limit
        )
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the tasks"
        )