"""
Analytics Routes - User behavior tracking
Analytics Routes - User behavior tracking
"""

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from dependencies import get_optional_user, get_analytics_service_dependency
from services.analytics_service import AnalyticsService
from middleware.api_decorators import handle_api_errors

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


class TrackEventRequest(BaseModel):
    """Track event request"""
    event_type: str  # page_view, click, action, conversion, etc.
    event_name: str  # Event name
    event_category: Optional[str] = None
    event_data: Optional[Dict[str, Any]] = None
    properties: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    page_url: Optional[str] = None


def get_client_ip(request: Request) -> str:
    """Get client IP address"""
    if request.client:
        return request.client.host
    return "unknown"


@router.post("/events")
@handle_api_errors
async def track_event(
    request: TrackEventRequest,
    http_request: Request,
    current_user: Optional[dict] = Depends(get_optional_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service_dependency)
):
    """Track a user event"""
    user_id = current_user.get("user_id") if current_user else None
    org_id = current_user.get("org_id") if current_user else None
    
    user_agent = http_request.headers.get("user-agent")
    ip_address = get_client_ip(http_request)
    referrer = http_request.headers.get("referer")
    
    result = analytics_service.track_event(
        user_id=user_id,
        org_id=org_id,
        event_type=request.event_type,
        event_name=request.event_name,
        event_category=request.event_category,
        event_data=request.event_data,
        properties=request.properties,
        session_id=request.session_id,
        page_url=request.page_url,
        referrer=referrer,
        user_agent=user_agent,
        ip_address=ip_address
    )
    
    return result


@router.get("/events/stats")
@handle_api_errors
async def get_event_stats(
    event_name: Optional[str] = Query(None, description="Filter by event name"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    days: int = Query(30, ge=1, le=365, description="Time period in days"),
    current_user: Optional[dict] = Depends(get_optional_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service_dependency)
):
    """Get event statistics"""
    user_id = current_user.get("user_id") if current_user else None
    org_id = current_user.get("org_id") if current_user else None
    
    stats = analytics_service.get_event_stats(
        event_name=event_name,
        event_type=event_type,
        user_id=user_id,
        org_id=org_id,
        days=days
    )
    
    return stats


@router.get("/retention")
@handle_api_errors
async def get_user_retention(
    days: int = Query(30, ge=1, le=365, description="Time period in days"),
    current_user: Optional[dict] = Depends(get_optional_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service_dependency)
):
    """Get user retention analysis"""
    org_id = current_user.get("org_id") if current_user else None
    
    retention = analytics_service.get_user_retention(
        org_id=org_id,
        days=days
    )
    
    return retention


@router.get("/features")
@handle_api_errors
async def get_feature_usage(
    days: int = Query(30, ge=1, le=365, description="Time period in days"),
    current_user: Optional[dict] = Depends(get_optional_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service_dependency)
):
    """Get feature usage statistics"""
    org_id = current_user.get("org_id") if current_user else None
    
    usage = analytics_service.get_feature_usage(
        org_id=org_id,
        days=days
    )
    
    return usage


@router.get("/funnel")
@handle_api_errors
async def get_conversion_funnel(
    funnel_name: str = Query(..., description="Funnel name"),
    days: int = Query(30, ge=1, le=365, description="Time period in days"),
    current_user: Optional[dict] = Depends(get_optional_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service_dependency)
):
    """Get conversion funnel analysis"""
    org_id = current_user.get("org_id") if current_user else None
    
    funnel = analytics_service.get_conversion_funnel(
        funnel_name=funnel_name,
        org_id=org_id,
        days=days
    )
    
    return funnel
