"""
Feedback Routes - User feedback and suggestions
Feedback Routes - User feedback and suggestions
"""

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from dependencies import get_optional_user, require_auth, get_feedback_service_dependency, get_permission_service_dependency
from services.feedback_service import FeedbackService
from services.permission_service import PermissionService, Permission
from middleware.api_decorators import handle_api_errors
from exceptions import NotFoundError, AuthenticationError

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


class CreateFeedbackRequest(BaseModel):
    """Create feedback request"""
    feedback_type: str  # suggestion, bug, question, complaint, praise
    title: str
    content: str
    category: Optional[str] = None  # feature, ui, performance, translation, other
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    attachments: Optional[List[str]] = None
    page_url: Optional[str] = None


class UpdateFeedbackStatusRequest(BaseModel):
    """Update feedback status request"""
    status: str  # pending, reviewing, resolved, rejected, closed
    resolution: Optional[str] = None
    priority: Optional[str] = None


class AddCommentRequest(BaseModel):
    """Add comment request"""
    content: str
    attachments: Optional[List[str]] = None


class SatisfactionSurveyRequest(BaseModel):
    """Satisfaction survey request"""
    survey_type: str  # onboarding, feature, general, nps
    ratings: Dict[str, int]  # {"overall": 5, "ease_of_use": 4, ...}
    comments: Optional[str] = None


def get_client_ip(request: Request) -> str:
    """Get client IP address"""
    if request.client:
        return request.client.host
    return "unknown"


@router.post("")
@handle_api_errors
async def create_feedback(
    request: CreateFeedbackRequest,
    http_request: Request,
    current_user: Optional[dict] = Depends(get_optional_user),
    feedback_service: FeedbackService = Depends(get_feedback_service_dependency)
):
    """Create feedback (anonymous supported)"""
    user_id = current_user.get("user_id") if current_user else None
    org_id = current_user.get("org_id") if current_user else None
    
    user_agent = http_request.headers.get("user-agent") if http_request else None
    ip_address = get_client_ip(http_request) if http_request else "unknown"
    
    feedback = feedback_service.create_feedback(
        user_id=user_id,
        org_id=org_id,
        feedback_type=request.feedback_type,
        title=request.title,
        content=request.content,
        category=request.category,
        contact_email=request.contact_email,
        contact_phone=request.contact_phone,
        attachments=request.attachments,
        page_url=request.page_url,
        user_agent=user_agent,
        ip_address=ip_address
    )
    
    return feedback


@router.get("")
@handle_api_errors
async def list_feedback(
    status: Optional[str] = Query(None, description="Filter by status"),
    feedback_type: Optional[str] = Query(None, description="Filter by type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Optional[dict] = Depends(get_optional_user),
    feedback_service: FeedbackService = Depends(get_feedback_service_dependency)
):
    """Get feedback list (users see only their own)"""
    user_id = current_user.get("user_id") if current_user else None
    org_id = current_user.get("org_id") if current_user else None
    
    result = feedback_service.list_feedback(
        user_id=user_id,
        org_id=org_id,
        status=status,
        feedback_type=feedback_type,
        category=category,
        limit=limit,
        offset=offset
    )
    
    return result


@router.get("/{feedback_id}")
@handle_api_errors
async def get_feedback(
    feedback_id: str,
    current_user: Optional[dict] = Depends(get_optional_user),
    feedback_service: FeedbackService = Depends(get_feedback_service_dependency)
):
    """Get a single feedback item"""
    user_id = current_user.get("user_id") if current_user else None
    
    feedback = feedback_service.get_feedback(feedback_id, user_id=user_id)
    
    if not feedback:
        raise NotFoundError("Feedback not found")
    
    return feedback


@router.put("/{feedback_id}/status")
@handle_api_errors
async def update_feedback_status(
    feedback_id: str,
    request: UpdateFeedbackStatusRequest,
    current_user: dict = Depends(require_auth),
    feedback_service: FeedbackService = Depends(get_feedback_service_dependency),
    permission_service: PermissionService = Depends(get_permission_service_dependency)
):
    """Update feedback status (admin)"""
    user_id = current_user.get("user_id")
    
    # Check if user has permission to manage feedback
    if not permission_service.has_permission(user_id, Permission.MANAGE_FEEDBACK):
        raise AuthenticationError("Permission denied: feedback management access required")
    
    feedback = feedback_service.update_feedback_status(
        feedback_id=feedback_id,
        status=request.status,
        resolution=request.resolution,
        resolved_by=user_id
    )
    
    return feedback


@router.post("/{feedback_id}/comments")
@handle_api_errors
async def add_comment(
    feedback_id: str,
    request: AddCommentRequest,
    current_user: Optional[dict] = Depends(get_optional_user),
    feedback_service: FeedbackService = Depends(get_feedback_service_dependency),
    permission_service: PermissionService = Depends(get_permission_service_dependency)
):
    """Add a comment"""
    user_id = current_user.get("user_id") if current_user else None
    
    # Check if user is admin
    is_admin = permission_service.has_permission(user_id, Permission.MANAGE_FEEDBACK) if user_id else False
    
    comment = feedback_service.add_comment(
        feedback_id=feedback_id,
        user_id=user_id,
        content=request.content,
        is_admin=is_admin,
        attachments=request.attachments
    )
    
    return comment


@router.post("/survey")
@handle_api_errors
async def submit_satisfaction_survey(
    request: SatisfactionSurveyRequest,
    current_user: Optional[dict] = Depends(get_optional_user),
    feedback_service: FeedbackService = Depends(get_feedback_service_dependency)
):
    """Submit satisfaction survey"""
    user_id = current_user.get("user_id") if current_user else None
    org_id = current_user.get("org_id") if current_user else None
    
    result = feedback_service.submit_satisfaction_survey(
        user_id=user_id,
        org_id=org_id,
        survey_type=request.survey_type,
        ratings=request.ratings,
        comments=request.comments
    )
    
    return result
