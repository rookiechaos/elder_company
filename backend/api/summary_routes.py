"""
Summary API Routes
"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from dependencies import require_auth, get_summary_service_dependency
from services.summary_service import SummaryService
from middleware.rate_limit import rate_limit, RATE_LIMITS
from middleware.api_decorators import handle_api_errors
from exceptions import ValidationError, NotFoundError
from utils.security import sanitize_input

router = APIRouter(prefix="/api/summary", tags=["summary"])


class LogInfoChangeRequest(BaseModel):
    """Record information change request"""
    customer_id: str = Field(..., min_length=1, description="Customer ID")
    field_name: str = Field(..., min_length=1, max_length=100, description="Field name")
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    change_type: str = Field("updated", description="Change type: created, updated, deleted")
    change_category: Optional[str] = Field(None, max_length=50, description="Change category")
    
    @classmethod
    def validate_change_type(cls, v):
        """Validate change type"""
        valid_types = ["created", "updated", "deleted"]
        if v not in valid_types:
            raise ValueError(f"Invalid change_type. Must be one of: {', '.join(valid_types)}")
        return v


@router.get("/customers/{customer_id}/summary")
@rate_limit(limit=RATE_LIMITS.get("default", "60/minute"))
@handle_api_errors
async def get_customer_summary(
    customer_id: str,
    summary_type: str = Query("full", description="Summary type: full, health, preferences, activities"),
    force_regenerate: bool = Query(False, description="Whether to force regeneration"),
    current_user: dict = Depends(require_auth),
    summary_service: SummaryService = Depends(get_summary_service_dependency)
):
    """Get customer information summary"""
    # Input validation
    if not customer_id or len(customer_id.strip()) == 0:
        raise ValidationError("Customer ID cannot be empty")
    
    valid_summary_types = ["full", "health", "preferences", "activities"]
    if summary_type not in valid_summary_types:
        raise ValidationError(f"Invalid summary_type. Must be one of: {', '.join(valid_summary_types)}")
    
    # Sanitize input
    customer_id = sanitize_input(customer_id, max_length=100)
    summary_type = sanitize_input(summary_type, max_length=50)
    
    summary = summary_service.generate_summary(
        customer_id=customer_id,
        summary_type=summary_type,
        force_regenerate=force_regenerate
    )
    
    return summary


@router.get("/customers/{customer_id}/info-cards")
@rate_limit(limit=RATE_LIMITS.get("default", "60/minute"))
@handle_api_errors
async def get_info_cards(
    customer_id: str,
    current_user: dict = Depends(require_auth),
    summary_service: SummaryService = Depends(get_summary_service_dependency)
):
    """Get information card data (for visualization)"""
    cards = summary_service.get_info_cards(customer_id)
    
    return cards


@router.get("/customers/{customer_id}/changes")
@rate_limit(limit=RATE_LIMITS.get("default", "60/minute"))
@handle_api_errors
async def get_info_changes(
    customer_id: str,
    since: Optional[str] = Query(None, description="Start time (ISO format)"),
    category: Optional[str] = Query(None, description="Change category"),
    current_user: dict = Depends(require_auth),
    summary_service: SummaryService = Depends(get_summary_service_dependency)
):
    """Get information change list"""
    # Parse datetime
    since_dt = None
    if since:
        try:
            since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
        except Exception:
            raise ValidationError("Invalid 'since' date format")
    
    changes = summary_service.get_info_changes(
        customer_id=customer_id,
        since=since_dt,
        category=category
    )
    
    return {
        "changes": changes,
        "count": len(changes)
    }


@router.post("/customers/changes/log")
@rate_limit(limit=RATE_LIMITS.get("default", "30/minute"))
@handle_api_errors
async def log_info_change(
    request: LogInfoChangeRequest,
    current_user: dict = Depends(require_auth),
    summary_service: SummaryService = Depends(get_summary_service_dependency)
):
    """Record information change"""
    # Sanitize input
    customer_id = sanitize_input(request.customer_id, max_length=100)
    field_name = sanitize_input(request.field_name, max_length=100)
    
    change = summary_service.log_info_change(
        customer_id=customer_id,
        field_name=field_name,
        old_value=request.old_value,
        new_value=request.new_value,
        change_type=request.change_type,
        changed_by=current_user.get("user_id"),
        change_category=request.change_category
    )
    
    return {
        "message": "Info change logged successfully",
        "change": change
    }
