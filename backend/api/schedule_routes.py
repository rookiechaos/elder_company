"""
Schedule Management API Routes
"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime

from dependencies import require_auth, get_schedule_service_dependency
from services.schedule_service import ScheduleService
from middleware.rate_limit import rate_limit, RATE_LIMITS
from middleware.api_decorators import handle_api_errors
from exceptions import ValidationError, NotFoundError

router = APIRouter(prefix="/api/schedules", tags=["schedules"])


class CreateScheduleRequest(BaseModel):
    """Create schedule request"""
    title: str = Field(..., min_length=1, max_length=200)
    schedule_type: str = Field(..., description="Schedule type: medication, exercise, appointment, activity")
    elder_id: str
    start_time: str  # ISO format
    end_time: Optional[str] = None  # ISO format
    recurrence: str = Field("none", description="Recurrence: daily, weekly, monthly, custom, none")
    recurrence_end_date: Optional[str] = None  # ISO format
    recurrence_pattern: Optional[Dict[str, Any]] = None
    description: Optional[str] = Field(None, max_length=1000)
    participants: Optional[List[str]] = None
    is_shared: bool = True
    shared_with: Optional[List[str]] = None
    reminders: Optional[List[Dict[str, Any]]] = None
    notes: Optional[str] = None
    location: Optional[str] = None
    related_task_id: Optional[str] = None
    
    @validator('schedule_type')
    def validate_schedule_type(cls, v):
        valid_types = ['medication', 'exercise', 'appointment', 'activity']
        if v not in valid_types:
            raise ValueError(f'Schedule type must be one of: {", ".join(valid_types)}')
        return v
    
    @validator('recurrence')
    def validate_recurrence(cls, v):
        valid_recurrences = ['daily', 'weekly', 'monthly', 'custom', 'none']
        if v not in valid_recurrences:
            raise ValueError(f'Recurrence must be one of: {", ".join(valid_recurrences)}')
        return v


class UpdateScheduleRequest(BaseModel):
    """Update schedule request"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    start_time: Optional[str] = None  # ISO format
    end_time: Optional[str] = None  # ISO format
    recurrence: Optional[str] = None
    participants: Optional[List[str]] = None
    is_shared: Optional[bool] = None
    reminders: Optional[List[Dict[str, Any]]] = None
    notes: Optional[str] = None
    location: Optional[str] = None


@router.post("")
@rate_limit(limit=RATE_LIMITS.get("default", "30/minute"))
@handle_api_errors
async def create_schedule(
    request: CreateScheduleRequest,
    current_user: dict = Depends(require_auth),
    schedule_service: ScheduleService = Depends(get_schedule_service_dependency)
):
    """Create schedule"""
    caregiver_id = current_user.get("user_id")
    
    # Parse datetime
    try:
        start_time = datetime.fromisoformat(request.start_time.replace('Z', '+00:00'))
    except Exception:
        raise ValidationError("Invalid start_time format. Use ISO format.")
    
    end_time = None
    if request.end_time:
        try:
            end_time = datetime.fromisoformat(request.end_time.replace('Z', '+00:00'))
        except Exception:
            raise ValidationError("Invalid end_time format")
    
    recurrence_end_date = None
    if request.recurrence_end_date:
        try:
            recurrence_end_date = datetime.fromisoformat(request.recurrence_end_date.replace('Z', '+00:00'))
        except Exception:
            raise ValidationError("Invalid recurrence_end_date format")
    
    schedule = schedule_service.create_schedule(
        caregiver_id=caregiver_id,
        elder_id=request.elder_id,
        title=request.title,
        schedule_type=request.schedule_type,
        start_time=start_time,
        end_time=end_time,
        recurrence=request.recurrence,
        recurrence_end_date=recurrence_end_date,
        recurrence_pattern=request.recurrence_pattern,
        description=request.description,
        participants=request.participants,
        is_shared=request.is_shared,
        shared_with=request.shared_with,
        reminders=request.reminders,
        notes=request.notes,
        location=request.location,
        org_id=current_user.get("org_id"),
        related_task_id=request.related_task_id
    )
    
    return {
        "message": "Schedule created successfully",
        "schedule": schedule
    }


@router.get("")
@rate_limit(limit=RATE_LIMITS.get("default", "60/minute"))
@handle_api_errors
async def get_schedules(
    elder_id: Optional[str] = Query(None),
    schedule_type: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: dict = Depends(require_auth),
    schedule_service: ScheduleService = Depends(get_schedule_service_dependency)
):
    """Get schedule list"""
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
    
    schedules = schedule_service.get_schedules(
        caregiver_id=caregiver_id,
        elder_id=elder_id,
        schedule_type=schedule_type,
        start_date=start_dt,
        end_date=end_dt,
        org_id=current_user.get("org_id")
    )
    
    return {
        "schedules": schedules,
        "count": len(schedules)
    }


@router.get("/calendar")
@rate_limit(limit=RATE_LIMITS.get("default", "60/minute"))
@handle_api_errors
async def get_calendar_view(
    elder_id: str = Query(..., description="Elder ID"),
    start_date: str = Query(..., description="Start date (ISO format)"),
    end_date: str = Query(..., description="End date (ISO format)"),
    current_user: dict = Depends(require_auth),
    schedule_service: ScheduleService = Depends(get_schedule_service_dependency)
):
    """Get calendar view data"""
    # Parse dates
    try:
        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    except Exception:
        raise ValidationError("Invalid date format. Use ISO format.")
    
    calendar_data = schedule_service.get_calendar_view(
        elder_id=elder_id,
        start_date=start_dt,
        end_date=end_dt,
        caregiver_id=current_user.get("user_id")
    )
    
    return calendar_data


@router.get("/{schedule_id}")
@rate_limit(limit=RATE_LIMITS.get("default", "60/minute"))
@handle_api_errors
async def get_schedule(
    schedule_id: str,
    current_user: dict = Depends(require_auth),
    schedule_service: ScheduleService = Depends(get_schedule_service_dependency)
):
    """Get a single schedule"""
    schedule = schedule_service.get_schedule(schedule_id)
    
    if not schedule:
        raise NotFoundError(f"Schedule {schedule_id} not found")
    
    return schedule


@router.put("/{schedule_id}")
@rate_limit(limit=RATE_LIMITS.get("default", "30/minute"))
@handle_api_errors
async def update_schedule(
    schedule_id: str,
    request: UpdateScheduleRequest,
    current_user: dict = Depends(require_auth),
    schedule_service: ScheduleService = Depends(get_schedule_service_dependency)
):
    """Update schedule"""
    # Parse datetime
    start_time = None
    end_time = None
    if request.start_time:
        try:
            start_time = datetime.fromisoformat(request.start_time.replace('Z', '+00:00'))
        except Exception:
            raise ValidationError("Invalid start_time format")
    if request.end_time:
        try:
            end_time = datetime.fromisoformat(request.end_time.replace('Z', '+00:00'))
        except Exception:
            raise ValidationError("Invalid end_time format")
    
    schedule = schedule_service.update_schedule(
        schedule_id=schedule_id,
        title=request.title,
        description=request.description,
        start_time=start_time,
        end_time=end_time,
        recurrence=request.recurrence,
        participants=request.participants,
        is_shared=request.is_shared,
        reminders=request.reminders,
        notes=request.notes,
        location=request.location
    )
    
    return {
        "message": "Schedule updated successfully",
        "schedule": schedule
    }


@router.delete("/{schedule_id}")
@rate_limit(limit=RATE_LIMITS.get("default", "20/minute"))
@handle_api_errors
async def delete_schedule(
    schedule_id: str,
    current_user: dict = Depends(require_auth),
    schedule_service: ScheduleService = Depends(get_schedule_service_dependency)
):
    """Delete schedule"""
    success = schedule_service.delete_schedule(schedule_id)
    
    if not success:
        raise NotFoundError(f"Schedule {schedule_id} not found")
    
    return {
        "message": "Schedule deleted successfully"
    }
