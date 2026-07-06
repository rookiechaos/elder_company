"""
Family Member Management API Routes
"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from dependencies import require_auth, get_family_service_dependency
from services.family_service import FamilyService
from middleware.rate_limit import rate_limit, RATE_LIMITS
from middleware.api_decorators import handle_api_errors
from exceptions import ValidationError, NotFoundError

router = APIRouter(prefix="/api/family-members", tags=["family-members"])


class AddFamilyMemberRequest(BaseModel):
    """Add family member request"""
    elder_id: str
    name: str = Field(..., min_length=1, max_length=100)
    relationship: str = Field(..., description="Relationship: son, daughter, spouse, etc.")
    phone: Optional[str] = None
    email: Optional[str] = None
    name_ja: Optional[str] = None
    name_zh: Optional[str] = None
    notification_preferences: Optional[Dict[str, bool]] = None
    can_view_tasks: bool = True
    can_view_schedules: bool = True
    can_view_emotions: bool = False
    can_view_activities: bool = True


class UpdateFamilyMemberRequest(BaseModel):
    """Update family member request"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = None
    email: Optional[str] = None
    notification_preferences: Optional[Dict[str, bool]] = None
    can_view_tasks: Optional[bool] = None
    can_view_schedules: Optional[bool] = None
    can_view_emotions: Optional[bool] = None
    can_view_activities: Optional[bool] = None
    is_active: Optional[bool] = None


@router.post("")
@rate_limit(limit=RATE_LIMITS.get("default", "30/minute"))
@handle_api_errors
async def add_family_member(
    request: AddFamilyMemberRequest,
    current_user: dict = Depends(require_auth),
    family_service: FamilyService = Depends(get_family_service_dependency)
):
    """Add family member"""
    member = family_service.add_family_member(
        elder_id=request.elder_id,
        name=request.name,
        relationship=request.relationship,
        phone=request.phone,
        email=request.email,
        name_ja=request.name_ja,
        name_zh=request.name_zh,
        notification_preferences=request.notification_preferences,
        can_view_tasks=request.can_view_tasks,
        can_view_schedules=request.can_view_schedules,
        can_view_emotions=request.can_view_emotions,
        can_view_activities=request.can_view_activities,
        org_id=current_user.get("org_id")
    )
    
    return {
        "message": "Family member added successfully",
        "member": member
    }


@router.get("")
@rate_limit(limit=RATE_LIMITS.get("default", "60/minute"))
@handle_api_errors
async def get_family_members(
    elder_id: str = Query(..., description="Elder ID"),
    is_active: Optional[bool] = Query(None),
    current_user: dict = Depends(require_auth),
    family_service: FamilyService = Depends(get_family_service_dependency)
):
    """Get family member list"""
    members = family_service.get_family_members(
        elder_id=elder_id,
        org_id=current_user.get("org_id"),
        is_active=is_active
    )
    
    return {
        "members": members,
        "count": len(members)
    }


@router.get("/{member_id}")
@rate_limit(limit=RATE_LIMITS.get("default", "60/minute"))
@handle_api_errors
async def get_family_member(
    member_id: str,
    current_user: dict = Depends(require_auth),
    family_service: FamilyService = Depends(get_family_service_dependency)
):
    """Get a single family member"""
    member = family_service.get_family_member(member_id)
    
    if not member:
        raise NotFoundError(f"Family member {member_id} not found")
    
    return member


@router.put("/{member_id}")
@rate_limit(limit=RATE_LIMITS.get("default", "30/minute"))
@handle_api_errors
async def update_family_member(
    member_id: str,
    request: UpdateFamilyMemberRequest,
    current_user: dict = Depends(require_auth),
    family_service: FamilyService = Depends(get_family_service_dependency)
):
    """Update family member information"""
    member = family_service.update_family_member(
        member_id=member_id,
        name=request.name,
        phone=request.phone,
        email=request.email,
        notification_preferences=request.notification_preferences,
        can_view_tasks=request.can_view_tasks,
        can_view_schedules=request.can_view_schedules,
        can_view_emotions=request.can_view_emotions,
        can_view_activities=request.can_view_activities,
        is_active=request.is_active
    )
    
    return {
        "message": "Family member updated successfully",
        "member": member
    }


@router.delete("/{member_id}")
@rate_limit(limit=RATE_LIMITS.get("default", "20/minute"))
@handle_api_errors
async def delete_family_member(
    member_id: str,
    current_user: dict = Depends(require_auth),
    family_service: FamilyService = Depends(get_family_service_dependency)
):
    """Delete family member"""
    success = family_service.delete_family_member(member_id)
    
    if not success:
        raise NotFoundError(f"Family member {member_id} not found")
    
    return {
        "message": "Family member deleted successfully"
    }
