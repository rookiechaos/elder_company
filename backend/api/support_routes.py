"""
Support Routes - Support ticket system
Support Routes - Ticket system
"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session

from dependencies import get_optional_user, require_auth, get_support_service_dependency, get_permission_service_dependency
from services.support_service import SupportService
from services.permission_service import PermissionService, Permission
from middleware.api_decorators import handle_api_errors
from exceptions import NotFoundError, AuthenticationError

router = APIRouter(prefix="/api/support", tags=["support"])


class CreateTicketRequest(BaseModel):
    """Create ticket request"""
    subject: str
    description: str
    category: str  # technical, billing, feature, other
    subcategory: Optional[str] = None
    priority: str = "normal"  # low, normal, high, urgent
    attachments: Optional[List[str]] = None


class UpdateTicketRequest(BaseModel):
    """Update ticket request"""
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
    resolution: Optional[str] = None


class AddMessageRequest(BaseModel):
    """Add message request"""
    content: str
    is_internal: bool = False  # Internal notes (admin only)
    attachments: Optional[List[str]] = None


@router.post("/tickets")
@handle_api_errors
async def create_ticket(
    request: CreateTicketRequest,
    current_user: Optional[dict] = Depends(get_optional_user),
    support_service: SupportService = Depends(get_support_service_dependency)
):
    """Create a support ticket"""
    user_id = current_user.get("user_id") if current_user else None
    org_id = current_user.get("org_id") if current_user else None
    
    ticket = support_service.create_ticket(
        user_id=user_id,
        org_id=org_id,
        subject=request.subject,
        description=request.description,
        category=request.category,
        subcategory=request.subcategory,
        priority=request.priority,
        attachments=request.attachments
    )
    
    return ticket


@router.get("/tickets")
@handle_api_errors
async def list_tickets(
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(require_auth),
    support_service: SupportService = Depends(get_support_service_dependency)
):
    """Get ticket list"""
    user_id = current_user.get("user_id")
    org_id = current_user.get("org_id")
    
    # Only support staff and admins can see all tickets
    # Regular users can only see their own tickets
    assigned_to = None
    
    result = support_service.list_tickets(
        user_id=user_id,
        org_id=org_id,
        status=status,
        category=category,
        priority=priority,
        assigned_to=assigned_to,
        limit=limit,
        offset=offset
    )
    
    return result


@router.get("/tickets/{ticket_id}")
@handle_api_errors
async def get_ticket(
    ticket_id: str,
    current_user: Optional[dict] = Depends(get_optional_user),
    support_service: SupportService = Depends(get_support_service_dependency)
):
    """Get a single ticket"""
    user_id = current_user.get("user_id") if current_user else None
    
    ticket = support_service.get_ticket(ticket_id, user_id=user_id, include_messages=True)
    
    if not ticket:
        raise NotFoundError("Ticket not found")
    
    return ticket


@router.put("/tickets/{ticket_id}")
@handle_api_errors
async def update_ticket(
    ticket_id: str,
    request: UpdateTicketRequest,
    current_user: dict = Depends(require_auth),
    support_service: SupportService = Depends(get_support_service_dependency),
    permission_service: PermissionService = Depends(get_permission_service_dependency)
):
    """Update ticket (admin/support staff)"""
    user_id = current_user.get("user_id")
    
    # Require support staff or admin permission
    if not permission_service.has_permission(user_id, Permission.EDIT_TICKETS):
        raise AuthenticationError("Permission denied: ticket management access required")
    
    ticket = support_service.update_ticket(
        ticket_id=ticket_id,
        status=request.status,
        priority=request.priority,
        assigned_to=request.assigned_to,
        resolution=request.resolution,
        updated_by=user_id
    )
    
    return ticket


@router.post("/tickets/{ticket_id}/messages")
@handle_api_errors
async def add_message(
    ticket_id: str,
    request: AddMessageRequest,
    current_user: Optional[dict] = Depends(get_optional_user),
    support_service: SupportService = Depends(get_support_service_dependency),
    permission_service: PermissionService = Depends(get_permission_service_dependency)
):
    """Add ticket message"""
    user_id = current_user.get("user_id") if current_user else None
    
    # Check if user is admin or support staff
    is_admin = permission_service.has_permission(user_id, Permission.EDIT_TICKETS) if user_id else False
    
    message = support_service.add_message(
        ticket_id=ticket_id,
        user_id=user_id,
        content=request.content,
        is_admin=is_admin,
        is_internal=request.is_internal and is_admin,  # Only admins can add internal messages
        attachments=request.attachments
    )
    
    return message
