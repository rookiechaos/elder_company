"""
Monitoring Routes - System monitoring endpoints
Monitoring Routes - System monitoring endpoints
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.orm import Session

from dependencies import require_auth, get_monitoring_service_dependency, get_permission_service_dependency
from services.monitoring_service import MonitoringService
from services.permission_service import PermissionService, Permission
from middleware.api_decorators import handle_api_errors
from exceptions import AuthenticationError

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])


@router.get("/system")
@handle_api_errors
async def get_system_resources(
    current_user: dict = Depends(require_auth),
    monitoring_service: MonitoringService = Depends(get_monitoring_service_dependency),
    permission_service: PermissionService = Depends(get_permission_service_dependency)
):
    """Get system resource usage"""
    # Require monitoring permission (manager or admin)
    user_id = current_user.get("user_id")
    if user_id and not permission_service.has_permission(user_id, Permission.VIEW_MONITORING):
        raise AuthenticationError("Permission denied: monitoring access required")
    
    resources = monitoring_service.get_system_resources()
    
    return resources


@router.get("/performance")
@handle_api_errors
async def get_api_performance(
    hours: int = Query(24, ge=1, le=168, description="Time period in hours"),
    current_user: dict = Depends(require_auth),
    monitoring_service: MonitoringService = Depends(get_monitoring_service_dependency),
    permission_service: PermissionService = Depends(get_permission_service_dependency)
):
    """Get API performance metrics"""
    # Check if user has monitoring permission
    user_id = current_user.get("user_id")
    if user_id and not permission_service.has_permission(user_id, Permission.VIEW_MONITORING):
        raise AuthenticationError("Permission denied: monitoring access required")
    
    performance = monitoring_service.get_api_performance(hours=hours)
    
    return performance


@router.get("/errors")
@handle_api_errors
async def get_error_rate(
    hours: int = Query(24, ge=1, le=168, description="Time period in hours"),
    current_user: dict = Depends(require_auth),
    monitoring_service: MonitoringService = Depends(get_monitoring_service_dependency),
    permission_service: PermissionService = Depends(get_permission_service_dependency)
):
    """Get error rate statistics"""
    # Require monitoring permission
    user_id = current_user.get("user_id")
    if user_id and not permission_service.has_permission(user_id, Permission.VIEW_MONITORING):
        raise AuthenticationError("Permission denied: monitoring access required")
    
    error_rate = monitoring_service.get_error_rate(hours=hours)
    
    return error_rate


@router.get("/activity")
@handle_api_errors
async def get_user_activity(
    hours: int = Query(24, ge=1, le=168, description="Time period in hours"),
    current_user: dict = Depends(require_auth),
    monitoring_service: MonitoringService = Depends(get_monitoring_service_dependency),
    permission_service: PermissionService = Depends(get_permission_service_dependency)
):
    """Get user activity statistics"""
    # Check if user has monitoring permission
    user_id = current_user.get("user_id")
    if user_id and not permission_service.has_permission(user_id, Permission.VIEW_MONITORING):
        raise AuthenticationError("Permission denied: monitoring access required")
    
    activity = monitoring_service.get_user_activity(hours=hours)
    
    return activity


@router.get("/comprehensive")
@handle_api_errors
async def get_comprehensive_monitoring(
    current_user: dict = Depends(require_auth),
    monitoring_service: MonitoringService = Depends(get_monitoring_service_dependency),
    permission_service: PermissionService = Depends(get_permission_service_dependency)
):
    """Get aggregated monitoring data"""
    # Check if user has monitoring permission
    user_id = current_user.get("user_id")
    if user_id and not permission_service.has_permission(user_id, Permission.VIEW_MONITORING):
        raise AuthenticationError("Permission denied: monitoring access required")
    
    monitoring = monitoring_service.get_comprehensive_monitoring()
    
    return monitoring
