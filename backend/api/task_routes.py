"""
Task Management API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime

from dependencies import require_auth, get_task_service_dependency
from services.task_service import TaskService
from middleware.rate_limit import rate_limit, RATE_LIMITS
from middleware.api_decorators import handle_api_errors
from exceptions import ValidationError, NotFoundError

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


class CreateTaskRequest(BaseModel):
    """Create task request"""
    title: str = Field(..., min_length=1, max_length=200)
    task_type: str = Field(..., description="Task type: medication, exercise, appointment, custom")
    elder_id: str
    due_date: Optional[str] = None  # ISO format
    description: Optional[str] = Field(None, max_length=1000)
    priority: str = Field("medium", description="Priority: low, medium, high")
    family_member_ids: Optional[List[str]] = None
    reminders: Optional[List[Dict[str, Any]]] = None
    notes: Optional[str] = None
    
    @validator('task_type')
    def validate_task_type(cls, v):
        valid_types = ['medication', 'exercise', 'appointment', 'custom']
        if v not in valid_types:
            raise ValueError(f'Task type must be one of: {", ".join(valid_types)}')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        valid_priorities = ['low', 'medium', 'high']
        if v not in valid_priorities:
            raise ValueError(f'Priority must be one of: {", ".join(valid_priorities)}')
        return v


class UpdateTaskRequest(BaseModel):
    """Update task request"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    priority: Optional[str] = None
    due_date: Optional[str] = None  # ISO format
    notes: Optional[str] = None
    reminders: Optional[List[Dict[str, Any]]] = None
    
    @validator('status')
    def validate_status(cls, v):
        if v and v not in ['pending', 'in_progress', 'completed', 'cancelled']:
            raise ValueError('Status must be one of: pending, in_progress, completed, cancelled')
        return v


class CompleteTaskRequest(BaseModel):
    """Complete task request"""
    completed_by: str
    completion_notes: Optional[str] = None
    generate_summary: bool = True


@router.post("")
@rate_limit(limit=RATE_LIMITS.get("default", "30/minute"))
@handle_api_errors
async def create_task(
    request: CreateTaskRequest,
    current_user: dict = Depends(require_auth),
    task_service: TaskService = Depends(get_task_service_dependency)
):
    """Create task"""
    caregiver_id = current_user.get("user_id")
    
    # Parse due datetime
    due_date = None
    if request.due_date:
        try:
            due_date = datetime.fromisoformat(request.due_date.replace('Z', '+00:00'))
        except Exception:
            raise ValidationError("Invalid due_date format. Use ISO format.")
    
    task = task_service.create_task(
        caregiver_id=caregiver_id,
        elder_id=request.elder_id,
        title=request.title,
        task_type=request.task_type,
        due_date=due_date,
        description=request.description,
        priority=request.priority,
        family_member_ids=request.family_member_ids,
        reminders=request.reminders,
        notes=request.notes,
        org_id=current_user.get("org_id")
    )
    
    return {
        "message": "Task created successfully",
        "task": task
    }


@router.get("")
@rate_limit(limit=RATE_LIMITS.get("default", "60/minute"))
@handle_api_errors
async def get_tasks(
    elder_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    task_type: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: dict = Depends(require_auth),
    task_service: TaskService = Depends(get_task_service_dependency)
):
    """Get task list"""
    caregiver_id = current_user.get("user_id")
    
    # Parse dates
    start_dt = None
    end_dt = None
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        except Exception:
            raise ValidationError("Invalid start_date format")
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except Exception:
            raise ValidationError("Invalid end_date format")
    
    tasks = task_service.get_tasks(
        caregiver_id=caregiver_id,
        elder_id=elder_id,
        status=status,
        task_type=task_type,
        start_date=start_dt,
        end_date=end_dt,
        org_id=current_user.get("org_id")
    )
    
    return {
        "tasks": tasks,
        "count": len(tasks)
    }


@router.get("/{task_id}")
@rate_limit(limit=RATE_LIMITS.get("default", "60/minute"))
@handle_api_errors
async def get_task(
    task_id: str,
    current_user: dict = Depends(require_auth),
    task_service: TaskService = Depends(get_task_service_dependency)
):
    """Get a single task"""
    task = task_service.get_task(task_id)
    
    if not task:
        raise NotFoundError(f"Task {task_id} not found")
    
    return task


@router.put("/{task_id}")
@rate_limit(limit=RATE_LIMITS.get("default", "30/minute"))
@handle_api_errors
async def update_task(
    task_id: str,
    request: UpdateTaskRequest,
    current_user: dict = Depends(require_auth),
    task_service: TaskService = Depends(get_task_service_dependency)
):
    """Update task"""
    # Parse due datetime
    due_date = None
    if request.due_date:
        try:
            due_date = datetime.fromisoformat(request.due_date.replace('Z', '+00:00'))
        except Exception:
            raise ValidationError("Invalid due_date format")
    
    task = task_service.update_task(
        task_id=task_id,
        title=request.title,
        description=request.description,
        status=request.status,
        progress=request.progress,
        priority=request.priority,
        due_date=due_date,
        notes=request.notes,
        reminders=request.reminders
    )
    
    return {
        "message": "Task updated successfully",
        "task": task
    }


@router.post("/{task_id}/complete")
@rate_limit(limit=RATE_LIMITS.get("default", "30/minute"))
@handle_api_errors
async def complete_task(
    task_id: str,
    request: CompleteTaskRequest,
    current_user: dict = Depends(require_auth),
    task_service: TaskService = Depends(get_task_service_dependency)
):
    """Complete task"""
    task = task_service.complete_task(
        task_id=task_id,
        completed_by=request.completed_by,
        completion_notes=request.completion_notes,
        generate_summary=request.generate_summary
    )
    
    return {
        "message": "Task completed successfully",
        "task": task
    }


@router.get("/{task_id}/progress")
@rate_limit(limit=RATE_LIMITS.get("default", "60/minute"))
@handle_api_errors
async def get_task_progress(
    task_id: str,
    current_user: dict = Depends(require_auth),
    task_service: TaskService = Depends(get_task_service_dependency)
):
    """Get task progress visualization data"""
    progress = task_service.get_task_progress(task_id)
    
    return progress


@router.get("/daily/summary")
@rate_limit(limit=RATE_LIMITS.get("default", "30/minute"))
@handle_api_errors
async def get_daily_summary(
    elder_id: str = Query(..., description="Elder ID"),
    date: Optional[str] = Query(None, description="Date (ISO format, defaults to today)"),
    current_user: dict = Depends(require_auth),
    task_service: TaskService = Depends(get_task_service_dependency)
):
    """Get daily task completion summary"""
    # Parse dates
    target_date = None
    if date:
        try:
            target_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
        except Exception:
            raise ValidationError("Invalid date format")
    
    summary = task_service.get_daily_summary(
        elder_id=elder_id,
        date=target_date
    )
    
    return summary
