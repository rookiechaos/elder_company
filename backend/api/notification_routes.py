"""
Notification API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from dependencies import require_auth, get_notification_service_dependency
from services.notification_service import NotificationService
from middleware.rate_limit import rate_limit, RATE_LIMITS
from middleware.api_decorators import handle_api_errors
from exceptions import ValidationError, NotFoundError

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


class SendNotificationRequest(BaseModel):
    """Send notification request"""
    recipient_type: str = Field(..., description="Recipient type: caregiver, elder, family_member")
    recipient_id: str
    notification_type: str = Field(..., description="Notification type: task_reminder, schedule_reminder, emergency, etc.")
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    related_task_id: Optional[str] = None
    related_schedule_id: Optional[str] = None
    related_activity_id: Optional[str] = None
    delivery_method: str = Field("in_app", description="Delivery method: push, email, sms, in_app")


class SendFamilyNotificationRequest(BaseModel):
    """Send family member notification request"""
    elder_id: str
    notification_type: str
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    related_task_id: Optional[str] = None
    related_schedule_id: Optional[str] = None


@router.post("")
@rate_limit(limit=RATE_LIMITS.get("default", "30/minute"))
@handle_api_errors
async def send_notification(
    request: SendNotificationRequest,
    current_user: dict = Depends(require_auth),
    notification_service: NotificationService = Depends(get_notification_service_dependency)
):
    """Send notification"""
    notification = notification_service.send_notification(
        recipient_type=request.recipient_type,
        recipient_id=request.recipient_id,
        notification_type=request.notification_type,
        title=request.title,
        content=request.content,
        related_task_id=request.related_task_id,
        related_schedule_id=request.related_schedule_id,
        related_activity_id=request.related_activity_id,
        delivery_method=request.delivery_method
    )
    
    return {
        "message": "Notification sent successfully",
        "notification": notification
    }


@router.post("/family")
@rate_limit(limit=RATE_LIMITS.get("default", "20/minute"))
@handle_api_errors
async def send_family_notification(
    request: SendFamilyNotificationRequest,
    current_user: dict = Depends(require_auth),
    notification_service: NotificationService = Depends(get_notification_service_dependency)
):
    """Send notification to family members"""
    notifications = notification_service.send_family_notification(
        elder_id=request.elder_id,
        notification_type=request.notification_type,
        title=request.title,
        content=request.content,
        related_task_id=request.related_task_id,
        related_schedule_id=request.related_schedule_id,
        org_id=current_user.get("org_id")
    )
    
    return {
        "message": f"Notifications sent to {len(notifications)} family members",
        "notifications": notifications
    }


@router.get("")
@rate_limit(limit=RATE_LIMITS.get("default", "60/minute"))
@handle_api_errors
async def get_notifications(
    recipient_id: Optional[str] = Query(None, description="Recipient ID (defaults to current user)"),
    recipient_type: Optional[str] = Query(None),
    is_read: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(require_auth),
    notification_service: NotificationService = Depends(get_notification_service_dependency)
):
    """Get notification list"""
    # Default recipient ID to current user when not specified
    if not recipient_id:
        recipient_id = current_user.get("user_id")
    
    notifications = notification_service.get_notifications(
        recipient_id=recipient_id,
        recipient_type=recipient_type,
        is_read=is_read,
        limit=limit
    )
    
    return {
        "notifications": notifications,
        "count": len(notifications)
    }


@router.put("/{notification_id}/read")
@rate_limit(limit=RATE_LIMITS.get("default", "60/minute"))
@handle_api_errors
async def mark_notification_as_read(
    notification_id: str,
    current_user: dict = Depends(require_auth),
    notification_service: NotificationService = Depends(get_notification_service_dependency)
):
    """Mark notification as read"""
    success = notification_service.mark_as_read(notification_id)
    
    if not success:
        raise NotFoundError("Notification not found")
    
    return {
        "message": "Notification marked as read"
    }


@router.put("/read-all")
@rate_limit(limit=RATE_LIMITS.get("default", "20/minute"))
@handle_api_errors
async def mark_all_as_read(
    recipient_id: Optional[str] = Query(None, description="Recipient ID (defaults to current user)"),
    current_user: dict = Depends(require_auth),
    notification_service: NotificationService = Depends(get_notification_service_dependency)
):
    """Mark all notifications as read"""
    if not recipient_id:
        recipient_id = current_user.get("user_id")
    
    count = notification_service.mark_all_as_read(recipient_id)
    
    return {
        "message": f"{count} notifications marked as read"
    }
