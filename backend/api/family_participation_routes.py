"""
Family Participation API Routes
"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from dependencies import require_auth, get_family_participation_service_dependency, get_family_feedback_service_dependency
from services.family_participation_service import FamilyParticipationService
from services.family_feedback_service import FamilyFeedbackService
from middleware.rate_limit import rate_limit, RATE_LIMITS
from middleware.api_decorators import handle_api_errors
from exceptions import ValidationError, NotFoundError

router = APIRouter(prefix="/api/family-participation", tags=["family-participation"])


class SubmitFeedbackRequest(BaseModel):
    """Submit feedback request"""
    family_member_id: str = Field(..., min_length=1, description="Family member ID")
    feedback_type: str = Field(..., description="Feedback type: task, schedule, activity, general")
    content: str = Field(..., min_length=1, max_length=1000, description="Feedback content")
    related_task_id: Optional[str] = Field(None, min_length=1, description="Related task ID")
    related_schedule_id: Optional[str] = Field(None, min_length=1, description="Related schedule ID")
    related_activity_id: Optional[str] = Field(None, min_length=1, description="Related activity ID")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating (1-5)")
    
    @classmethod
    def validate_feedback_type(cls, v):
        """Validate feedback type"""
        valid_types = ["task", "schedule", "activity", "general"]
        if v not in valid_types:
            raise ValueError(f"Invalid feedback_type. Must be one of: {', '.join(valid_types)}")
        return v


@router.post("/tasks/{task_id}/family/{family_member_id}")
@rate_limit(limit=RATE_LIMITS.get("default", "30/minute"))
@handle_api_errors
async def add_family_to_task(
    task_id: str,
    family_member_id: str,
    current_user: dict = Depends(require_auth),
    participation_service: FamilyParticipationService = Depends(get_family_participation_service_dependency)
):
    """Add family member to task"""
    # Input validation
    if not task_id or len(task_id.strip()) == 0:
        raise ValidationError("Task ID cannot be empty")
    if not family_member_id or len(family_member_id.strip()) == 0:
        raise ValidationError("Family member ID cannot be empty")
    
    task = participation_service.add_family_to_task(task_id, family_member_id)
    
    return {
        "message": "Family member added to task successfully",
        "task": task
    }


@router.post("/schedules/{schedule_id}/family/{family_member_id}")
@rate_limit(limit=RATE_LIMITS.get("default", "30/minute"))
@handle_api_errors
async def add_family_to_schedule(
    schedule_id: str,
    family_member_id: str,
    current_user: dict = Depends(require_auth),
    participation_service: FamilyParticipationService = Depends(get_family_participation_service_dependency)
):
    """Add family member to schedule"""
    # Input validation
    if not schedule_id or len(schedule_id.strip()) == 0:
        raise ValidationError("Schedule ID cannot be empty")
    if not family_member_id or len(family_member_id.strip()) == 0:
        raise ValidationError("Family member ID cannot be empty")
    
    schedule = participation_service.add_family_to_schedule(schedule_id, family_member_id)
    
    return {
        "message": "Family member added to schedule successfully",
        "schedule": schedule
    }


@router.get("/family/{family_member_id}/tasks")
@rate_limit(limit=RATE_LIMITS.get("default", "60/minute"))
@handle_api_errors
async def get_family_tasks(
    family_member_id: str,
    status: Optional[str] = Query(None),
    current_user: dict = Depends(require_auth),
    participation_service: FamilyParticipationService = Depends(get_family_participation_service_dependency)
):
    """Get tasks with family member participation"""
    # Validate input
    if not family_member_id or len(family_member_id.strip()) == 0:
        raise ValidationError("Family member ID cannot be empty")
    
    org_id = current_user.get("org_id")
    tasks = participation_service.get_family_tasks(family_member_id, status, org_id)
    
    return {
        "tasks": tasks,
        "count": len(tasks)
    }


@router.get("/family/{family_member_id}/schedules")
@rate_limit(limit=RATE_LIMITS.get("default", "60/minute"))
@handle_api_errors
async def get_family_schedules(
    family_member_id: str,
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    current_user: dict = Depends(require_auth),
    participation_service: FamilyParticipationService = Depends(get_family_participation_service_dependency)
):
    """Get schedules with family member participation"""
    # Validate input
    if not family_member_id or len(family_member_id.strip()) == 0:
        raise ValidationError("Family member ID cannot be empty")
    
    # Parse dates (improved error handling)
    start_dt = None
    end_dt = None
    if start_date:
        try:
            # Support multiple date formats
            date_str = start_date.replace('Z', '+00:00')
            if '+' not in date_str and '-' in date_str:
                # Assume UTC when timezone is missing
                date_str = date_str + '+00:00'
            start_dt = datetime.fromisoformat(date_str)
        except (ValueError, AttributeError) as e:
            raise ValidationError(f"Invalid start_date format. Expected ISO 8601 format (e.g., '2026-01-20T00:00:00Z' or '2026-01-20T00:00:00+00:00'). Error: {str(e)}")
    
    if end_date:
        try:
            date_str = end_date.replace('Z', '+00:00')
            if '+' not in date_str and '-' in date_str:
                date_str = date_str + '+00:00'
            end_dt = datetime.fromisoformat(date_str)
        except (ValueError, AttributeError) as e:
            raise ValidationError(f"Invalid end_date format. Expected ISO 8601 format (e.g., '2026-01-20T00:00:00Z' or '2026-01-20T00:00:00+00:00'). Error: {str(e)}")
    
    # Validate date range logic
    if start_dt and end_dt and start_dt > end_dt:
        raise ValidationError("start_date must be before or equal to end_date")
    
    org_id = current_user.get("org_id")
    schedules = participation_service.get_family_schedules(family_member_id, start_dt, end_dt, org_id)
    
    return {
        "schedules": schedules,
        "count": len(schedules)
    }


@router.post("/feedback")
@rate_limit(limit=RATE_LIMITS.get("default", "30/minute"))
@handle_api_errors
async def submit_feedback(
    request: SubmitFeedbackRequest,
    current_user: dict = Depends(require_auth),
    feedback_service: FamilyFeedbackService = Depends(get_family_feedback_service_dependency)
):
    """Submit family member feedback"""
    feedback = feedback_service.submit_feedback(
        family_member_id=request.family_member_id,
        feedback_type=request.feedback_type,
        content=request.content,
        related_task_id=request.related_task_id,
        related_schedule_id=request.related_schedule_id,
        related_activity_id=request.related_activity_id,
        rating=request.rating
    )
    
    return {
        "message": "Feedback submitted successfully",
        "feedback": feedback
    }


@router.get("/feedback")
@rate_limit(limit=RATE_LIMITS.get("default", "60/minute"))
@handle_api_errors
async def get_feedbacks(
    elder_id: Optional[str] = Query(None),
    family_member_id: Optional[str] = Query(None),
    feedback_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(require_auth),
    feedback_service: FamilyFeedbackService = Depends(get_family_feedback_service_dependency)
):
    """Get feedback list"""
    org_id = current_user.get("org_id")
    feedbacks = feedback_service.get_feedbacks(
        elder_id=elder_id,
        family_member_id=family_member_id,
        feedback_type=feedback_type,
        limit=limit,
        org_id=org_id
    )
    
    return {
        "feedbacks": feedbacks,
        "count": len(feedbacks)
    }


@router.get("/feedback/summary")
@rate_limit(limit=RATE_LIMITS.get("default", "30/minute"))
@handle_api_errors
async def get_feedback_summary(
    elder_id: str = Query(..., description="Elder ID"),
    days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(require_auth),
    feedback_service: FamilyFeedbackService = Depends(get_family_feedback_service_dependency)
):
    """Get feedback summary"""
    summary = feedback_service.get_feedback_summary(elder_id, days)
    
    return summary
